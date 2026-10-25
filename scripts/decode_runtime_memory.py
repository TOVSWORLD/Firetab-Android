#!/usr/bin/env python3
"""Strict offline douglas ARM64 memory-handoff decoder; no device operations."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

LIMIT = 1 << 64


def regions(items):
    result = sorted(items, key=lambda x: x['start'])
    for i, item in enumerate(result):
        start, size = item['start'], item['bytes']
        if not size or start < 0 or start + size > LIMIT:
            raise ValueError('Zero size or overflowing memory extent')
        if i and result[i-1]['start'] + result[i-1]['bytes'] > start:
            raise ValueError('Overlapping memory extents')
    return result


def vendor(data, mblock=False):
    # Pinned ARM64 setup.h: u32 count, 4-byte padding, four aligned records.
    stride = 24 if mblock else 16
    if len(data) != 8 + 4*stride:
        raise ValueError('Unexpected vendor structure length')
    count = struct.unpack_from('<I', data)[0]
    if not 1 <= count <= 4:
        raise ValueError('Vendor count outside 1..4')
    result = []
    for i in range(count):
        start, size = struct.unpack_from('<QQ', data, 8+i*stride)
        item = {'start': start, 'bytes': size}
        if mblock:
            item['rank'] = struct.unpack_from('<I', data, 24+i*stride)[0]
        result.append(item)
    checked = regions(result)
    # Keep rank array order: mblock rank is an index into orig_dram_info.
    return result if not mblock else checked


def decode(report):
    records = {}
    for item in report['selected_records']:
        if item['name'] in records:
            raise ValueError('Duplicate record')
        records[item['name']] = item
    def raw(name):
        item = records[name]
        if item.get('available') is not True:
            raise ValueError('Required property unavailable')
        return bytes.fromhex(item['hex'])
    root = '/proc/device-tree/'
    if raw(root+'#address-cells') != b'\0\0\0\2' or raw(root+'#size-cells') != b'\0\0\0\2':
        raise ValueError('Expected two address and size cells')
    path = root+'memory@00000000/'
    reg = raw(path+'reg')
    if not reg or len(reg) % 16 or len(reg) > 64:
        raise ValueError('Invalid standard reg tuple length')
    usable = regions([{'start': a, 'bytes': b} for a, b in struct.iter_unpack('>QQ', reg)])
    ranks = vendor(raw(path+'orig_dram_info'))
    blocks = vendor(raw(path+'mblock_info'), True)
    for block in blocks:
        if block['rank'] >= len(ranks):
            raise ValueError('mblock rank outside physical rank array')
        rank = ranks[block['rank']]
        if not rank['start'] <= block['start'] < block['start']+block['bytes'] <= rank['start']+rank['bytes']:
            raise ValueError('mblock is outside its physical rank')
    if usable != [{'start': b['start'], 'bytes': b['bytes']} for b in blocks]:
        raise ValueError('Standard reg and vendor mblocks disagree')
    gaps = []
    for rank in regions(ranks):
        cursor = rank['start']
        for block in blocks:
            if rank['start'] <= block['start'] < rank['start']+rank['bytes']:
                if cursor < block['start']:
                    gaps.append({'start': cursor, 'bytes': block['start']-cursor})
                cursor = block['start']+block['bytes']
        end = rank['start']+rank['bytes']
        if cursor < end:
            gaps.append({'start': cursor, 'bytes': end-cursor})
    return {'scope': 'Offline memory structure consistency only; reservation ownership and physical boot unqualified',
            'physical_ranks': ranks, 'usable_banks': usable, 'mblocks': blocks,
            'physical_bytes': sum(x['bytes'] for x in ranks),
            'usable_dt_bytes': sum(x['bytes'] for x in usable), 'excluded_from_usable_dt': gaps,
            'standard_reg_matches_vendor_mblocks': True, 'boot_qualified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    try:
        if not args.report.is_file() or args.report.stat().st_size > 1024*1024:
            raise ValueError('Expected regular JSON file at most 1 MiB')
        data = args.report.read_bytes()
        result = decode(json.loads(data))
        result['input_sha256'] = hashlib.sha256(data).hexdigest()
        result['decoder_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    except (OSError, ValueError, KeyError, TypeError, struct.error) as error:
        parser.exit(2, f'Decoding refused: {error}\n')
    print(json.dumps(result, indent=2)+'\n', end='')


if __name__ == '__main__':
    main()
