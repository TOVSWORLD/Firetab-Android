#!/usr/bin/env python3
"""Build a separate deny-by-default static PID1 archive; never execute it or pack firmware."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
from build_diagnostic_initramfs import archive, inspect_elf
from validate_usb_acm_userspace_abi import validate
from validate_usb_acm_serial import validate as validate_serial

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'projects/firetabs-android/diagnostic-usb'
GATES = ['LOADING','RETURN','LOG_RETENTION','DEVICE_ROLE','SECURITY_POLICY','IMMUTABLE_NAMESPACE','DESCRIPTOR_ASSIGNMENT']
NAMES = ['dev','proc','sys','security','config','dev/console','init']


def admission_contract():
    validate()
    header=(SOURCE/'admission.h').read_text()
    for name in GATES:
        if re.findall(r'^#define FT_'+name+r'_QUALIFIED\s+(\S+)$',header,re.M)!=['0']:
            raise ValueError('Unqualified admission must remain zero: '+name)
    for name in ['VID','PID']:
        if re.findall(r'^#define FT_PHYSICAL_'+name+r'\s+(.*)$',header,re.M)!=['""']:
            raise ValueError('No physical USB descriptor assignment admitted')
    source=(SOURCE/'init.c').read_text()
    table=(ROOT/'evidence/usb-acm-userspace/source/syscall.tbl').read_text()
    for name,number in re.findall(r'^#define FT_NR_(MOUNT|UMOUNT2|NANOSLEEP) (\d+)$',source,re.M):
        if not re.search(r'^'+number+r'\s+(common|64)\s+'+name.lower()+r'\s',table,re.M):
            raise ValueError('PID1 syscall ABI drift: '+name)
    flags=(ROOT/'evidence/usb-acm-userspace/source/fcntl-generic.h').read_text()
    expected=re.search(r'^#define O_NONBLOCK\s+(\d+)',flags,re.M)
    actual=re.search(r'^#define FT_O_NONBLOCK (\d+)$',source,re.M)
    if not expected or not actual or int(expected[1],8)!=int(actual[1],8):
        raise ValueError('Nonblocking console ABI mismatch')
    return {'admitted':False,'gates':{name:False for name in GATES},'physical_descriptors_assigned':False}


def inspect_archive(data,elf):
    offset=0;entries=[]
    while True:
        if data[offset:offset+6]!=b'070701':raise ValueError('Invalid newc magic')
        fields=[int(data[offset+6+i*8:offset+14+i*8],16) for i in range(13)]
        start=offset+110;namesize=fields[11]
        if namesize<1 or namesize>64 or start+namesize>len(data):raise ValueError('Invalid name extent')
        raw=data[start:start+namesize]
        if raw[-1:]!=b'\0':raise ValueError('Unterminated name')
        name=raw[:-1].decode('ascii');start=(start+namesize+3)&~3
        end=start+fields[6]
        if end>len(data):raise ValueError('Invalid payload extent')
        payload=data[start:end];offset=(end+3)&~3
        if fields[2:6]!=[0,0,1,0]:raise ValueError('Unexpected ownership/time')
        if fields[7:9]!=[0,0] or fields[12]!=0:raise ValueError('Unexpected device/checksum metadata')
        if name=='TRAILER!!!':
            if fields[1] or fields[6] or fields[9:11]!=[0,0]:raise ValueError('Nonempty trailer')
            break
        if name not in NAMES or name in entries:raise ValueError('Unexpected archive entry')
        if name=='init':
            if fields[1]!=0o100755 or fields[9:11]!=[0,0] or payload!=elf:raise ValueError('Wrong PID1')
        elif name=='dev/console':
            if fields[1]!=0o020600 or fields[9:11]!=[5,1] or payload:raise ValueError('Wrong console node')
        elif fields[1]!=0o040755 or fields[9:11]!=[0,0] or payload:raise ValueError('Unexpected directory content')
        entries.append(name)
    if entries!=NAMES or any(data[offset:]):raise ValueError('Archive order/tail mismatch')
    return entries


def build(compiler,kind,output):
    admission=admission_contract();serial_contract=validate_serial();output.mkdir(parents=True,exist_ok=True)
    elf=output/'init'
    cmd=[compiler]
    if kind=='clang':cmd+=['--target=aarch64-linux-gnu','-fuse-ld=lld']
    cmd+=['-nostdlib','-static','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin',
          '-fno-stack-protector','-mgeneral-regs-only','-Wl,--build-id=none,-e,_start',
          '-o',str(elf),str(SOURCE/'init.c'),str(SOURCE/'memory.c')]
    subprocess.run(cmd,check=True)
    data=elf.read_bytes();inspection=inspect_elf(data)
    entries=[(n,0o040755,b'',(0,0)) for n in NAMES[:5]]
    entries += [('dev/console',0o020600,b'',(5,1)),('init',0o100755,data,(0,0))]
    raw=archive(entries);names=inspect_archive(raw,data)
    packed=bytearray(gzip.compress(raw,mtime=0));packed[9]=255;packed=bytes(packed)
    (output/'initramfs.cpio.gz').write_bytes(packed)
    report={'scope':'Separate static PID1 compile/archive only; current gadget admission denied',
            'admission':admission,'compiler':subprocess.check_output([compiler,'--version'],text=True).splitlines()[0],
            'command':[x.replace(str(ROOT),'<workspace>') for x in cmd],
            'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(SOURCE.glob('*')) if p.suffix in ('.c','.h')},
            'elf':inspection,'archive_entries':names,
            'artifacts':{n:{'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()} for n,b in [('init',data),('initramfs.cpio.gz',packed)]},
            'source_fixed_acm_frame_implemented':True,'package_output_admitted':False,'serial_contract':serial_contract,'boot_tested':False,'device_tested':False,'security_policy_qualified':False}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler',default='clang-18')
    parser.add_argument('--compiler-kind',choices=['clang','gcc'],default='clang')
    parser.add_argument('--output',type=Path,default=ROOT/'out/usb-acm-initramfs')
    args=parser.parse_args()
    print(json.dumps(build(args.compiler,args.compiler_kind,args.output),indent=2))

if __name__=='__main__':main()
