#!/usr/bin/env python3
"""Exact-build static LK bootargs writer trace and future log-token checks."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
from inspect_loader_layout import checked_file, lk_layout
from trace_lk_handoff import ROOT, thumb_call

EVIDENCE = ROOT/'evidence/lk-bootargs'


def required_limits(text):
    # Conservative plain kernel arguments only; do not reinterpret shell quoting.
    if not text or len(text) > 16384 or any(ord(c) < 32 or ord(c) > 126 for c in text) or any(c in text for c in '\\"\''):
        raise ValueError('Expected bounded plain ASCII command line without quoting')
    tokens = text.split()
    for key, expected in [('nr_cpus', 'nr_cpus=1'), ('maxcpus', 'maxcpus=0')]:
        selected = [x for x in tokens if x.split('=', 1)[0] == key]
        if selected != [expected]:
            raise ValueError('Missing, duplicated or conflicting primary-only limit: '+key)
    return {'required_tokens_present_once': True, 'effective_kernel_arguments_verified': False,
            'physical_boot_verified': False}


def pc_reference(payload, load, add):
    half, second = struct.unpack_from('<HH', payload, load)
    if half == 0xf8df:
        reg, pool = second >> 12, ((load+4)&~3)+(second&4095)
    elif half&0xf800 == 0x4800:
        reg, pool = (half>>8)&7, ((load+4)&~3)+4*(half&255)
    else:
        raise ValueError('Expected literal load')
    expected_add = 0x4478|(reg&7)|((reg&8)<<4)
    if struct.unpack_from('<H', payload, add)[0] != expected_add:
        raise ValueError('PC-relative add differs')
    target = (struct.unpack_from('<I', payload, pool)[0]+add+4)&0xffffffff
    raw = payload[target:target+128].split(b'\0', 1)
    if len(raw) != 2:
        raise ValueError('Unterminated bounded string')
    return {'load': hex(load), 'add': hex(add), 'pool': hex(pool), 'target': hex(target), 'text': raw[0].decode('ascii')}


def trace(payload):
    if len(payload) != 485040:
        raise ValueError('Unexpected exact-build payload length')
    for item in json.loads((EVIDENCE/'windows.json').read_text()):
        raw = payload[item['start']:item['end']]
        if raw.hex() != item['hex'] or hashlib.sha256(raw).hexdigest() != item['sha256']:
            raise ValueError('Static bootargs window differs')
    references = [pc_reference(payload, 0x3ed20, 0x3ed28), pc_reference(payload, 0x3e0da, 0x3e0e0),
                  pc_reference(payload, 0x3e5cc, 0x3e5da)]
    if [x['text'] for x in references] != ['%s %s', '/chosen', 'bootargs']:
        raise ValueError('Selected command-line/property references differ')
    calls = []
    for at, expected in [(0x3ed2a, 0x459e4), (0x3eda0, 0x3eb84), (0x3e0e2, 0x4643c),
                         (0x3e5c8, 0x45d58), (0x3e5dc, 0x46930), (0x46954, 0x464ac),
                         (0x46974, 0x468b4), (0x4699e, 0x45a58)]:
        target = thumb_call(*struct.unpack_from('<HH', payload, at), at)
        if target != expected:
            raise ValueError('Selected bootargs call target differs')
        calls.append({'offset': hex(at), 'target': hex(target)})
    table = (struct.unpack_from('<I', payload, 0x3ef54)[0]+0x3ebb4)&0xffffffff
    slot = table+struct.unpack_from('<I', payload, 0x3ef70)[0]
    pointer = struct.unpack_from('<I', payload, slot)[0]
    if table != 0x761f4 or pointer != 0x4bd74cb8:
        raise ValueError('Command buffer table reference differs')
    initial = payload[pointer-0x4bd00000:pointer-0x4bd00000+151]
    if not initial.endswith(b'\0'):
        raise ValueError('Initial command buffer terminator differs')
    return {'scope': 'Selected exact-build static paths only; not whole-loader emulation',
            'initial_file_backed_command_buffer': {'linked_address': hex(pointer), 'bytes_before_nul': len(initial)-1,
                'sha256_before_nul': hashlib.sha256(initial[:-1]).hexdigest(),
                'argument_keys': [x.split('=', 1)[0] for x in initial[:-1].decode('ascii').split()],
                'diagnostic_limits_present': b'nr_cpus=' in initial or b'maxcpus=' in initial},
            'references': references, 'calls': calls,
            'header_input': 'header+0x40 passed with current command buffer to %s %s formatting helper at3ed2a',
            'handoff_buffer': 'r4 -> r2 at3ed92; callee r2 -> r6 at3de28',
            'bootargs_write': 'chosen node; r3=current command buffer; length=strlen(buffer)+1',
            'existing_property_branch': 'resize data, replace big-endian length, copy new buffer from r9 into property data',
            'checked_writer_preserves_existing_dt_bootargs_by_itself': False,
            'failure_path': 'nonzero property-write result branches3e100, returns0; immediate wrapper loops',
            'dt_only_limits_sufficiently_preserved_by_loader': False,
            'unknowns': ['Initial command buffer construction/global mutations and all boot modes',
                         'Complete formatter and header validation/error lineage',
                         'All FDT helper mutations to PSCI status/CPU fields',
                         'Installed loader equivalence and actual effective command line'],
            'packaging_contract': 'Require diagnostic tokens in final loader output and later Kernel command line log; validate unique values; separately verify resulting PSCI status and online CPUs',
            'runtime_boot_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lk', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Fresh report file required')
    expected = json.loads((ROOT/'evidence/ota-loaders/inspection-result.json').read_text())['loader_images']['lk.bin']['sha256']
    image = checked_file(args.lk, expected)
    report = {'lk_sha256': expected, 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'facts': trace(image[lk_layout(image)['payload_offset']:])}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
