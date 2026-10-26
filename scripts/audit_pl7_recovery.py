#!/usr/bin/env python3
"""Static exact-preloader recovery-assumption audit; never patches or executes firmware."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
from inspect_loader_layout import checked_file, preloader_layout
from trace_lk_handoff import ROOT, thumb_pc_string, thumb_call, analysis_object

EVIDENCE = ROOT/'evidence/pl7-recovery-code'


def audit(data):
    layout = preloader_layout(data)
    if layout['declared_load_base'] != 0x200d00:
        raise ValueError('Unexpected GFH declared mapping')
    manifest = json.loads((EVIDENCE/'windows.json').read_text())
    for item in manifest['windows']:
        start = item['file_offset']
        raw = bytes.fromhex(item['hex'])
        if data[start:start+len(raw)] != raw or hashlib.sha256(raw).hexdigest() != item['sha256']:
            raise ValueError('Selected preloader instruction/literal differs')
    base = layout['declared_load_base']
    usb = thumb_pc_string(data, 0x2171d8-base, 0x2171de-base)
    arb = thumb_pc_string(data, 0x201934-base, 0x20193a-base)
    failure = thumb_pc_string(data, 0x201950-base, 0x201952-base)
    if int(usb['literal_pool_offset'], 16)+base != 0x217420 or usb['text'] != '       wLength = %x\n\n':
        raise ValueError('USB reference is not the checked literal-pool word')
    if '[ANTI-ROLLBACK]' not in arb['text'] or 'Failed to read block 0' not in failure['text']:
        raise ValueError('Anti-rollback diagnostic references differ')
    call = thumb_call(*struct.unpack_from('<HH', data, 0x20a7ce-base), 0x20a7ce)
    if call != 0x201934:
        raise ValueError('Anti-rollback caller differs')
    return {'scope': 'Static GFH-declared mapping only; actual loaded mapping and physical recovery unverified',
            'mapping': layout, 'usb_literal_reference': usb, 'antirollback_log_reference': arb,
            'antirollback_failure_reference': failure, 'checked_arb_call': {'site': '0x20a7ce', 'target': hex(call),
                'condition': 'selected branch tests mutable boot-parameter byte against1'},
            'reference_site_classification': {'0x217420': 'data literal referenced by LDR at2171d8, not the descriptor instruction assumed by old reference',
                '0x21b970': 'CMP r5,0 inside selected loop/tail block; unsigned-DA verifier entry identity unverified',
                '0x201934': 'callable entry with anti-rollback log references; complete policy/compatibility unverified',
                '0x20a204': 'ADD r1,pc before logging/epilogue; TEE-loader entry identity unverified'},
            'reference_patch_set_qualified_for_current_preloader': False,
            'marker_absence_proves_exploit_patched': False,
            'missing_recovery_evidence': ['Compatible build-specific loader route; old offsets cannot be reused blindly',
                'Verified way to enter recovery and restore required state for this installed build',
                'Validated recovery artifact/provenance and non-destructive test plan',
                'Authorization for any later physical actions; none performed by this audit'],
            'no_safe_nonpersistent_load_route_established': True, 'physical_boot_or_recovery_verified': False}


def mapped_object(data):
    result = bytearray(analysis_object(data))
    section_table = struct.unpack_from('<I', result, 32)[0]
    struct.pack_into('<I', result, section_table+40+12, preloader_layout(data)['declared_load_base'])
    return bytes(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preloader', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--analysis-object', type=Path, help='Optional ignored ET_REL disassembly object, never executable')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Fresh report required')
    expected = json.loads((ROOT/'evidence/ota-loaders/inspection-result.json').read_text())['loader_images']['preloader.bin']['sha256']
    data = checked_file(args.preloader, expected)
    if args.analysis_object:
        if args.analysis_object.exists():
            parser.error('Fresh analysis object required')
        args.analysis_object.parent.mkdir(parents=True, exist_ok=True)
        args.analysis_object.write_bytes(mapped_object(data))
    result = {'preloader_sha256': expected, 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'facts': audit(data)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
