#!/usr/bin/env python3
"""Static CPU-node removal/frequency cap trace; host policy model, no firmware execution."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
from inspect_loader_layout import checked_file,lk_layout
from trace_lk_dtb_selection import LK_SHA,wide_pc_string
from trace_lk_handoff import analysis_object,thumb_pc_string,thumb_call

WINDOWS=[('callback',0x258ec,0x25a9a),('frequency',0x25794,0x257d4),
         ('caller',0x3e06a,0x3e07a),('node_remove',0x46c74,0x46cc8)]
WINDOW_HASHES={'callback': 'c3c101917983816075f05f35f010836d2af1b233ca5ca2181848bb42f9df8cf8', 'frequency': 'c452c47c220f4d6b7014f3dfd2780eeccaee22babcaa4e58d2b0926f1054c8e3', 'caller': '45b3e644d66979560714278354d9f2b4dcbffa5e7a26c118bb89a72a0db32857', 'node_remove': 'f67864419bbda1d28c9f45330b2427632bc2684276458365133e339cfe771873'}
CORE_LIMITS=[3,4,4,4,2,4,1]


def selected_policy(core_input,frequency_input,cpu_reg,clock_frequency):
    """Model only the selected node's keep/remove and downward cap decisions."""
    for x in [core_input,frequency_input,cpu_reg,clock_frequency]:
        if not isinstance(x,int) or not 0<=x<=0xffffffff:raise ValueError('32-bit input required')
    selector=(core_input>>4)&15
    limit=CORE_LIMITS[selector-8] if 8<=selector<=14 else 4
    frequency_selector=frequency_input&15
    cap=2000000000 if frequency_selector==0 else 2000000000-100000000*(frequency_selector-1) if frequency_selector<=10 else 1100000000
    keep=(cpu_reg&255)<limit
    return {'scope':'Host model only; not actual CPU count/rate/PSCI qualification',
            'core_limit':limit,'cap_hz':cap,'keep':keep,'cluster_bit':(cpu_reg>>8)&1,
            'clock_frequency_after':min(clock_frequency,cap) if keep else None}


def trace(payload):
    if len(payload)<0x765ac:raise ValueError('Truncated payload')
    word=lambda a:struct.unpack_from('<I',payload,a)[0]
    for name,a,b in WINDOWS:
        if hashlib.sha256(payload[a:b]).hexdigest()!=WINDOW_HASHES[name]:raise ValueError('Window drift: '+name)
    table=(word(0x25a9c)+0x25914+4)&0xffffffff
    if table!=0x5ef20 or [word(table+4*i) for i in range(7)]!=CORE_LIMITS:raise ValueError('Core limit table drift')
    if word(0x3e9c8)!=0x310 or word(0x761f4+0x310)!=0x4bd258ed:raise ValueError('Caller function-presence guard drift')
    refs=[thumb_pc_string(payload,a,b) for a,b in [(0x2591a,0x2591e),(0x2593c,0x2594a),
          (0x25948,0x2595a),(0x25958,0x25962)]]+[wide_pc_string(payload,0x2594c,0x2595c)]
    if [r['text'] for r in refs]!=['/cpus','reg','device_type','clock-frequency','cpu']:raise ValueError('CPU property reference drift')
    calls=[]
    for pc,target in [(0x3e076,0x258ec),(0x258f4,0x25794),(0x258fc,0x4b014),
                      (0x25798,0x4b014),(0x25920,0x4643c),(0x259d2,0x46c74),
                      (0x25a76,0x46930)]:
        if thumb_call(*struct.unpack_from('<HH',payload,pc),pc)!=target:raise ValueError('Call drift')
        calls.append({'offset':hex(pc),'target':hex(target)})
    return {'references':refs,'calls':calls,'core_table_offset':hex(table),'core_limits_selectors8_to14':CORE_LIMITS,
            'caller_guard':'GOT+0x310 is nonzero Thumb pointer0x4bd258ed; selected pinned artifact calls callback',
            'input':'Helper0x4b014 argument3 is read separately for frequency low nibble and core-limit bits4..7; actual value/stability unqualified',
            'removal':'device_type=cpu and low8 bits of first big-endian reg cell >= core limit selects node-removal helper0x46c74; not status=disabled',
            'frequency':'Retained nodes receive clock-frequency only when current cell exceeds selected cap; no upward rate assertion',
            'psci_limit':'Selected callback has no proven enable-method/PSCI rewrite; CPU-node mutation is not PSCI qualification',
            'unresolved':['Actual helper input and stability between its two reads',
                          'All malformed/missing property paths and nonstandard CPU reg encodings',
                          'Installed LK3 equivalence, other reservation/dispatcher writes and complete FDT lineage',
                          'Physical CPU boot/rates and independent failure return/log retention']}


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
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS selected CPU-node removal/cap trace; runtime gates open')


if __name__=='__main__':main()
