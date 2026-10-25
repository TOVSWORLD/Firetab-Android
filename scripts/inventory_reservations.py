#!/usr/bin/env python3
"""Offline cross-check of static candidate reservations against runtime banks."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def overlap(a, b):
    return max(0, min(a['start']+a['bytes'], b['start']+b['bytes'])-max(a['start'], b['start']))


def cells(value):
    values = [int(x, 16) for x in value.split()]
    if len(values) != 4 or any(not 0 <= x <= 0xffffffff for x in values):
        raise ValueError('Expected four uint32 cells')
    start, size = (values[0] << 32)+values[1], (values[2] << 32)+values[3]
    if not size or start+size > 1 << 64:
        raise ValueError('Invalid reservation extent')
    return {'start': start, 'bytes': size}


def inventory(memory, candidate):
    variants = [d for d in candidate['dtbs'] if d['facts']['version']['value'] == 'hvt']
    if len(variants) != 1:
        raise ValueError('Exactly one hvt candidate required')
    fixed, dynamic = [], []
    for name, props in variants[0]['facts']['reserved_nodes'].items():
        if 'reg' not in props:
            dynamic.append({'node': name, 'properties': props, 'address_known': False})
            continue
        reg = props['reg']
        if reg['exit_code']:
            raise ValueError('Unavailable static reservation')
        item = {'node': name, **cells(reg['value'])}
        if any(overlap(item, x) for x in fixed):
            raise ValueError('Overlapping static reservations')
        item['inside_runtime_usable_bank'] = any(overlap(item, b) == item['bytes'] for b in memory['usable_banks'])
        item['overlap_top_exclusion_bytes'] = sum(overlap(item, g) for g in memory['excluded_from_usable_dt'])
        fixed.append(item)
    return {'scope': 'Static candidate declarations versus observed runtime banks, not runtime reservation ownership',
            'candidate_dtb_sha256': variants[0]['sha256'], 'fixed_reservations': fixed,
            'dynamic_reservations': dynamic, 'fixed_bytes': sum(x['bytes'] for x in fixed),
            'fixed_overlap_top_exclusion_bytes': sum(x['overlap_top_exclusion_bytes'] for x in fixed),
            'unattributed_top_exclusion': memory['excluded_from_usable_dt'],
            'missing_runtime_evidence': ['memory/tee_reserved_mem', 'memory/lca_reserved_mem', 'chosen/atag,videolfb'],
            'reservation_ownership_verified': False, 'boot_qualified': False}


def main():
    paths = ['evidence/runtime-memory/result.json', 'evidence/stock-dtb/candidate-report.json']
    raw = [(ROOT/p).read_bytes() for p in paths]
    result = inventory(*(json.loads(x) for x in raw))
    result['input_sha256'] = {p: hashlib.sha256(x).hexdigest() for p, x in zip(paths, raw)}
    result['inventory_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
