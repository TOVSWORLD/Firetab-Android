#!/usr/bin/env python3
"""Bounded offline LK input-size audit; static bytes and cached boot layout only."""
import argparse
import hashlib
import json
from pathlib import Path
from inspect_loader_layout import checked_file, lk_layout
from trace_lk_handoff import ROOT

EVIDENCE = ROOT/'evidence/lk-input-length'
CAPACITY = 28*1024*1024


def selected_input_length(header_size, staging_base, matched_fdt):
    # 3de6e sets end=base+header_size; scan distance r7 grows backwards.
    # 3df90/94 align distance UP to four; 3dfa6 subtracts from saved size.
    if not 0 < header_size <= 32*1024*1024 or not 0 <= staging_base <= 0xffffffff-header_size:
        raise ValueError('Invalid bounded input interval')
    end = staging_base+header_size
    if not staging_base < matched_fdt <= end or end-matched_fdt > 0x57800:
        raise ValueError('FDT outside checked scan range')
    distance = end-matched_fdt
    rounded = (distance+3)&~3
    if rounded >= header_size:
        raise ValueError('No compressed input remains')
    return {'scan_distance_bytes': distance, 'rounded_suffix_bytes': rounded,
            'selected_inflate_input_bytes': header_size-rounded}


def audit(payload, boot_report, dt_report):
    if len(payload) != 485040:
        raise ValueError('Unexpected LK payload length')
    for item in json.loads((EVIDENCE/'windows.json').read_text()):
        raw = payload[item['start']:item['end']]
        if raw.hex() != item['hex'] or hashlib.sha256(raw).hexdigest() != item['sha256']:
            raise ValueError('Static input trace window mismatch')
    kernel = next(x for x in boot_report['components'] if x['name'] == 'kernel')
    members = dt_report['dtbs']
    prefix = 512
    if len(members) != 2 or members[0]['offset_in_kernel_component'] != prefix+dt_report['gzip_bytes']:
        raise ValueError('Unexpected stock gzip/DT layout')
    cases = []
    for member in members:
        offset = member['offset_in_kernel_component']-prefix
        model = selected_input_length(kernel['bytes'], 0x45000000, 0x45000000+offset)
        model.update({'hypothetical_matched_dt_index': member['index'],
                      'includes_complete_gzip_member': model['selected_inflate_input_bytes'] >= dt_report['gzip_bytes'],
                      'bytes_beyond_gzip_end': model['selected_inflate_input_bytes']-dt_report['gzip_bytes']})
        cases.append(model)
    actual = dt_report['gzip_uncompressed_bytes']
    return {'scope': 'Selected static paths and conditional arithmetic; not a loader emulator or tablet test',
            'staging_base': '0x45000000',
            'mtk_present_branch_read_destination': '0x44fffe00 (staging base minus512)',
            'mtk_prefix_bytes': prefix,
            'read_callback_and_security_transform_verified': False,
            'scan_initial_size_source': 'header+8 saved at3de58/3de5a; not automatically gzip-member size',
            'scan_start': 'staging base plus header size; prefix-shift can place this512 bytes beyond component payload',
            'fdt_match_cases': cases, 'actual_dt_selection_verified': False,
            'stock_gzip_bytes': dt_report['gzip_bytes'], 'stock_gzip_output_bytes': actual,
            'stock_output_capacity_bytes': CAPACITY,
            'stock_output_capacity_margin_bytes': CAPACITY-actual,
            'capacity_applies_to': 'inflate output next_out/avail_out; compressed input uses a separate length',
            'inflate_success_test': 'return1 at3f30e; output byte count replaces length via next_out minus original destination at3f316/3f31a',
            'modern_image_size_is_gzip_output_length': False,
            'modern_actual_gzip_output_bytes': None,
            'remaining_limits': ['Mutable header and all writers not exhaustively enumerated',
                                 'Indirect read and security transform1cf0c not qualified',
                                 'FDT version match, alternate branches and secure monitor not runtime verified'],
            'boot_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lk', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Fresh output directory required')
    loader = json.loads((ROOT/'evidence/ota-loaders/inspection-result.json').read_text())
    image = checked_file(args.lk, loader['loader_images']['lk.bin']['sha256'])
    boot_path = ROOT/'evidence/stock-ota-probe/boot-inspection.json'
    dt_path = ROOT/'evidence/stock-dtb/candidate-report.json'
    facts = audit(image[lk_layout(image)['payload_offset']:], json.loads(boot_path.read_text()), json.loads(dt_path.read_text()))
    report = {'lk_sha256': hashlib.sha256(image).hexdigest(), 'facts': facts,
              'inputs': [{'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in (boot_path, dt_path, EVIDENCE/'windows.json')],
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    args.output.mkdir(parents=True)
    (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(facts, indent=2))


if __name__ == '__main__':
    main()
