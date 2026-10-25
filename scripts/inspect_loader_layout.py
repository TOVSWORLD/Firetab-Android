#!/usr/bin/env python3
"""Strict static loader-container audit; never executes, modifies or repacks firmware."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from audit_image_placement import placement
ROOT = Path(__file__).resolve().parents[1]
CAP = 1024*1024


def preloader_layout(data):
    if len(data) < 56:
        raise ValueError('Truncated GFH FILE_INFO')
    magic, size, kind = struct.unpack_from('<IHH', data)
    if magic != 0x014d4d4d or kind != 0 or size < 56 or data[8:20].rstrip(b'\0') != b'FILE_INFO':
        raise ValueError('Expected GFH v1 FILE_INFO at offset zero')
    address, length, maximum, content, signature = struct.unpack_from('<5I', data, 28)
    if length != len(data) or maximum < length or not size <= content < length:
        raise ValueError('Inconsistent GFH container bounds')
    end = length-signature
    if not content < end <= length or address+end > 1 << 32:
        raise ValueError('Invalid GFH code/signature bounds')
    return {'format': 'GFH v1 FILE_INFO', 'declared_load_base': address,
            'payload_offset': content, 'payload_bytes': end-content,
            'declared_code_start': address+content, 'declared_code_end_exclusive': address+end,
            'signature_region_bytes': signature, 'maximum_file_bytes': maximum,
            'signature_verified': False}


def lk_layout(data):
    if len(data) < 512:
        raise ValueError('Truncated LK MTK prefix')
    magic, size = struct.unpack_from('<II', data)
    if magic != 0x58881688 or size != len(data)-512 or data[8:40].rstrip(b'\0') != b'LK':
        raise ValueError('Expected exact LK MTK prefix and payload extent')
    address, mode = struct.unpack_from('<II', data, 40)
    return {'format': 'MTK 512-byte LK prefix', 'payload_offset': 512, 'payload_bytes': size,
            'declared_address_word': address, 'mode_word': mode,
            'uses_preloader_default_address': address == 0xffffffff,
            'actual_load_base_verified': False, 'signature_verified': False}


def address_window(data, layout, address, base):
    if type(address) is not int or type(base) is not int or not 0 <= base <= address < 1 << 32:
        raise ValueError('Invalid code address/base')
    relative = address-base
    if relative+16 > layout['payload_bytes']:
        raise ValueError('Address outside bounded payload window')
    offset = layout['payload_offset']+relative
    raw = data[offset:offset+16]
    return {'address': hex(address), 'assumed_or_declared_code_base': hex(base),
            'file_offset': offset, 'bytes_hex': raw.hex(), 'sha256': hashlib.sha256(raw).hexdigest(),
            'function_identity_verified': False, 'patch_compatibility_verified': False}


def checked_file(path, expected):
    if not path.is_file() or not 8 <= path.stat().st_size <= CAP:
        raise ValueError('Expected regular local loader file at most 1 MiB')
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('Loader hash mismatch')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preloader', type=Path, required=True)
    parser.add_argument('--lk', type=Path, required=True)
    args = parser.parse_args()
    expected = json.loads((ROOT/'evidence/ota-loaders/inspection-result.json').read_text())['loader_images']
    preloader = checked_file(args.preloader, expected['preloader.bin']['sha256'])
    lk = checked_file(args.lk, expected['lk.bin']['sha256'])
    pre, boot = preloader_layout(preloader), lk_layout(lk)
    # Addresses are pinned source claims, never permissions to apply patches.
    pre_windows = [address_window(preloader, pre, a, pre['declared_code_start'])
                   for a in [0x0021b970, 0x00217420, 0x00201934, 0x0020a204]]
    lk_windows = [address_window(lk, boot, a, 0x4bd00000)
                  for a in [0x4bd205ec, 0x4bd2080c, 0x4bd3fd1e]]
    header = json.loads((ROOT/'evidence/qemu-diagnostic/generic-runtime-result.json').read_text())['arm64_header']
    result = {'scope': 'Static container and hypothetical address mapping only; no instruction-flow or boot qualification',
              'preloader_sha256': expected['preloader.bin']['sha256'], 'lk_sha256': expected['lk.bin']['sha256'],
              'preloader': pre, 'lk': boot, 'newer_fork_patch_address_windows': pre_windows,
              'legacy_lk_patch_address_windows_assuming_source_base': lk_windows,
              'modern_image_at_stock_header_entry': placement(0x40080000, header['text_offset'], header['image_size']),
              'legacy_helper_bundled_loader_binaries_present_in_pinned_git': False,
              'loader_branch_behavior_verified': False, 'boot_qualified': False,
              'inspector_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
