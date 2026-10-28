#!/usr/bin/env python3
"""Static alternate-memory and optional IDME fixup boundaries; no firmware execution."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
from inspect_loader_layout import checked_file,lk_layout
from trace_lk_dtb_selection import LK_SHA,wide_pc_string
from trace_lk_handoff import analysis_object,thumb_pc_string,thumb_call

WINDOWS=[('guard',0x3e07a,0x3e09c),('alternate',0x3e17c,0x3e22c),
         ('dispatcher',0x140,0x158),('registration',0x50e,0x522),
         ('idme_lookup',0xda6,0xdc2),('idme_property_refs',0xe08,0xe1e),('idme_writes',0xe80,0xecc)]
WINDOW_HASHES = {'idme_property_refs': '0be5a76592f6985466e6ba0f05b6c9e375b7df5c411ca61446c95d96dabce887', 'guard': 'd9c42ee022e4197cc0904505585fb6f79324aac507e74c0231bf98e6994563b6', 'alternate': '6d0b4bc7f69615a6dd9161ab52650ff20d012fca6a5c30dca4b9ba54a8541bb7', 'dispatcher': '6b147c369517165ae9887db472a594939cb025a86516ecb63868318b8a207fb7', 'registration': '74d9cf431ebe5b11901f15ffe9affd8818a92b7ea61f91a6f9844a7851f3311e', 'idme_lookup': '0be9fdcbb4ed9489d5aa96584d750cda999c1e9cdcd2dbc2d3724974844e9e15', 'idme_writes': '0bb5cdf405d5226ab4c31f0185e92c8d534709b476daa72b59b3daece259f84c'}


def encode_alternate_ranks(ranks,last_adjustment):
    """Owned host arithmetic model for selected zero-high-cell branch only."""
    if not isinstance(last_adjustment,int) or not 0<=last_adjustment<=0xffffffff:
        raise ValueError('32-bit adjustment required')
    if len(ranks)>4:raise ValueError('Model restricted to initializer rank limit')
    result=[]
    for i,(start,size) in enumerate(ranks):
        if not all(isinstance(v,int) and 0<=v<=0xffffffff for v in [start,size]):
            raise ValueError('32-bit rank values required')
        subtract=last_adjustment if i==len(ranks)-1 else 0
        result.append({'start':start,'size':(size-subtract)&0xffffffff,
                       'subtraction_wrapped':subtract>size})
    return {'scope':'Host model; not runtime memory validation','ranges':result,
            'dt_reg_hex':b''.join(struct.pack('>IIII',0,r['start'],0,r['size']) for r in result).hex()}


def trace(payload):
    if len(payload)<0x765ac:raise ValueError('Truncated payload')
    word=lambda a:struct.unpack_from('<I',payload,a)[0]
    for name,a,b in WINDOWS:
        if hashlib.sha256(payload[a:b]).hexdigest()!=WINDOW_HASHES[name]:raise ValueError('Window drift: '+name)
    got=0x761f4
    slots=[]
    for pool,offset,target in [(0x3e9cc,0x380,0x4bd25ac5),(0x3e9d0,0x2b0,0x4bd874e4),
                               (0x3e9fc,0x39c,0x4bd874e8),(0x3ea00,0x138,0x4bd874c4),
                               (0x5c0,0xdc,0x4bd00d85)]:
        if word(pool)!=offset or word(got+offset)!=target:raise ValueError('GOT slot drift')
        slots.append({'pool':hex(pool),'got_offset':hex(offset),'linked_target':hex(target)})
    callback=(word(0x158)+0x144+4)&0xffffffff
    context=(word(0x15c)+0x14c+4)&0xffffffff
    registration=(word(0x5c4)+0x51e+4)&0xffffffff
    if (callback,context,registration)!=(0x7c010,0x7c014,0x7c010):raise ValueError('Dispatcher storage drift')
    refs=[wide_pc_string(payload,0xda6,0xdb4),thumb_pc_string(payload,0xe12,0xe14),thumb_pc_string(payload,0xe18,0xe1a)]
    if [r['text'] for r in refs]!=['/idme','value','permission']:raise ValueError('IDME property drift')
    for pc,target in [(0xdbe,0x4643c),(0xe90,0x46930),(0xec8,0x46930)]:
        if thumb_call(*struct.unpack_from('<HH',payload,pc),pc)!=target:raise ValueError('Call drift')
    return {'slots':slots,'references':refs,
            'alternate_guard':'GOT entry is nonzero Thumb function pointer0x4bd25ac5; pinned artifact takes helper path, not alternate branch, absent later mutation',
            'alternate_arithmetic':'32-bit start/size pairs become zero-high64-bit DT cells; subtract runtime adjustment from last size modulo2^32; FDT r5 saved/restored atstack+0x2c',
            'callback_storage_payload':hex(callback),'context_storage_payload':hex(context),
            'selected_registered_target':'0x4bd00d85 (Thumb payload0xd84); conditional setup0x51c/0x520',
            'selected_target_effect':'Looks up /idme and writes value/permission properties from runtime context; full record enumeration and identity contents unqualified',
            'privacy':'Raw post-fixup DTB may contain device/household identifiers; keep it private in ignored out and publish normalized allowlisted facts only',
            'unresolved':['All GOT and dispatcher storage writers/selected setup outcome',
                          'Runtime alternate rank count/adjustment and actual callback context',
                          'Remaining PSCI/reservation callbacks and complete FDT lineage',
                          'Installed LK3 equivalence, physical placement and failure return/log retention']}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--lk',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    args=p.parse_args()
    if args.output.exists():p.error('Fresh output directory required')
    raw=checked_file(args.lk,LK_SHA);payload=raw[lk_layout(raw)['payload_offset']:];facts=trace(payload)
    objdump=subprocess.check_output(['xcrun','--find','llvm-objdump'],text=True,timeout=15).strip()
    args.output.mkdir(parents=True);obj=args.output/'analysis-only.o';obj.write_bytes(analysis_object(payload));excerpts=[]
    for name,a,b in WINDOWS:
        r=subprocess.run([objdump,'-d','--triple=thumbv7-none-eabi','--print-imm-hex','--start-address='+hex(a),'--stop-address='+hex(b),str(obj)],capture_output=True,text=True,check=True,timeout=15)
        if r.stderr or len(r.stdout)>32768:raise ValueError('Unexpected disassembler output')
        text=r.stdout.replace(str(obj),'<analysis-only.o>');(args.output/(name+'.txt')).write_text(text)
        excerpts.append({'name':name,'start':hex(a),'end':hex(b),'sha256':hashlib.sha256(text.encode()).hexdigest()})
    report={'scope':'Static selected exact-OTA paths only; no firmware/device execution','lk_sha256':LK_SHA,'facts':facts,'excerpts':excerpts,'llvm_version':subprocess.check_output([objdump,'--version'],text=True,timeout=15).splitlines()[0]}
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS alternate guard and selected dispatcher/IDME boundary; runtime gates open')


if __name__=='__main__':main()
