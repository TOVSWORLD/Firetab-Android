#!/usr/bin/env python3
"""Measure raw Image/gzip bytes separately from ARM64 runtime memory footprint."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib

MAX_IMAGE = 64*1024*1024
LK_CAPACITY = 28*1024*1024


def measure(image, packed):
    if not 64 <= len(image) <= MAX_IMAGE or image[56:60] != b'ARMd':
        raise ValueError('Expected bounded complete raw ARM64 Image')
    offset, footprint, flags = struct.unpack_from('<QQQ', image, 8)
    if not len(image) <= footprint <= 1024*1024*1024 or flags >> 4:
        raise ValueError('Unsupported/truncated Image memory footprint or flags')
    if not 18 <= len(packed) <= MAX_IMAGE+65536 or packed[:4] != b'\x1f\x8b\x08\x00' or packed[4:8] != bytes(4):
        raise ValueError('Expected bounded gzip -n member with zero timestamp and no optional header')
    decoder = zlib.decompressobj(31)
    decoded = decoder.decompress(packed, len(image)+1)
    if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail or decoded != image:
        raise ValueError('gzip must contain exactly this Image in one complete member')
    return {'scope': 'File lengths/header memory requirement only; no board placement or boot qualification',
            'image_bytes': len(image), 'image_sha256': hashlib.sha256(image).hexdigest(),
            'gzip_bytes': len(packed), 'gzip_sha256': hashlib.sha256(packed).hexdigest(),
            'gzip_header_hex': packed[:10].hex(), 'gzip_round_trip_verified': True,
            'text_offset': offset, 'image_size': footprint, 'flags': flags,
            'declared_runtime_bytes_beyond_file': footprint-len(image),
            'lk_checked_output_capacity_bytes': LK_CAPACITY,
            'decoded_file_fits_lk_capacity': len(image) <= LK_CAPACITY,
            'lk_output_capacity_margin_bytes': LK_CAPACITY-len(image),
            'appended_dt_bytes': None, 'placement_base_alignment_bytes': 2*1024*1024,
            'physical_destination_selected': False, 'boot_verified': False}


def bounded_file(path, maximum):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > maximum:
        raise ValueError('Bounded regular input file required')
    return path.read_bytes()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--gzip', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Fresh output file required')
    facts = measure(bounded_file(args.image, MAX_IMAGE), bounded_file(args.gzip, MAX_IMAGE+65536))
    facts['script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(facts, indent=2)+'\n')
    print(json.dumps(facts, indent=2))


if __name__ == '__main__':
    main()
