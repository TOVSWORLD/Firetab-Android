#!/usr/bin/env python3
"""Pin entry-r4 and local bootarg-buffer source contract; never run firmware."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
from inspect_loader_layout import checked_file, lk_layout
from trace_lk_dtb_selection import LK_SHA
from trace_lk_handoff import analysis_object, arm_branch, thumb_call

WINDOWS = [('startup','armv7',0x24,0x70),('writer','thumbv7',0x23230,0x23266),
           ('magic_copy','thumbv7',0x233a4,0x233b0),('init_call','thumbv7',0x2347c,0x23486)]
WINDOW_HASHES = {'startup':'613f2e9db3dc5b10caf3f65e6fe6c27471155c3e584880e06cbf921fa9985a49',
                'writer':'6fa3d3aea361a10fb75b1cc72b8732c413bca69aa50384988d1cbec000e7476b',
                'magic_copy':'077e8fdab8540966f6d6719381bdb43cc7e550a8c5d26173478d4318175e9a03',
                'init_call':'b6029493b17cbaf0d0e57b05f6f9357e7c5acb71bda2b46895af3ba3fec6c704'}


def trace(payload):
    if len(payload)<0x765ac:raise ValueError('Truncated file-backed payload')
    word=lambda o:struct.unpack_from('<I',payload,o)[0]
    for name,_,a,b in WINDOWS:
        if hashlib.sha256(payload[a:b]).hexdigest()!=WINDOW_HASHES[name]:
            raise ValueError('Selected instruction-window drift: '+name)
    if arm_branch(word(0),0)!=0x24 or (word(0x70),word(0x74),word(0x78),word(0x7c)) != (0x4bd00020,0x4bd00000,0x4bd765ac,0x4bd00080):
        raise ValueError('Startup/literal drift')
    if word(0x20)!=0:raise ValueError('Expected file-backed bootarg slot placeholder')
    got=word(0x233c0)+0x23240+4
    if got!=0x761f4:raise ValueError('Unexpected GOT')
    slots=[]
    for pool,offset,target in [(0x233c4,0x12c,0x4bd874c0),(0x233c8,0x98,0x4bd87340),(0x233cc,0x21c,0x4bd00020)]:
        if word(pool)!=offset or word(got+offset)!=target:raise ValueError('Pointer slot drift')
        slots.append({'literal_pool':hex(pool),'got_offset':hex(offset),'linked_target':hex(target)})
    calls=[]
    for pc,target in [(0x2347e,0x23230),(0x233a8,0x45a58)]:
        if thumb_call(*struct.unpack_from('<HH',payload,pc),pc)!=target:raise ValueError('Call drift')
        calls.append({'offset':hex(pc),'target':hex(target)})
    return {'entry_bootarg_register':'r4', 'entry_capture_address':'0x4bd00020',
            'capture_instruction_offset':'0x28', 'pointer_global':'0x4bd874c0',
            'local_buffer':'0x4bd87340','local_buffer_bytes':0x180,
            'magic':hex(0x504c504c),'slots':slots,'calls':calls,
            'writer':'0x23248 stores local buffer address into pointer-global before inspecting incoming bootarg magic',
            'matching_magic_path':'0x233a4 sets384-byte copy length;0x233a8 copies source from saved entry r4 into local buffer',
            'nonmatching_magic_path':'0x23256 onward parses alternate tags into local buffer; complete tag conversion unqualified',
            'lifetime':'Local buffer and pointer global lie beyond file-backed relocation range; full initialization/reset ordering unqualified',
            'relocation_caveat':'Absolute linked-address r4 store precedes relocation copy; alternate placement/pointer preservation not qualified',
            'unresolved':['Actual entry r4 pointer, accessibility,384-byte extent and magic',
                          'All subsequent writers and local-buffer lifetime across reset/alternate boot paths',
                          'Alternate tag conversion and alternate DT memory tuple branch',
                          'Installed LK3 equivalence, remaining PSCI/FDT lineage and failed-boot return/log retention']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lk',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():p.error('Fresh output directory required')
    raw=checked_file(args.lk,LK_SHA);payload=raw[lk_layout(raw)['payload_offset']:]
    facts=trace(payload)
    objdump=subprocess.check_output(['xcrun','--find','llvm-objdump'],text=True,timeout=15).strip()
    args.output.mkdir(parents=True);obj=args.output/'analysis-only.o';obj.write_bytes(analysis_object(payload))
    excerpts=[]
    for name,mode,a,b in WINDOWS:
        r=subprocess.run([objdump,'-d','--triple='+mode+'-none-eabi','--print-imm-hex','--start-address='+hex(a),'--stop-address='+hex(b),str(obj)],capture_output=True,text=True,check=True,timeout=15)
        if r.stderr or len(r.stdout)>32768:raise ValueError('Unexpected disassembler output')
        text=r.stdout.replace(str(obj),'<analysis-only.o>');(args.output/(name+'.txt')).write_text(text)
        excerpts.append({'name':name,'start':hex(a),'end':hex(b),'mode':mode,'sha256':hashlib.sha256(text.encode()).hexdigest()})
    report={'scope':'Static selected exact-OTA paths only; no firmware/device execution','lk_sha256':LK_SHA,
            'facts':facts,'excerpts':excerpts,'llvm_version':subprocess.check_output([objdump,'--version'],text=True,timeout=15).splitlines()[0]}
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS entry-r4/local-buffer provenance; relocation and runtime gates remain open')


if __name__=='__main__':main()
