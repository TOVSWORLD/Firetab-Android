#!/usr/bin/env python3
"""Bounded static DT selection receipt; never execute input firmware."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
from inspect_loader_layout import checked_file, lk_layout
from trace_lk_handoff import analysis_object, thumb_call, thumb_pc_string

LK_SHA = '4ca0cca7ae9af6e959dc848b9ca002624c62e1bb93c83c0ecc89bae8d2186b08'
DT_SHA = 'b837e6cb439d43778527c834e534abddb271170fd29cb6b13b174272214d1411'


def wide_pc_string(payload, load, add):
    first, second = struct.unpack_from('<HH', payload, load)
    register = second >> 12
    if first != 0xf8df or struct.unpack_from('<H', payload, add)[0] != 0x4478+(register & 7)+((register & 8) << 4):
        raise ValueError('Expected wide literal load and matching PC add')
    pool = ((load+4) & ~3)+(second & 4095)
    target = (struct.unpack_from('<I', payload, pool)[0]+add+4) & 0xffffffff
    pieces = payload[target:target+128].split(b'\0', 1)
    if len(pieces) != 2:
        raise ValueError('Missing bounded string terminator')
    return {'load': hex(load), 'add': hex(add), 'pool': hex(pool),
            'target': hex(target), 'text': pieces[0].decode('ascii')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lk', type=Path, required=True)
    parser.add_argument('--dtb', type=Path, required=True)
    parser.add_argument('--fdtget', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Fresh output directory required')
    raw = checked_file(args.lk, LK_SHA)
    payload = raw[lk_layout(raw)['payload_offset']:]
    checked_file(args.dtb, DT_SHA)
    refs = [wide_pc_string(payload, a, b) for a, b in
            [(0x3de76, 0x3de88), (0x3de7e, 0x3de8e), (0x3df76, 0x3df7c)]]
    assert [x['text'] for x in refs] == ['version', 'not fdt prop\n', 'ERROR: No valid DT found for version %s\n']
    selector_key = thumb_pc_string(payload, 0x209b2, 0x209bc)
    assert selector_key['text'] == 'board_id'
    # Relocated pointer table: use the image-linked base, not host addresses.
    linked_base = struct.unpack_from('<I', payload, 0x74)[0]
    got_base = struct.unpack_from('<I', payload, 0x20a38)[0]+0x20994+4
    table = struct.unpack_from('<I', payload, got_base+0x318)[0]-linked_base
    versions = [payload[table+i*17:table+(i+1)*17].split(b'\0', 1)[0].decode('ascii') for i in range(8)]
    assert versions == ['pre_evt']+['hvt']*6+['invalid']
    calls = {}
    for pc, target in [(0x3de38, 0x20984), (0x3dee6, 0x3de04),
                       (0x3df08, 0x46cc8), (0x3df14, 0x45f34),
                       (0x3df26, 0x464ac), (0x3df62, 0x45cc0)]:
        assert thumb_call(*struct.unpack_from('<HH', payload, pc), pc) == target
        calls[hex(pc)] = hex(target)
    # Branches: null property -> rescan; zero comparison -> selected path -> trim.
    for pc, encoded in [(0x3df2e, '00f02181'), (0x3df68, '00f0fb80'),
                         (0x3e172, '14e7'), (0x3e17a, '9be6')]:
        if payload[pc:pc+len(bytes.fromhex(encoded))] != bytes.fromhex(encoded):
            raise ValueError('Branch anchor mismatch at '+hex(pc))
    result = subprocess.run([args.fdtget, '-ts', str(args.dtb), '/', 'version'],
                            capture_output=True, text=True, timeout=15)
    if result.returncode != 1 or 'FDT_ERR_NOTFOUND' not in result.stderr or result.stdout:
        raise ValueError('Expected exact candidate missing-version observation')
    args.output.mkdir(parents=True)
    obj = args.output/'analysis-only.o'
    obj.write_bytes(analysis_object(payload))
    objdump = subprocess.check_output(['xcrun', '--find', 'llvm-objdump'], text=True, timeout=15).strip()
    excerpts = []
    for name, start, end in [('entry', 0x3de1c, 0x3de44), ('selection', 0x3de76, 0x3dfa8),
                             ('match', 0x3e162, 0x3e17c), ('compare', 0x45cc0, 0x45cde),
                             ('selector', 0x20984, 0x20a32), ('copy', 0x3de04, 0x3de1c)]:
        r = subprocess.run([objdump, '-d', '--triple=thumbv7-none-eabi', '--print-imm-hex',
                            '--start-address='+hex(start), '--stop-address='+hex(end), str(obj)],
                           capture_output=True, text=True, check=True, timeout=15)
        if r.stderr or len(r.stdout) > 32768:
            raise ValueError('Unexpected disassembler output')
        text = r.stdout.replace(str(obj), '<analysis-only.o>')
        (args.output/(name+'.txt')).write_text(text)
        excerpts.append({'name': name, 'start': hex(start), 'end': hex(end),
                         'sha256': hashlib.sha256(text.encode()).hexdigest()})
    report = {'scope': 'Exact OTA LK static selection only; installed LK3 equivalence and execution untested',
              'lk_sha256': LK_SHA, 'candidate_dtb_sha256': DT_SHA,
              'candidate_root_version': 'FDT_ERR_NOTFOUND', 'strings': refs, 'calls': calls,
              'selector_key': selector_key, 'selector_table_offset': hex(table),
              'selector_versions': versions, 'llvm_version': subprocess.check_output([objdump, '--version'], text=True, timeout=15).splitlines()[0],
              'excerpts': excerpts, 'selector_runtime_value': 'unqualified; producer uses runtime state',
              'result': 'Missing version follows rescan branch in this cached route; matching installed route remains unqualified',
              'next': 'Trace selector runtime provenance, incoming DT destination, late fixups and final handoff; do not invent a version or execute loader'}
    (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
