#!/usr/bin/env python3
"""Read-only Android boot-header-v0 layout inspection; never packs or flashes."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

MAX_INPUT_BYTES = 256 * 1024 * 1024


def inspect(data, partition_bytes=None):
    if len(data) > MAX_INPUT_BYTES:
        raise ValueError('Input exceeds 256 MiB inspection limit')
    if len(data) < 1632 or data[:8] != b'ANDROID!':
        raise ValueError('Expected a complete Android boot header at offset zero; OTA/wrapper formats are unsupported')
    kernel, kernel_addr, ramdisk, ramdisk_addr, second, second_addr, tags, page, version, os_version = struct.unpack_from('<10I', data, 8)
    if version:
        raise ValueError('Only header v0 / legacy zero-dt-size layout is supported; nonzero version/dt-size is ambiguous here')
    if page < 2048 or page > 65536 or page & (page - 1):
        raise ValueError('Unsupported or invalid header page size')
    if not kernel:
        raise ValueError('Kernel component is empty')
    if partition_bytes is not None and partition_bytes <= 0:
        raise ValueError('Partition size must be positive')
    offset = page
    components = []
    for name, size, address in [('kernel', kernel, kernel_addr), ('ramdisk', ramdisk, ramdisk_addr), ('second', second, second_addr)]:
        end = offset + size
        padded_end = offset + ((size + page - 1) // page) * page
        if end > len(data) or padded_end > len(data):
            raise ValueError(f'{name} component or its page padding exceeds input')
        payload = data[offset:end]
        kind = 'not inspected'
        if name == 'kernel':
            if payload.startswith(b'\x1f\x8b'):
                kind = 'gzip signature; contents and appended DTB not validated'
            elif len(payload) >= 60 and payload[56:60] == b'ARMd':
                kind = 'ARM64 Image magic; execution/loader compatibility not validated'
            else:
                kind = 'unknown kernel payload'
        components.append({'name': name, 'offset': offset, 'bytes': size,
                           'load_address': address, 'padded_end': padded_end,
                           'sha256': hashlib.sha256(payload).hexdigest(), 'identification': kind})
        offset = padded_end
    return {'scope': 'Read-only component layout; no signature, firmware identity, load-address, DT or boot qualification',
            'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'header_layout': 'v0 or legacy zero-dt-size; indistinguishable here',
            'page_size': page, 'tags_address': tags, 'os_version_word': os_version,
            'components': components, 'unclassified_trailing_bytes': len(data) - offset,
            'partition_bytes': partition_bytes,
            'fits_supplied_partition': None if partition_bytes is None else len(data) <= partition_bytes,
            'signature_verified': False, 'bootable': 'not determined'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--partition-bytes', type=int, help='Explicit known partition size; never inferred')
    args = parser.parse_args()
    try:
        if not args.image.is_file():
            raise ValueError('Input must be a regular local file; device nodes and pipes are refused')
        with args.image.open('rb') as stream:
            data = stream.read(MAX_INPUT_BYTES + 1)
        result = inspect(data, args.partition_bytes)
    except (OSError, ValueError) as error:
        parser.exit(2, f'Inspection refused: {error}\n')
    print(json.dumps(result, indent=2))
    if result['fits_supplied_partition'] is False:
        parser.exit(2, 'Input exceeds the supplied partition size\n')


if __name__ == '__main__':
    main()
