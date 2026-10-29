#!/usr/bin/env python3
"""Hash/ABI/source checks for source-only fixed ACM status output; not transport admission."""
import hashlib
import json
from pathlib import Path
import re
from validate_usb_acm_userspace_abi import integer, validate as validate_base
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'evidence/usb-acm-serial/source'
SOURCE=ROOT/'projects/firetabs-android/diagnostic-usb/acm_serial.h'


def validate():
    validate_base()
    receipt=json.loads((EVIDENCE/'sources.json').read_text())
    for item in receipt['sources']:
        name=item['path'].replace('/','_') if item['path'].endswith('Kbuild') or item['path']=='include/linux/kdev_t.h' else item['path'].rsplit('/',1)[-1]
        name=item.get('file',name)
        data=(EVIDENCE/name).read_bytes()
        if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:
            raise ValueError('Pinned serial source drift: '+name)
    text=SOURCE.read_text()
    macros=dict(re.findall(r'^#define (FT_SERIAL_[A-Z0-9_]+)\s+(0x[0-9a-f]+|[0-9]+)$',text,re.M))
    table=(ROOT/'evidence/usb-acm-userspace/source/syscall.tbl').read_text()
    for name in ['IOCTL','MKNODAT','STATX','NANOSLEEP']:
        value=macros['FT_SERIAL_'+name]
        if not re.search(r'^'+value+r'\s+(common|64)\s+'+name.lower()+r'\s',table,re.M):
            raise ValueError('Serial syscall mismatch: '+name)
    flags=(ROOT/'evidence/usb-acm-userspace/source/fcntl-generic.h').read_text()
    flags+='\n'+(ROOT/'evidence/usb-acm-userspace/source/fcntl-linux.h').read_text()
    declarations={
        'NOCTTY':('O_NOCTTY',flags),'NONBLOCK':('O_NONBLOCK',flags),'AT_EMPTY_PATH':('AT_EMPTY_PATH',flags),
        'TCGETS':('TCGETS',(EVIDENCE/'ioctls.h').read_text()),'TCSETS':('TCSETS',(EVIDENCE/'ioctls.h').read_text()),
        'STATX_TYPE':('STATX_TYPE',(EVIDENCE/'stat.h').read_text()),
        'IFCHR':('S_IFCHR',(EVIDENCE/'stat.h').read_text()),'IFMT':('S_IFMT',(EVIDENCE/'stat.h').read_text())}
    termbits=(EVIDENCE/'termbits.h').read_text()+'\n'+(EVIDENCE/'termbits-common.h').read_text()
    for name in ['B9600','CS8','CREAD','CLOCAL','VMIN','VTIME']:declarations[name]=(name,termbits)
    for name,(original,source) in declarations.items():
        found=re.search(r'^#define\s+'+original+r'\s+(0x[0-9a-f]+|[0-9]+)(?:U)?\b',source,re.M)
        if not found or integer(found[1])!=integer(macros['FT_SERIAL_'+name]):
            raise ValueError('Serial constant mismatch: '+name)
    directory=json.loads((EVIDENCE/'arm64-uapi-directory.txt').read_text().split('\n',1)[1])
    if any(x['name'] in ['termbits.h','termios.h','ioctls.h'] for x in directory['entries']):
        raise ValueError('ARM64 TTY header override requires fresh ABI review')
    chain=(EVIDENCE/'include_uapi_asm-generic_Kbuild').read_text()
    if not all('mandatory-y += '+n in chain for n in ['termbits.h','termios.h','ioctls.h']):
        raise ValueError('Generic TTY ABI selection drift')
    if '#include <asm/termbits.h>' not in (EVIDENCE/'termios.h').read_text():raise ValueError('Termios include chain drift')
    acm=(EVIDENCE/'f_acm.c').read_text();serial=(EVIDENCE/'u_serial.c').read_text()
    for anchor in ['CONFIGFS_ATTR_RO(f_acm_, port_num)','gserial_alloc_line(&opts->port_num)','gserial_connect(&acm->port, acm->port_num);']:
        if anchor not in acm:raise ValueError('ACM ownership/activation source drift')
    for anchor in ['driver->name = "ttyGS"','tty_port_register_device(&port->port,','GS_CLOSE_TIMEOUT * HZ','count = kfifo_in(&port->port_write_buf, buf, count)']:
        if anchor not in serial:raise ValueError('TTY allocation/write/close source drift')
    if '(minor & 0xff) | (major << 8) | ((minor & ~0xff) << 12)' not in (EVIDENCE/'include_linux_kdev_t.h').read_text():
        raise ValueError('Modern device encoding drift')
    return {'source_contract':'Allocated function port_num -> dynamic ttyGS dev identity; fd statx; raw termios; fixed bounded frame',
            'syscalls':{n:integer(macros['FT_SERIAL_'+n]) for n in ['IOCTL','MKNODAT','STATX','NANOSLEEP']},
            'write_return_is_not_host_receipt':True,'driver_close_timeout_seconds_source':15,
            'strict_wall_clock_bound_qualified':False,'device_tested':False,'runtime_qualified':False}


if __name__=='__main__':print(json.dumps(validate(),indent=2))
