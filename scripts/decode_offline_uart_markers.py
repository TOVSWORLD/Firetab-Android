#!/usr/bin/env python3
"""Summarize supplied fixed-marker bytes; never acquire or echo serial data."""
import argparse
import hashlib
import json
from verify_offline_escrow import regular_file

MAX_BYTES = 1024 * 1024
MARKERS = {b'FTD1 ENTRY': 'entry', b'FTD1 RETURN': 'return', b'FTD1 ERROR': 'error'}


def decode_markers(raw):
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise ValueError('Transcript must be bytes within 1 MiB')
    sequence = []
    malformed = 0
    lines = raw.split(b'\n')
    for index, line in enumerate(lines):
        # Accept LF and CRLF, but never treat a truncated final line as complete.
        complete = index < len(lines) - 1
        if line.endswith(b'\r'):
            line = line[:-1]
        if line in MARKERS and complete:
            sequence.append(MARKERS[line])
        elif b'FTD1' in line:
            malformed += 1
    valid = malformed == 0 and sequence in (['entry', 'return'], ['entry', 'error'])
    return {
        'transcript_bytes': len(raw),
        'transcript_sha256': hashlib.sha256(raw).hexdigest(),
        'complete_marker_counts': {name: sequence.count(name) for name in MARKERS.values()},
        'malformed_marker_lines': malformed,
        'single_marker_pair_valid': valid,
        'reported_outcome': sequence[-1] if valid else 'unqualified',
        'capture_origin_verified': False,
        'capture_freshness_verified': False,
        'agent_execution_verified': False,
        'stock_restore_verified': False,
        'physical_test_ready': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('transcript')
    args = parser.parse_args()
    with regular_file(args.transcript) as stream:
        raw = stream.read(MAX_BYTES + 1)
    print(json.dumps(decode_markers(raw), indent=2))


if __name__ == '__main__':
    main()
