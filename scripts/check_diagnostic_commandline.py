#!/usr/bin/env python3
"""Check a resolved config for the opt-in forced diagnostic argument contract."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

EXPECTED='nr_cpus=1 maxcpus=0 earlycon=uart8250,mmio32,0x11002000 console=ttyS0,921600n8'
GENERIC_EXPECTED='nr_cpus=1 maxcpus=0 console=ttyAMA0 earlycon rdinit=/init panic=-1'
REQUIRED=('CMDLINE_FORCE','SERIAL_EARLYCON','SERIAL_8250','SERIAL_8250_CONSOLE',
          'SERIAL_8250_MT6577','OF_EARLY_FLATTREE')


def check(text, profile='device'):
    if profile not in ('device','generic-force'):
        raise ValueError('Unknown command-line profile')
    expected=EXPECTED if profile=='device' else GENERIC_EXPECTED
    pairs=re.findall(r'^CONFIG_([A-Z0-9_]+)=(.*)$',text,re.M)
    if len({key for key,value in pairs}) != len(pairs):
        raise ValueError('Duplicate config symbol')
    config=dict(pairs)
    if config.get('CMDLINE') != json.dumps(expected):
        raise ValueError('Unexpected diagnostic command line')
    required=REQUIRED + (('SERIAL_AMBA_PL011_CONSOLE',) if profile=='generic-force' else ())
    if any(config.get(key) != 'y' for key in required):
        raise ValueError('Required built-in command-line/console support missing')
    if any(config.get(key,'n')!='n' for key in ('CMDLINE_EXTEND','CMDLINE_FROM_BOOTLOADER')):
        raise ValueError('Conflicting command-line mode')
    return {'profile':profile,'resolved_config_contract_pass':True,
            'config_sha256':hashlib.sha256(text.encode()).hexdigest(),
            'compiled_or_runtime_verified':False,'loader_entry_verified':False,
            'physical_console_qualified':False,'physical_test_ready':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config',type=Path)
    parser.add_argument('--profile',choices=['device','generic-force'],default='device')
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--source',type=Path)
    args=parser.parse_args()
    if args.apply:
        if args.profile!='generic-force' or args.source is None:
            parser.error('Only explicit generic-force build application is supported')
        command=[str(args.source/'scripts/config'),'--file',str(args.config)]
        subprocess.run(command+['--set-str','CMDLINE',GENERIC_EXPECTED,'--enable','CMDLINE_FORCE',
            '--disable','CMDLINE_FROM_BOOTLOADER','--disable','CMDLINE_EXTEND'],check=True)
    else:
        print(json.dumps(check(args.config.read_text(),args.profile),indent=2))


if __name__=='__main__':
    main()
