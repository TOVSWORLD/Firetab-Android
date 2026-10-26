#!/usr/bin/env python3
"""Check a resolved config for the opt-in forced diagnostic argument contract."""
import argparse
import hashlib
import json
from pathlib import Path
import re

EXPECTED='nr_cpus=1 maxcpus=0 earlycon=uart8250,mmio32,0x11002000 console=ttyS0,921600n8'
REQUIRED=('CMDLINE_FORCE','SERIAL_EARLYCON','SERIAL_8250','SERIAL_8250_CONSOLE',
          'SERIAL_8250_MT6577','OF_EARLY_FLATTREE')


def check(text):
    pairs=re.findall(r'^CONFIG_([A-Z0-9_]+)=(.*)$',text,re.M)
    if len({key for key,value in pairs}) != len(pairs):
        raise ValueError('Duplicate config symbol')
    config=dict(pairs)
    if config.get('CMDLINE') != json.dumps(EXPECTED):
        raise ValueError('Unexpected diagnostic command line')
    if any(config.get(key) != 'y' for key in REQUIRED):
        raise ValueError('Required built-in command-line/console support missing')
    if any(config.get(key,'n')!='n' for key in ('CMDLINE_EXTEND','CMDLINE_FROM_BOOTLOADER')):
        raise ValueError('Conflicting command-line mode')
    return {'resolved_config_contract_pass':True,
            'config_sha256':hashlib.sha256(text.encode()).hexdigest(),
            'compiled_or_runtime_verified':False,'loader_entry_verified':False,
            'physical_console_qualified':False,'physical_test_ready':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config',type=Path)
    args=parser.parse_args()
    print(json.dumps(check(args.config.read_text()),indent=2))


if __name__=='__main__':
    main()
