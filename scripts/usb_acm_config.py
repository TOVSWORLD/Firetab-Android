#!/usr/bin/env python3
"""Apply/check an explicit builtin ACM compile profile; never configure a gadget."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / 'projects/firetabs-android/kernel/usb-acm'


def requirements():
    lock = json.loads((PROFILE / 'profile.json').read_text())
    if hashlib.sha256((ROOT / lock['kconfig_source']).read_bytes()).hexdigest() != lock['kconfig_sha256']:
        raise ValueError('Pinned gadget Kconfig drift')
    for path, expected in lock.get('security_kconfig_sources', {}).items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != expected:
            raise ValueError('Pinned security Kconfig drift')
    states = {}
    for line in (PROFILE / 'fragment.config').read_text().splitlines():
        yes = re.fullmatch(r'CONFIG_([A-Z0-9_]+)=y', line)
        no = re.fullmatch(r'# CONFIG_([A-Z0-9_]+) is not set', line)
        lsm = re.fullmatch(r'CONFIG_(LSM)=("[a-z,]+")', line)
        if not (yes or no or lsm):
            if line: raise ValueError('Unexpected ACM fragment syntax')
            continue
        name = (yes or no or lsm)[1]
        if name in states: raise ValueError('Duplicate ACM fragment symbol')
        states[name] = lsm[2] if lsm else 'y' if yes else 'n'
    expected = {n: 'y' for n in lock['required_builtin']}
    expected.update({n: 'n' for n in lock['required_disabled']})
    expected['LSM'] = '"'+lock['lsm']+'"'
    if states != expected:
        raise ValueError('ACM requested policy changed or security/unrequested symbols added')
    return states, lock


def check(text):
    expected, lock = requirements()
    resolved = {}
    for line in text.splitlines():
        active = re.fullmatch(r'CONFIG_([A-Z0-9_]+)=(.*)', line)
        disabled = re.fullmatch(r'# CONFIG_([A-Z0-9_]+) is not set', line)
        if active or disabled:
            name = (active or disabled)[1]
            if name in resolved: raise ValueError('Duplicate resolved symbol: '+name)
            resolved[name] = active[2] if active else 'n'
    errors = [f'{n}: expected {v}, resolved {resolved.get(n,"n")}'
              for n, v in expected.items() if resolved.get(n, 'n') != v]
    errors += [f'{n}: required security must be builtin'
               for n in lock['security_required_builtin'] if resolved.get(n) != 'y']
    if errors: raise ValueError('; '.join(errors))
    return {'scope': 'Resolved builtin ACM profile only, not configured or executed USB',
            'required_builtin': lock['required_builtin'], 'other_configfs_functions_disabled': True,
            'selinux_required_builtin_and_listed': True, 'passed': True,
            'gadget_userspace_implemented': False, 'transport_qualified': False}


def object_targets():
    _, lock = requirements()
    for path, expected in lock['object_makefiles'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != expected:
            raise ValueError('Pinned gadget Makefile drift')
    source = (ROOT/'evidence/usb-gadget-prerequisites/gadget-Makefile').read_text()
    units = []
    for row in re.findall(r'^libcomposite-y\s*(?::=|\+=)\s*(.*)$', source, re.M):
        units += row.split()
    if units != ['usbstring.o','config.o','epautoconf.o','composite.o','functions.o','configfs.o','u_f.o']:
        raise ValueError('Unexpected builtin composite component set')
    functions = (ROOT/'evidence/usb-gadget-prerequisites/function-Makefile').read_text()
    if not re.search(r'^usb_f_acm-y\s*:=\s*f_acm.o$',functions,re.M):
        raise ValueError('Unexpected ACM component mapping')
    if not re.search(r'^obj-\$\(CONFIG_USB_U_SERIAL\)\s*\+=\s*u_serial.o$',functions,re.M):
        raise ValueError('Unexpected serial component mapping')
    return ['drivers/usb/gadget/'+n for n in units]+[
        'drivers/usb/gadget/function/f_acm.o','drivers/usb/gadget/function/u_serial.o']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['apply', 'check', 'objects'])
    parser.add_argument('config', type=Path, nargs='?')
    parser.add_argument('--source', type=Path)
    args = parser.parse_args()
    if args.mode == 'objects':
        print('\n'.join(object_targets()))
        return
    if args.config is None: parser.error('config required for apply/check')
    states, _ = requirements()
    if args.mode == 'apply':
        if args.source is None: parser.error('--source required for apply')
        for name, value in states.items():
            command = [str(args.source/'scripts/config'), '--file', str(args.config)]
            if name == 'LSM': command += ['--set-str', name, value[1:-1]]
            else: command += ['--enable' if value == 'y' else '--disable', name]
            subprocess.run(command, check=True)
    else:
        print(json.dumps(check(args.config.read_text()), indent=2))


if __name__ == '__main__':
    main()
