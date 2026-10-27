#!/usr/bin/env python3
"""Hash a supplied legacy MTK console ring; no acquisition, raw text or pstore decoding."""
import argparse
import hashlib
import json
import struct
from verify_offline_escrow import regular_file

MAX_BYTES = 2 * 1024 * 1024
HEADER = struct.Struct('<16I')
SIGNATURE = 0x43474244


def decode(raw):
    if type(raw) is not bytes or not HEADER.size <= len(raw) <= MAX_BYTES:
        raise ValueError('Legacy buffer must be64bytes..2MiB')
    fields = HEADER.unpack_from(raw)
    sig, total, linux, console, start, size, capacity = (
        fields[0], fields[10], fields[11], fields[12], fields[13], fields[14], fields[15])
    if sig != SIGNATURE or total != len(raw):
        raise ValueError('Legacy signature or complete-buffer length mismatch')
    if not HEADER.size <= linux < console < total or capacity != total-console:
        raise ValueError('Console offsets/capacity outside supplied buffer')
    if not 0 <= start < capacity or not start <= size <= capacity:
        raise ValueError('Ring start/length invalid; subtraction must not underflow')
    if size < capacity and start != size:
        raise ValueError('Partial ring cursor differs from its used length')
    # Mirrors chronological traversal only, never the legacy raw-buffer fallback.
    ring = raw[console:]
    chronological = ring[start:size] + ring[:start]
    if len(chronological) != size:
        raise ValueError('Ring length mismatch')
    return {'scope': 'Supplied legacy ring structure only; source/binary layout not authenticated',
        'buffer_bytes': len(raw), 'buffer_sha256': hashlib.sha256(raw).hexdigest(),
        'console_offset': console, 'console_capacity': capacity,
        'log_bytes': size, 'log_sha256': hashlib.sha256(chronological).hexdigest(),
        'ring_geometry_valid': True, 'raw_log_text_emitted': False,
        'installed_layout_verified': False, 'capture_origin_verified': False,
        'capture_freshness_verified': False, 'retention_verified': False,
        'boot_qualified': False, 'physical_test_ready': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('buffer', help='Previously supplied private regular host file')
    args = parser.parse_args()
    try:
        with regular_file(args.buffer) as stream:
            raw = stream.read(MAX_BYTES+1)
        result = decode(raw)
    except (OSError, ValueError, struct.error):
        parser.exit(2, 'Legacy console decoding refused; no input text emitted\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
