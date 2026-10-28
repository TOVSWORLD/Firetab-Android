#!/usr/bin/env python3
"""Static exact-OTA memory fixups and host-only tuple decoder. Never run firmware."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
from inspect_loader_layout import checked_file, lk_layout
from trace_lk_dtb_selection import LK_SHA
from trace_lk_handoff import analysis_object, thumb_call, thumb_pc_string

WINDOWS = [('tuple_producer', 0x25ac4, 0x25bac),
           ('memory_metadata', 0x25bbc, 0x25c4a),
           ('framebuffer', 0x25c4a, 0x25d1c),
           ('caller', 0x3e07a, 0x3e0da)]


WINDOW_HASHES = {'tuple_producer': 'f6ca67c468132206fb8a2328e52c92f37517d936cbf2da6b43e27113e10666d5', 'memory_metadata': 'd189460dc8e90403bd029aed2aadd4d73568aa3f22adec082cfd0aa56e08b4eb', 'framebuffer': '78a2a19d30aed8c1c3074f0cecc856ce4b824a3840c41ab1de65c31134fdbea3', 'caller': 'ff1409779b2e4a19591b1486f9845c07b92c5ea8779d4ff73276eeaf467cef39'}

def decode_mblocks(raw):
    """Decode a caller-supplied runtime struct snapshot, not an installed read."""
    if not 0x38 <= len(raw) <= 4096:
        raise ValueError('Bounded structure snapshot required')
    count = struct.unpack_from('<I', raw, 0x30)[0]
    if count > 4:
        raise ValueError('Exceeds selected caller capacity of four records')
    if len(raw) < 0x38+count*24:
        raise ValueError('Truncated mblock records')
    ranges = []
    for i in range(count):
        start, size = struct.unpack_from('<QQ', raw, 0x38+i*24)
        ranges.append({'start': start, 'size': size})
    encoded = b''.join(struct.pack('>QQ', r['start'], r['size']) for r in ranges)
    return {'scope': 'Host decoding model only; no firmware execution or memory validation',
            'count': count, 'ranges': ranges, 'dt_reg_hex': encoded.hex()}


def trace(payload):
    if len(payload) < 0x76324:
        raise ValueError('Truncated exact-build payload')
    for name,a,b in WINDOWS:
        if hashlib.sha256(payload[a:b]).hexdigest() != WINDOW_HASHES[name]:
            raise ValueError('Selected instruction window drift: '+name)
    anchors = [(0x25ad2,'5b581b68196b029391425ed8'), (0x25ada,'91425ed8002958d0'),
               (0x25aec,'03f140067a44039256f8082c'), (0x25b04,'10377468'),
               (0x25b58,'47f80cac'), (0x25b70,'47f804cc0493183647f808ec'),
               (0x25b80,'47f8109c'), (0x25b8c,'029a136b4345afd8')]
    for a, h in anchors:
        if payload[a:a+len(bytes.fromhex(h))] != bytes.fromhex(h):
            raise ValueError('Instruction drift at '+hex(a))
    pairs = [(0x25ae6,0x25af0), (0x25b9c,0x25b9e), (0x25bc2,0x25bcc),
             (0x25be4,0x25bec), (0x25c06,0x25c0c), (0x25c1c,0x25c28),
             (0x25c36,0x25c40), (0x25c4a,0x25c4e), (0x25c54,0x25c5a),
             (0x25c64,0x25c66), (0x25c6e,0x25c7a), (0x25c9a,0x25c9e)]
    refs = [thumb_pc_string(payload,a,b) for a,b in pairs]
    expected = ['mblock[%d].start: 0x%llx, size: 0x%llx\n',
                'mblock_info->mblock_num =%d is bigger than mem_property=%d\n',
                '/memory','orig_dram_info','mblock_info','lca_reserved_mem',
                'tee_reserved_mem','/reserved-memory','fb-reserved-memory',
                'mediatek,fb-reserved-memory','compatible','reg']
    if [r['text'] for r in refs] != expected:
        raise ValueError('Unexpected metadata reference')
    calls = []
    for pc,target in [(0x3e08c,0x25ac4),(0x3e0ce,0x25bbc),(0x25bd8,0x4643c),
                      (0x25bf0,0x46930),(0x25c0e,0x46930),(0x25c2a,0x46930),
                      (0x25c42,0x46930),(0x25c50,0x4643c),(0x25c5c,0x46c54),
                      (0x25c7c,0x46930),(0x25ce0,0x46930)]:
        if thumb_call(*struct.unpack_from('<HH',payload,pc),pc) != target:
            raise ValueError('Call target drift at '+hex(pc))
        calls.append({'offset':hex(pc),'target':hex(target)})
    got = struct.unpack_from('<I',payload,0x25bac)[0]+0x25ad0+4
    slot = got+struct.unpack_from('<I',payload,0x25bb0)[0]
    pointer_global = struct.unpack_from('<I',payload,slot)[0]
    if (got,slot,pointer_global) != (0x761f4,0x76320,0x4bd874c0):
        raise ValueError('Runtime pointer provenance drift')
    return {'calls':calls,'references':refs,
            'runtime_structure_pointer_global':hex(pointer_global),
            'runtime_pointer_value_file_backed':False,
            'tuple_layout':{'count_offset':0x30,'records_offset':0x38,'stride':24,
                            'start_offset':0,'size_offset':8,'output_bytes_per_record':16,
                            'selected_caller_max_records':4,'output_endianness':'big'},
            'metadata_copies':[{'property':'orig_dram_info','offset':0x98,'bytes':0x48},
                               {'property':'mblock_info','offset':0x30,'bytes':0x68},
                               {'property':'lca_reserved_mem','offset':0xe0,'bytes':16},
                               {'property':'tee_reserved_mem','offset':0xf0,'bytes':16}],
            'framebuffer':'Adds fb-reserved-memory child, compatible string and16-byte reg from runtime globals; actual geometry unqualified',
            'unresolved':['Runtime structure writer and actual count/records',
                          'Alternate inline memory-tuple branch at0x3e17c',
                          'Complete reserved-memory/PSCI callback inventory and selected r5 lineage',
                          'Installed LK3 equivalence, physical placement and failure return/log retention']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lk',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    args=p.parse_args()
    if args.output.exists():p.error('Fresh output directory required')
    raw=checked_file(args.lk,LK_SHA)
    payload=raw[lk_layout(raw)['payload_offset']:]
    facts=trace(payload)
    objdump=subprocess.check_output(['xcrun','--find','llvm-objdump'],text=True,timeout=15).strip()
    args.output.mkdir(parents=True)
    obj=args.output/'analysis-only.o';obj.write_bytes(analysis_object(payload))
    excerpts=[]
    for name,a,b in WINDOWS:
        r=subprocess.run([objdump,'-d','--triple=thumbv7-none-eabi','--print-imm-hex',
                          '--start-address='+hex(a),'--stop-address='+hex(b),str(obj)],
                         capture_output=True,text=True,check=True,timeout=15)
        if r.stderr or len(r.stdout)>32768:raise ValueError('Unexpected disassembler output')
        text=r.stdout.replace(str(obj),'<analysis-only.o>')
        (args.output/(name+'.txt')).write_text(text)
        excerpts.append({'name':name,'start':hex(a),'end':hex(b),'sha256':hashlib.sha256(text.encode()).hexdigest()})
    report={'scope':'Static selected exact-OTA paths only; no firmware/device execution',
            'lk_sha256':LK_SHA,'facts':facts,'excerpts':excerpts,
            'llvm_version':subprocess.check_output([objdump,'--version'],text=True,timeout=15).splitlines()[0]}
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS selected memory producer and metadata references; runtime gates open')


if __name__=='__main__':main()
