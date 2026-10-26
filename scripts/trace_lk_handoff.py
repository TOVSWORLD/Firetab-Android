#!/usr/bin/env python3
"""Static exact-build LK trace. Makes a non-loadable analysis object; never runs firmware."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
from inspect_loader_layout import checked_file, lk_layout

ROOT = Path(__file__).resolve().parents[1]
WINDOWS = [('startup', 'armv7', 0, 0x70),
           ('save_parameters', 'thumbv7', 0x3de1c, 0x3de32),
           ('k64_select_and_call', 'thumbv7', 0x3e732, 0x3e74a),
           ('forwarding_wrapper', 'thumbv7', 0x3ddd0, 0x3ddfa),
           ('smc_transition', 'armv7', 0x3c8e0, 0x3c8fc)]


def arm_branch(word, pc):
    if word & 0xff000000 not in (0xea000000, 0xeb000000):
        raise ValueError('Expected unconditional ARM B/BL')
    immediate = word & 0xffffff
    if immediate & 0x800000:
        immediate -= 1 << 24
    return pc+8+(immediate << 2)


def thumb_call(first, second, pc):
    if first & 0xf800 != 0xf000 or second & 0xd000 not in (0xc000, 0xd000):
        raise ValueError('Expected Thumb BL/BLX immediate')
    exchange = second & 0x1000 == 0
    if exchange and second & 1:
        raise ValueError('Invalid BLX alignment bit')
    sign = (first >> 10) & 1
    i1, i2 = 1-(((second >> 13) & 1)^sign), 1-(((second >> 11) & 1)^sign)
    offset = (sign << 24) | (i1 << 23) | (i2 << 22) | ((first & 1023) << 12) | ((second & 2047) << 1)
    if sign:
        offset -= 1 << 25
    return ((pc+4)&~3 if exchange else pc+4)+offset


def thumb_pc_string(payload, load_offset, add_offset):
    first = struct.unpack_from('<H', payload, load_offset)[0]
    register = (first >> 8) & 7
    if first & 0xf800 != 0x4800 or struct.unpack_from('<H', payload, add_offset)[0] != 0x4478+register:
        raise ValueError('Expected Thumb literal load plus same-register PC add')
    pool = ((load_offset+4)&~3)+4*(first & 255)
    relative = struct.unpack_from('<I', payload, pool)[0]
    target = (relative+add_offset+4)&0xffffffff
    raw = payload[target:target+128].split(b'\0', 1)
    if len(raw) != 2:
        raise ValueError('Unterminated bounded string reference')
    return {'load_offset': hex(load_offset), 'add_pc_offset': hex(add_offset),
            'literal_pool_offset': hex(pool), 'target_offset': hex(target),
            'text': raw[0].decode('ascii')}


def analysis_object(payload):
    if not payload or len(payload) > 1024*1024:
        raise ValueError('Bounded analysis payload required')
    names = b'\0.text\0.shstrtab\0'
    names_offset = 256+len(payload)
    sections = (names_offset+len(names)+3)&~3
    result = bytearray(sections+120)
    # ET_REL, no entry point and no program headers: not a bootable image.
    struct.pack_into('<16sHHIIIIIHHHHHH', result, 0, b'\x7fELF\1\1\1'+bytes(9),
                     1, 40, 1, 0, 0, sections, 0x05000000, 52, 0, 0, 40, 3, 2)
    result[256:256+len(payload)] = payload
    result[names_offset:names_offset+len(names)] = names
    struct.pack_into('<10I', result, sections+40, 1, 1, 6, 0, 256, len(payload), 0, 0, 4, 0)
    struct.pack_into('<10I', result, sections+80, 7, 3, 0, 0, names_offset, len(names), 0, 0, 1, 0)
    return bytes(result)


def trace(payload):
    if len(payload) < 0x3eb84:
        raise ValueError('Truncated LK analysis payload')
    def word(offset): return struct.unpack_from('<I', payload, offset)[0]
    def exact(offset, encoded):
        if payload[offset:offset+len(encoded)] != encoded:
            raise ValueError(f'Instruction anchor mismatch at {offset:x}')
    # Match instruction anchors, not arbitrary string/literal hits.
    if arm_branch(word(0), 0) != 0x24:
        raise ValueError('Unexpected reset branch')
    for offset, value in [(0x40, 0xe1a0000f), (0x44, 0xe2400048), (0x48, 0xe59f1024),
                          (0x4c, 0xe1500001), (0x50, 0x0a00000a), (0x54, 0xe59f201c), (0x58, 0xe4903004),
                          (0x5c, 0xe4813004), (0x60, 0xe1510002), (0x64, 0x1afffffb),
                          (0x68, 0xe59f000c), (0x6c, 0xe12fff10)]:
        if word(offset) != value:
            raise ValueError('Relocation sequence differs')
    if word(0x7c) != word(0x74)+0x80 or not word(0x74) < word(0x78) <= word(0x74)+len(payload):
        raise ValueError('Invalid linked relocation literals')
    for offset, encoded in [(0x3de1c, bytes.fromhex('2de9f04fadf2ac4d')),
                            (0x3ddd0, bytes.fromhex('f8b504460d46014617461e46')), (0x3de2a, bytes.fromhex('0d46')), (0x3de2e, bytes.fromhex('0a90')),
                            (0x3e73c, bytes.fromhex('0a98294600220123')),
                            (0x3dde4, bytes.fromhex('204629463a463346')),
                            (0x3c8e0, bytes.fromhex('0340a0e10230a0e10120a0e10010a0e108009fe5700060e1'))]:
        exact(offset, encoded)
    calls = []
    for at, expected in [(0x3eb90, 0x3de1c), (0x3e744, 0x3ddd0), (0x3ddec, 0x3c8e0)]:
        first, second = struct.unpack_from('<HH', payload, at)
        if (second & 0x1000 == 0) != (at == 0x3ddec):
            raise ValueError('Call state transition differs')
        target = thumb_call(first, second, at)
        if target != expected:
            raise ValueError('Call target differs')
        calls.append({'payload_offset': hex(at), 'target_offset': hex(target)})
    if word(0x3c900) != 0x82000200:
        raise ValueError('SMC function ID differs')
    return {'linked_base_from_startup_literal': hex(word(0x74)),
            'relocation_copy_end_literal': hex(word(0x78)), 'relocation_target_literal': hex(word(0x7c)),
            'checked_calls': calls,
            'k64_log_reference': thumb_pc_string(payload, 0x3dddc, 0x3ddde),
            'fdt_label_reference': thumb_pc_string(payload, 0x3e96c, 0x3e970), 'smc_offset': '0x3c8f4', 'smc_function_id': '0x82000200',
            'smc_registers_on_checked_path': {'r0': '0x82000200', 'r1': 'stack slot +0x28, saved incoming r0; earlier producer not yet traced',
                'r2': 'r5 at selected call site; complete lineage unresolved', 'r3': 0, 'r4': 1},
            'checked_wrapper_adjusts_entry_alignment': False,
            'complete_parameter_lineage_verified': False,
            'upstream_header_decompression_flow_complete': False, 'secure_monitor_behavior_verified': False,
            'runtime_boot_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lk', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Fresh output directory required')
    expected = json.loads((ROOT/'evidence/ota-loaders/inspection-result.json').read_text())['loader_images']['lk.bin']['sha256']
    image = checked_file(args.lk, expected)
    layout = lk_layout(image)
    payload = image[layout['payload_offset']:]
    facts = trace(payload)
    objdump = shutil.which('llvm-objdump')
    if objdump is None:
        objdump = subprocess.check_output(['xcrun', '--find', 'llvm-objdump'], text=True, timeout=15).strip()
    version = subprocess.check_output([objdump, '--version'], text=True, timeout=15).splitlines()[0]
    args.output.mkdir(parents=True)
    obj = args.output/'analysis-only.o'
    obj.write_bytes(analysis_object(payload))
    excerpts = []
    for name, mode, start, end in WINDOWS:
        command = [objdump, '-d', '--triple='+mode+'-none-eabi', '--mattr=+trustzone', '--print-imm-hex',
                   '--start-address='+hex(start), '--stop-address='+hex(end), str(obj)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=15, check=True)
        if result.stderr or len(result.stdout.encode()) > 65536:
            raise ValueError('Unexpected disassembler diagnostics/output size')
        text = result.stdout.replace(str(obj), '<analysis-only.o>')
        (args.output/(name+'.txt')).write_text(text)
        excerpts.append({'name': name, 'mode': mode, 'payload_start': hex(start), 'payload_end': hex(end),
                         'sha256': hashlib.sha256(text.encode()).hexdigest()})
    report = {'scope': 'Static ARM/Thumb instruction evidence only; firmware never executed',
              'lk_sha256': expected, 'llvm_version': version, 'analysis_object_type': 'ET_REL; no entry/program headers',
              'facts': facts, 'excerpts': excerpts, 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
