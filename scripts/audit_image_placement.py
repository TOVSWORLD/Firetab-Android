#!/usr/bin/env python3
"""Offline conditional ARM64 placement arithmetic; never selects addresses or packs firmware."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

U64 = 1 << 64
ALIGN = 2 * 1024 * 1024


def placement(address, text_offset, image_size):
    for value in (address, text_offset, image_size):
        if type(value) is not int or not 0 <= value < U64:
            raise ValueError('Expected unsigned 64-bit integer header fields')
    if not image_size:
        raise ValueError('Zero image_size has unspecified extent; cannot assess range')
    if address < text_offset or address + image_size > U64:
        raise ValueError('Address subtraction underflow or extent overflow')
    base = address - text_offset
    return {'assumed_entry_address': hex(address), 'text_offset': text_offset,
            'image_size': image_size, 'required_base': hex(base),
            'base_alignment_bytes': ALIGN, 'alignment_satisfied': base % ALIGN == 0,
            'end_exclusive': hex(address + image_size)}


def audit(runtime, boot, prefix):
    if prefix['boot_image_sha256'] != boot['sha256']:
        raise ValueError('Stock prefix and boot report hashes differ')
    raw = bytes.fromhex(prefix['gzip_decompressed_prefix_hex'])
    if len(raw) != 64 or raw[56:60] != b'ARMd':
        raise ValueError('Expected complete stock AArch64 header prefix')
    stock_offset, stock_size = struct.unpack_from('<QQ', raw, 8)
    header = runtime['arm64_header']
    new_raw = bytes.fromhex(header['first64_hex'])
    if len(new_raw) != 64 or new_raw[56:60] != b'ARMd':
        raise ValueError('Expected complete diagnostic AArch64 header prefix')
    if struct.unpack_from('<QQQ', new_raw, 8) != (header['text_offset'], header['image_size'], header['flags']):
        raise ValueError('Diagnostic decoded fields disagree with recorded header bytes')
    kernels = [x for x in boot['components'] if x['name'] == 'kernel']
    if len(kernels) != 1:
        raise ValueError('Expected exactly one stock kernel component')
    address = kernels[0]['load_address']
    return {'scope': 'Conditional report-based arithmetic; source binaries and actual loader placement not authenticated',
            'stock_boot_sha256': boot['sha256'], 'diagnostic_kernel_sha256': runtime['kernel_sha256'],
            'assumption': 'Loader uses the stock boot header kernel address as decompressed entry unchanged',
            'stock_header_at_candidate_address': placement(address, stock_offset, stock_size),
            'diagnostic_header_at_candidate_address': placement(address, header['text_offset'], header['image_size']),
            'actual_loader_placement_verified': False, 'memory_safety_qualified': False,
            'firmware_packed': False, 'douglas_boot_tested': False,
            'abi_source': 'https://docs.kernel.org/arch/arm64/booting.html'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-report', type=Path, required=True)
    parser.add_argument('--boot-report', type=Path, required=True)
    parser.add_argument('--stock-prefix-report', type=Path, required=True)
    args = parser.parse_args()
    try:
        paths = [args.runtime_report, args.boot_report, args.stock_prefix_report]
        inputs = []
        for path in paths:
            if not path.is_file() or path.stat().st_size > 1024*1024:
                raise ValueError('Reports must be regular local files at most 1 MiB')
            inputs.append(path.read_bytes())
        result = audit(*(json.loads(data) for data in inputs))
        result['input_report_sha256'] = [hashlib.sha256(data).hexdigest() for data in inputs]
        result['auditor_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    except (OSError, ValueError, KeyError, TypeError, struct.error) as error:
        parser.exit(2, f'Audit refused: {error}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
