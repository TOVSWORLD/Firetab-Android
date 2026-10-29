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
    states = {}
    for line in (PROFILE / 'fragment.config').read_text().splitlines():
        yes = re.fullmatch(r'CONFIG_([A-Z0-9_]+)=y', line)
        no = re.fullmatch(r'# CONFIG_([A-Z0-9_]+) is not set', line)
        if not (yes or no):
            if line: raise ValueError('Unexpected ACM fragment syntax')
            continue
        name = (yes or no)[1]
        if name in states: raise ValueError('Duplicate ACM fragment symbol')
        states[name] = 'y' if yes else 'n'
    expected = {n: 'y' for n in lock['required_builtin']}
    expected.update({n: 'n' for n in lock['required_disabled']})
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
    errors += [f'{n}: existing security must remain builtin'
               for n in lock['security_required_unchanged_builtin'] if resolved.get(n) != 'y']
    if errors: raise ValueError('; '.join(errors))
    return {'scope': 'Resolved builtin ACM profile only, not configured or executed USB',
            'required_builtin': lock['required_builtin'], 'other_configfs_functions_disabled': True,
            'selinux_kept_builtin': True, 'passed': True,
            'gadget_userspace_implemented': False, 'transport_qualified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['apply', 'check'])
    parser.add_argument('config', type=Path)
    parser.add_argument('--source', type=Path)
    args = parser.parse_args()
    states, _ = requirements()
    if args.mode == 'apply':
        if args.source is None: parser.error('--source required for apply')
        for name, value in states.items():
            subprocess.run([str(args.source/'scripts/config'), '--file', str(args.config),
                            '--enable' if value == 'y' else '--disable', name], check=True)
    else:
        print(json.dumps(check(args.config.read_text()), indent=2))


if __name__ == '__main__':
    main()
