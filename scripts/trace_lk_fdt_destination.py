#!/usr/bin/env python3
"""Static selected LK FDT address/fixup boundaries; no input execution."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
from inspect_loader_layout import checked_file, lk_layout
from trace_lk_dtb_selection import LK_SHA, wide_pc_string
from trace_lk_handoff import analysis_object, thumb_call

WINDOWS = [('header_or_fallback', 0x3ed80, 0x3edd6),
           ('wrapper', 0x3eb84, 0x3eb96), ('save_destination', 0x3de1c, 0x3de44),
           ('copy_before_open', 0x3ded8, 0x3df20),
           ('memory_write', 0x3e09c, 0x3e0c2),
           ('chosen_lookup', 0x3e0da, 0x3e100),
           ('chosen_atags', 0x3e24a, 0x3e28e),
           ('handoff_call', 0x3e732, 0x3e74a)]


def trace(payload):
    if len(payload) < 0x65b22:
        raise ValueError('Truncated selected-path payload')
    anchors = [(0x3ed80, '3368abb11d6ad3f80c80'),
               (0x3ed90, '294622463d6803464046'),
               (0x3edbc, '4ff400404ff4807122460096c4f200000195c4f20001'),
               (0x3eb84, '30b583b0069d079c00950194'), (0x3de2a, '0d46'),
               (0x3deee, '28462946aa46'),
               (0x3defc, '5a1bb2f5801f28bf4ff48012'),
               (0x3e0a8, 'daf800400146dff8282928463b4624017a440094'),
               (0x3e73c, '0a98294600220123')]
    for pc, encoded in anchors:
        if payload[pc:pc+len(bytes.fromhex(encoded))] != bytes.fromhex(encoded):
            raise ValueError('Instruction anchor mismatch at '+hex(pc))
    calls = []
    for pc, target in [(0x3eda0, 0x3eb84), (0x3edd2, 0x3eb84),
                       (0x3eb90, 0x3de1c), (0x3dee6, 0x3de04),
                       (0x3df08, 0x46cc8), (0x3e0a4, 0x4643c),
                       (0x3e0bc, 0x46930), (0x3e0e2, 0x4643c),
                       (0x3e262, 0x46930), (0x3e284, 0x46930),
                       (0x3e744, 0x3ddd0)]:
        if thumb_call(*struct.unpack_from('<HH', payload, pc), pc) != target:
            raise ValueError('Unexpected call target at '+hex(pc))
        calls.append({'offset': hex(pc), 'target': hex(target)})
    refs = [wide_pc_string(payload, a, b) for a, b in
            [(0x3e09c, 0x3e0a2), (0x3e0ae, 0x3e0b8), (0x3e0da, 0x3e0e0),
             (0x3e252, 0x3e260), (0x3e26c, 0x3e27a)]]
    if [r['text'] for r in refs] != ['/memory', 'reg', '/chosen', 'atag,boot', 'atag,mem']:
        raise ValueError('Unexpected fixup property references')
    return {'instruction_anchors': [{'offset': hex(a), 'bytes': b} for a, b in anchors],
            'calls': calls, 'references': refs,
            'header_present_destination': 'header+0x20 -> r5 -> r1 at0x3ed90 -> wrapper -> incoming r1 saved in r5 at0x3de2a',
            'header_absent_destination': 'r1 MOV.W0x100 then MOVT0x4000 ->0x40000100 -> same wrapper',
            'copy_open_order': 'rounded suffix copied to r5 before in-place open/check; open capacity MIN(global boundary-r5,0x100000)',
            'memory_fixup': '/memory reg receives stack tuple buffer, length runtime count<<4; values not proved equal to candidate reg',
            'chosen_fixups': 'selected atag,boot and atag,mem writes via0x46930; existing bootargs overwrite trace remains applicable',
            'selected_handoff': 'r1=r5 at0x3e73e before K64 wrapper; all intervening r5 lineage and secure-monitor behavior remain unproved',
            'assumptions': ['Standard ARM AAPCS callee-saved register preservation', 'Selected header-present/absent and K64 branches only'],
            'unresolved': ['Runtime header+0x20 and boundary global values', 'Pre-copy destination capacity/overlap/alignment qualification',
                           'All mutation callbacks and reservation/PSCI edits', 'Complete r5 lineage across every selected branch',
                           'Installed LK3 equivalence and actual experimental handoff/return/log retention']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lk', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    if args.output.exists():
        p.error('Fresh output directory required')
    raw = checked_file(args.lk, LK_SHA)
    payload = raw[lk_layout(raw)['payload_offset']:]
    facts = trace(payload)
    objdump = subprocess.check_output(['xcrun', '--find', 'llvm-objdump'], text=True, timeout=15).strip()
    args.output.mkdir(parents=True)
    obj = args.output/'analysis-only.o'
    obj.write_bytes(analysis_object(payload))
    excerpts = []
    for name, start, end in WINDOWS:
        r = subprocess.run([objdump, '-d', '--triple=thumbv7-none-eabi', '--print-imm-hex',
                            '--start-address='+hex(start), '--stop-address='+hex(end), str(obj)],
                           capture_output=True, text=True, check=True, timeout=15)
        if r.stderr or len(r.stdout) > 32768:
            raise ValueError('Unexpected disassembler output')
        text = r.stdout.replace(str(obj), '<analysis-only.o>')
        (args.output/(name+'.txt')).write_text(text)
        excerpts.append({'name': name, 'start': hex(start), 'end': hex(end), 'sha256': hashlib.sha256(text.encode()).hexdigest()})
    report = {'scope': 'Static exact-OTA selected paths only; firmware never executed',
              'lk_sha256': LK_SHA, 'analysis_object': 'ET_REL; no entry/program headers',
              'llvm_version': subprocess.check_output([objdump, '--version'], text=True, timeout=15).splitlines()[0],
              'facts': facts, 'excerpts': excerpts}
    (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PASS selected destination/call/string anchors; runtime gates remain open')


if __name__ == '__main__':
    main()
