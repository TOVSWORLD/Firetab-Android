#!/usr/bin/env python3
"""Exact-build, static LK header/entry/decompression trace; never executes firmware."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
from inspect_loader_layout import checked_file, lk_layout
from trace_lk_handoff import ROOT, analysis_object, thumb_call, thumb_pc_string

EVIDENCE = ROOT/'evidence/lk-header-producer'


def trace(payload):
    if len(payload) != 485040:
        raise ValueError('Unexpected payload length')
    for item in json.loads((EVIDENCE/'anchors.json').read_text())['ranges']:
        raw = bytes.fromhex(item['hex'])
        if payload[item['offset']:item['offset']+len(raw)] != raw:
            raise ValueError(f"Static anchor differs at {item['offset']:x}")
    def word(offset): return struct.unpack_from('<I', payload, offset)[0]
    bases = [(word(pool)+add+4)&0xffffffff for pool, add in
             [(0x24958, 0x2477e), (0x3ef54, 0x3ebb0), (0x3e994, 0x3de30)]]
    if len(set(bases)) != 1 or bases[0] != 0x761f4:
        raise ValueError('Header global tables do not join')
    indices = [word(at) for at in (0x2495c, 0x3ef78, 0x3e998)]
    if indices != [0x248]*3 or word(bases[0]+indices[0]) != 0x4bd841b0:
        raise ValueError('Header global slot differs')
    calls = []
    for at, expected in [(0x247ee, 0x45d8c), (0x3eda0, 0x3eb84),
                         (0x3e11c, 0x3f3f0), (0x3f3fe, 0x3f364),
                         (0x3f3aa, 0x3f2b4), (0x3f30a, 0x48ad8)]:
        target = thumb_call(*struct.unpack_from('<HH', payload, at), at)
        if target != expected:
            raise ValueError('Selected call differs')
        calls.append({'offset': hex(at), 'target': hex(target)})
    return {'shared_got_payload_offset': hex(bases[0]), 'header_pointer_global_linked_address': '0x4bd841b0',
            'header_pointer_value_available_in_file': False,
            'header_magic_reference': thumb_pc_string(payload, 0x247e6, 0x247ec),
            'kernel_address_label_reference': thumb_pc_string(payload, 0x2482c, 0x24832),
            'checked_calls': calls,
            'header_present_entry_path': 'header +0xc -> r8 -> r0 at 0x3ed98 -> 0x3eb84 -> saved entry slot -> selected K64 SMC',
            'decompression_destination_path': 'global header pointer -> +0xc -> r1 at 0x3e11a -> adapter r2 -> inflate next_out',
            'k64_header_address_alignment_bytes': 524288,
            'k64_alignment_failure': '0x3e132 logs then loops at 0x3e146; rejects rather than rounds address',
            'decompression_output_capacity_bytes': 29360128,
            'staging_address_returned_by_0x2578c': '0x45000000',
            'checked_entry_and_output_path_rounds_address': False,
            'assumptions': ['Standard ARM AAPCS callee-saved register preservation',
                            'Checked header-present and nonzero K64 branches selected',
                            'No intervening untraced code mutates header/global values'],
            'unresolved': ['Indirect storage callback and complete header validation/error propagation',
                           'All writes to header/global and alternative boot paths',
                           'Complete staging/decompression input length and appended DT handling',
                           'Secure monitor final transfer, physical placement and recovery'],
            'whole_loader_compatibility_verified': False, 'runtime_boot_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lk', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Fresh output directory required')
    expected = json.loads((ROOT/'evidence/ota-loaders/inspection-result.json').read_text())['loader_images']['lk.bin']['sha256']
    image = checked_file(args.lk, expected)
    payload = image[lk_layout(image)['payload_offset']:]
    facts = trace(payload)
    objdump = shutil.which('llvm-objdump') or subprocess.check_output(['xcrun', '--find', 'llvm-objdump'], text=True, timeout=15).strip()
    version = subprocess.check_output([objdump, '--version'], text=True, timeout=15).splitlines()[0]
    args.output.mkdir(parents=True)
    obj = args.output/'analysis-only.o'
    obj.write_bytes(analysis_object(payload))
    excerpts = []
    for item in json.loads((EVIDENCE/'windows.json').read_text()):
        start, end = item['start'], item['end']
        if hashlib.sha256(payload[start:end]).hexdigest() != item['sha256']:
            raise ValueError('Disassembly window hash differs')
        command = [objdump, '-d', '--triple=thumbv7-none-eabi', '--mattr=+trustzone', '--print-imm-hex',
                   '--start-address='+hex(start), '--stop-address='+hex(end), str(obj)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=15, check=True)
        if result.stderr or len(result.stdout.encode()) > 16384:
            raise ValueError('Unexpected disassembler diagnostics/output size')
        text = result.stdout.replace(str(obj), '<analysis-only.o>')
        (args.output/(item['name']+'.txt')).write_text(text)
        excerpts.append(dict(item, text_sha256=hashlib.sha256(text.encode()).hexdigest()))
    report = {'scope': 'Static selected paths only; no firmware/device execution', 'lk_sha256': expected,
              'llvm_version': version, 'facts': facts, 'excerpts': excerpts,
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(facts, indent=2))


if __name__ == '__main__':
    main()
