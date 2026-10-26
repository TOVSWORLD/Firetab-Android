#!/usr/bin/env python3
"""Read regular host files only; no collection, device protocols or restoration.
GPT layout: https://uefi.org/specs/UEFI/2.11/05_GUID_Partition_Table_Format.html
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import struct
import zlib
from contextlib import contextmanager

MAX_TABLE = 4 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


@contextmanager
def regular_file(path):
    require(stat.S_ISREG(Path(path).lstat().st_mode), 'Input must be a regular file')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        require(stat.S_ISREG(os.fstat(fd).st_mode), 'Input changed file type')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            yield stream
    finally:
        os.close(fd)


def read_exact(stream, offset, count):
    require(offset >= 0 and count >= 0, 'Negative read extent')
    stream.seek(offset)
    data = stream.read(count)
    require(len(data) == count, 'Truncated input extent')
    return data


def header(stream, lba, sector, total):
    raw = read_exact(stream, lba * sector, sector)
    require(raw[:8] == b'EFI PART', 'Missing GPT signature')
    revision, size, checksum, reserved = struct.unpack_from('<IIII', raw, 8)
    require(revision == 0x10000 and 92 <= size <= sector and reserved == 0,
            'Unsupported GPT header format')
    checked = bytearray(raw[:size]); checked[16:20] = bytes(4)
    require(zlib.crc32(checked) == checksum, 'GPT header CRC mismatch')
    current, alternate, first, last = struct.unpack_from('<QQQQ', raw, 24)
    table_lba, count, width, table_crc = struct.unpack_from('<QIII', raw, 72)
    require(current == lba and 0 < alternate < total and alternate != current,
            'GPT header location mismatch')
    require(2 < first <= last < total - 1, 'Invalid usable LBA bounds')
    require(count > 0 and width >= 128 and width & (width - 1) == 0,
            'Invalid GPT table geometry')
    length = count * width
    require(16384 <= length <= MAX_TABLE, 'GPT table size outside verifier limits')
    table_end = table_lba + (length + sector - 1) // sector
    require(1 < table_lba < table_end <= total - 1, 'GPT table outside metadata area')
    if lba == 1:
        require(table_end <= first, 'Primary GPT overlaps usable area')
    else:
        require(table_lba > last and table_end <= lba, 'Secondary GPT overlaps usable area')
    table = read_exact(stream, table_lba * sector, length)
    require(zlib.crc32(table) == table_crc, 'GPT table CRC mismatch')
    return dict(current=current, alternate=alternate, first=first, last=last,
                guid=raw[56:72], count=count, width=width, table=table)


def verify_gpt(stream, sector, expected_bytes):
    require(sector in (512, 4096), 'Unsupported logical sector size')
    require(expected_bytes % sector == 0 and expected_bytes // sector >= 8,
            'Invalid expected user-region geometry')
    require(os.fstat(stream.fileno()).st_size == expected_bytes, 'User-region length mismatch')
    total = expected_bytes // sector
    primary = header(stream, 1, sector, total)
    secondary = header(stream, total - 1, sector, total)
    require(primary['alternate'] == total - 1 and secondary['alternate'] == 1,
            'GPT headers are not reciprocal')
    for key in ('first', 'last', 'guid', 'count', 'width', 'table'):
        require(primary[key] == secondary[key], 'Primary and secondary GPT disagree')
    require(primary['guid'] != bytes(16), 'Zero disk GUID')
    regions, ids = [], set()
    for offset in range(0, len(primary['table']), primary['width']):
        entry = primary['table'][offset:offset + primary['width']]
        if entry[:16] == bytes(16):
            continue
        uid = entry[16:32]
        require(uid != bytes(16) and uid not in ids, 'Invalid or duplicate partition GUID')
        ids.add(uid)
        start, end = struct.unpack_from('<QQ', entry, 32)
        require(primary['first'] <= start <= end <= primary['last'], 'Partition outside usable region')
        regions.append((start, end))
    regions.sort()
    require(all(a[1] < b[0] for a, b in zip(regions, regions[1:])), 'Overlapping partitions')
    return {'both_headers_and_tables_valid': True, 'separate_secondary_location_checked': True,
            'used_partition_count': len(regions)}


def verify_region(path, expected_bytes, digest, gpt_sector=None):
    require(type(expected_bytes) is int and expected_bytes > 0, 'Invalid expected region length')
    require(isinstance(digest, str) and re.fullmatch('[0-9a-f]{64}', digest), 'Invalid expected SHA256')
    with regular_file(path) as stream:
        before = os.fstat(stream.fileno())
        require(before.st_size == expected_bytes, 'Region length mismatch')
        hasher = hashlib.sha256()
        while chunk := stream.read(1024 * 1024):
            hasher.update(chunk)
        require(hasher.hexdigest() == digest, 'Region SHA256 mismatch')
        result = {'length_matches': True, 'sha256_matches': True}
        if gpt_sector is not None:
            result['gpt'] = verify_gpt(stream, gpt_sector, expected_bytes)
        after = os.fstat(stream.fileno())
        require((before.st_size, before.st_mtime_ns, before.st_ctime_ns) ==
                (after.st_size, after.st_mtime_ns, after.st_ctime_ns), 'Input changed during validation')
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', help='Private JSON with user/boot1/boot2 records')
    args = parser.parse_args()
    try:
        with regular_file(args.manifest) as stream:
            data = stream.read(65537)
        require(len(data) <= 65536, 'Manifest exceeds cap')
        manifest = json.loads(data)
        require(set(manifest) == {'logical_sector_bytes', 'regions'}, 'Unexpected manifest fields')
        require(set(manifest['regions']) == {'user', 'boot1', 'boot2'}, 'All three region records required')
        results = {}
        base = Path(args.manifest).resolve().parent
        paths = set()
        identities = set()
        for name in ('user', 'boot1', 'boot2'):
            record = manifest['regions'][name]
            require(set(record) == {'file', 'expected_bytes', 'sha256'}, 'Unexpected region fields')
            path = base / record['file']
            require(path.resolve() not in paths, 'Region files must be distinct')
            paths.add(path.resolve())
            info = path.lstat()
            identity = (info.st_dev, info.st_ino)
            require(identity not in identities, 'Region files alias the same host inode')
            identities.add(identity)
            results[name] = verify_region(path, record['expected_bytes'], record['sha256'],
                manifest['logical_sector_bytes'] if name == 'user' else None)
        print(json.dumps({'offline_file_integrity_pass': True, 'regions': results,
            'collection_region_identity_verified': False, 'restore_qualified': False,
            'physical_test_ready': False}, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        # Never expose private paths/GUIDs/partition names or OS exception strings.
        print(json.dumps({'offline_file_integrity_pass': False, 'error_type': type(exc).__name__,
                          'restore_qualified': False, 'physical_test_ready': False}))
        raise SystemExit(1)


if __name__ == '__main__':
    main()
