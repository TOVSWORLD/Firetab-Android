#!/usr/bin/env python3
"""Inspect supplied recovery ZIPs offline; never extract, import or execute contents."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import zipfile

CAP = 31 * 1024 * 1024
ENTRY_CAP = 1024 * 1024
SELECTED_CAP = 4 * 1024 * 1024
PACKAGES = ('amonet-douglas-v1.2.zip', 'brick-douglas.zip',
            'amonet-douglas-return-to-stock.zip')
SELECTED = frozenset(('amonet/bin/preloader.bin', 'amonet/bin/lk.bin',
    'amonet/step-1.sh', 'amonet/step-2.sh', 'amonet/fastboot-step.sh',
    'amonet/brick-9820.sh', 'amonet/bootrom-step.sh',
    'amonet/bootrom-step-minimal.sh', 'amonet/return-to-stock.sh',
    'amonet/functions.inc', 'amonet/modules/main.py', 'amonet/modules/gpt.py'))


def inspect(paths, mirror_hashes=None):
    """Hashes compare bytes only; filenames and local custody cannot prove origin."""
    if len(paths) != 3:
        raise ValueError('Exactly three explicit package paths required')
    blobs = []
    total = 0
    for path in paths:
        # Open once without following the final symlink; bound actual reads too.
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= CAP-total:
                raise ValueError('Regular ZIP files within combined31MiB cap required')
            data = stream.read(CAP-total+1)
            if len(data) != info.st_size or len(data) > CAP-total:
                raise ValueError('Package size changed or budget exceeded')
            total += len(data)
            blobs.append(data)
    packages = []
    selected_bytes = 0
    for role, data in zip(PACKAGES, blobs):
        files = []
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            entries = archive.infolist()
            if len(entries) > 500:
                raise ValueError('ZIP entry count exceeds500')
            seen = set()
            for entry in entries:
                name = entry.filename
                parts = PurePosixPath(name).parts
                if (not name or '\\' in name or name.startswith('/') or
                        '..' in parts or name in seen):
                    raise ValueError('Ambiguous or unsafe ZIP path')
                seen.add(name)
                mode = entry.external_attr >> 16
                if stat.S_ISLNK(mode) or entry.flag_bits & 1:
                    raise ValueError('Symlink/encrypted ZIP entry rejected')
                # Accept a single enclosing release directory, never arbitrary suffixes.
                canonical = name if name in SELECTED else '/'.join(parts[1:])
                if canonical not in SELECTED:
                    continue
                if any(x['name'] == canonical for x in files):
                    raise ValueError('Duplicate canonical selected entry')
                if (not 0 < entry.file_size <= ENTRY_CAP or
                        selected_bytes + entry.file_size > SELECTED_CAP):
                    raise ValueError('Selected-content budget exceeded')
                with archive.open(entry) as stream:
                    content = stream.read(ENTRY_CAP+1)
                if len(content) != entry.file_size:
                    raise ValueError('Selected entry length differs')
                selected_bytes += len(content)
                digest = hashlib.sha256(content).hexdigest()
                expected = (mirror_hashes or {}).get(canonical)
                files.append({'name': canonical, 'bytes': len(content), 'sha256': digest,
                    'mirror_comparison': ('not_available' if expected is None else
                        'equal' if digest == expected else 'different')})
        packages.append({'supplied_role': role, 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest(), 'entry_count': len(entries),
            'selected_files': files,
            'selected_names_absent': sorted(SELECTED - {x['name'] for x in files})})
    return {'scope': 'Supplied local bytes only; roles do not authenticate package origin',
        'combined_bytes': total, 'combined_cap': CAP, 'selected_bytes': selected_bytes,
        'packages': packages, 'source_provenance_verified': False,
        'original_author_archive_match_verified': False,
        'restore_qualified': False, 'physical_test_ready': False,
        'archive_contents_executed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packages', nargs=3, type=Path, metavar='ZIP',
                        help='v1.2, brick, return-to-stock, in that order')
    parser.add_argument('--mirror-receipt', type=Path,
                        help='Optional own cached extraction receipt for byte comparisons')
    args = parser.parse_args()
    hashes = {}
    if args.mirror_receipt:
        if args.mirror_receipt.stat().st_size > 1024*1024:
            parser.error('Receipt exceeds1MiB')
        receipt = json.loads(args.mirror_receipt.read_text())
        hashes = {x['name']: x['sha256'] for x in receipt['files']}
    print(json.dumps(inspect(args.packages, hashes), indent=2))


if __name__ == '__main__':
    main()
