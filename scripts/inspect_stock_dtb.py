#!/usr/bin/env python3
"""Bounded local candidate kernel/DT inspection; no downloads or device access."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import zlib

from inspect_boot_image import inspect, MAX_INPUT_BYTES


def split_kernel(kernel, maximum=64*1024*1024):
    if len(kernel) < 512 or struct.unpack_from('<I', kernel)[0] != 0x58881688:
        raise ValueError('Expected observed 512-byte kernel prefix')
    if struct.unpack_from('<I', kernel, 4)[0] != len(kernel)-512 or kernel[8:40].split(b'\0')[0] != b'KERNEL':
        raise ValueError('Kernel prefix name/size mismatch')
    payload = kernel[512:]
    decoder, position, total = zlib.decompressobj(31), 0, 0
    digest, prefix = hashlib.sha256(), b''
    while not decoder.eof and position < len(payload):
        block = payload[position:position+65536]
        position += len(block)
        while block:
            data = decoder.decompress(block, min(65536, maximum-total+1))
            total += len(data)
            if total > maximum:
                raise ValueError('Decompression budget exceeded')
            digest.update(data)
            prefix = (prefix + data[:64])[:64]
            remaining = decoder.unconsumed_tail
            if decoder.eof:
                break
            if remaining == block and not data:
                raise ValueError('DEFLATE made no progress')
            block = remaining
    if not decoder.eof:
        raise ValueError('Truncated gzip member')
    consumed = position-len(decoder.unused_data)
    suffix, offset, blobs, descriptors = payload[consumed:], 0, [], []
    while offset < len(suffix):
        if len(blobs) >= 32 or len(suffix)-offset < 40:
            raise ValueError('Too many DTBs or truncated suffix')
        header = struct.unpack_from('>10I', suffix, offset)
        magic, size, structure, strings, reserve, version, compatible, _, strings_size, structure_size = header
        if (magic != 0xd00dfeed or not 40 <= size <= 2*1024*1024 or offset+size > len(suffix) or
                version != 17 or compatible > 17 or reserve < 40 or reserve+16 > size or
                structure < 40 or structure+structure_size > size or strings < 40 or strings+strings_size > size):
            raise ValueError('Unsupported/invalid appended DTB header or suffix')
        blob = suffix[offset:offset+size]
        reservations, cursor = [], reserve
        while cursor+16 <= size:
            address, length = struct.unpack_from('>QQ', blob, cursor)
            cursor += 16
            if not address and not length:
                break
            reservations.append({'address': hex(address), 'bytes': length})
        else:
            raise ValueError('Unterminated FDT reservation map')
        descriptors.append({'index': len(blobs), 'offset_in_kernel_component': 512+consumed+offset,
                            'bytes': size, 'sha256': hashlib.sha256(blob).hexdigest(),
                            'header_reservations': reservations})
        blobs.append(blob)
        offset += size
    if not blobs:
        raise ValueError('No appended DTBs')
    return {'scope': 'Static file layout, not signature/loader/runtime qualification',
            'gzip_bytes': consumed, 'gzip_uncompressed_bytes': total,
            'gzip_uncompressed_sha256': digest.hexdigest(),
            'arm64_magic': prefix[56:60] == b'ARMd',
            'decompression_budget': maximum, 'dtbs': descriptors}, blobs


def facts(fdtget, file):
    queries = 0
    def query(option, node, prop=None):
        nonlocal queries
        queries += 1
        if queries > 128:
            raise ValueError('DT property-query budget exceeded')
        command = [str(fdtget), option, str(file), node] + ([prop] if prop else [])
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        return {'exit_code': result.returncode, 'value': result.stdout.strip()}
    result = {key: query('-ts', '/', key) for key in ['model', 'compatible', 'version']}
    for key in ['#address-cells', '#size-cells']:
        result[key] = query('-tx', '/', key)
    result['memory_nodes'] = {}
    children = query('-l', '/')
    if children['exit_code']:
        raise ValueError('fdtget rejected extracted tree')
    for child in children['value'].splitlines():
        if child == 'memory' or child.startswith('memory@'):
            result['memory_nodes']['/'+child] = query('-tx', '/'+child, 'reg')
    result['psci'] = {'compatible': query('-ts', '/psci', 'compatible'), 'method': query('-ts', '/psci', 'method')}
    for key in ['cpu_suspend', 'cpu_off', 'cpu_on', 'affinity_info']:
        result['psci'][key] = query('-tx', '/psci', key)
    result['cpu0_enable_method'] = query('-ts', '/cpus/cpu@0', 'enable-method')
    result['reserved_nodes'] = {}
    for child in query('-l', '/reserved-memory')['value'].splitlines():
        node = '/reserved-memory/'+child
        properties = query('-p', node)['value'].splitlines()
        result['reserved_nodes'][node] = {key: query('-tx', node, key) for key in properties
                                         if key in ['reg', 'size', 'alignment', 'alloc-ranges', 'no-map']}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--fdtget', type=Path, default=Path(__file__).resolve().parents[1]/'work/dtb-tool/build/fdtget')
    args = parser.parse_args()
    if args.output.exists() or not args.image.is_file():
        parser.error('Fresh output directory and regular local input required')
    with args.image.open('rb') as handle:
        data = handle.read(MAX_INPUT_BYTES+1)
    digest = hashlib.sha256(data).hexdigest()
    if digest != args.expected_sha256:
        parser.error('Input checksum differs from selected candidate')
    boot = inspect(data)
    component = next(x for x in boot['components'] if x['name'] == 'kernel')
    report, blobs = split_kernel(data[component['offset']:component['offset']+component['bytes']])
    args.output.mkdir(parents=True)
    for descriptor, blob in zip(report['dtbs'], blobs):
        file = args.output/f"dtb-{descriptor['index']}.dtb"
        file.write_bytes(blob)
        descriptor['facts'] = facts(args.fdtget, file)
    report.update(boot_image_sha256=digest, fdtget_version=subprocess.check_output([str(args.fdtget), '--version'], text=True).strip(),
                  inspector_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  installed_build_matched=False, signature_verified=False, hardware_tested=False)
    (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
