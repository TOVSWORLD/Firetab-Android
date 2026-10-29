#!/usr/bin/env python3
"""Audit the current builtin-only ACM candidate; never operate USB or grant boot admission."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'evidence/usb-gadget-prerequisites'
BUILTINS = ['USB_GADGET', 'USB_ROLE_SWITCH', 'USB_CONFIGFS', 'USB_LIBCOMPOSITE',
            'USB_F_ACM', 'USB_U_SERIAL', 'USB_CONFIGFS_ACM', 'CONFIGFS_FS']


def config_states(text):
    result = {}
    for line in text.splitlines():
        match = re.fullmatch(r'CONFIG_([A-Z0-9_]+)=(y|m)', line)
        disabled = re.fullmatch(r'# CONFIG_([A-Z0-9_]+) is not set', line)
        if match or disabled:
            name = (match or disabled)[1]
            if name in result:
                raise ValueError('Duplicate configuration symbol: ' + name)
            result[name] = match[2] if match else 'n'
        elif line and not line.startswith('#'):
            raise ValueError('Unexpected normalized configuration line')
    return result


def archive_inventory(data):
    """Read bounded newc data without extracting or executing any entry."""
    if len(data) > 8 * 1024 * 1024:
        raise ValueError('Diagnostic archive exceeds audit bound')
    offset = 0; entries = {}
    while offset + 110 <= len(data):
        if data[offset:offset+6] != b'070701':
            raise ValueError('Unsupported/truncated newc header')
        try:
            fields = [int(data[offset+6+i*8:offset+14+i*8], 16) for i in range(13)]
        except ValueError as error:
            raise ValueError('Invalid newc number') from error
        size, namesize = fields[6], fields[11]
        start = offset + 110
        if not 1 <= namesize <= 256 or start + namesize > len(data):
            raise ValueError('Invalid newc name')
        raw = data[start:start+namesize]
        if raw[-1:] != b'\0' or b'\0' in raw[:-1]:
            raise ValueError('Invalid newc name terminator')
        name = raw[:-1].decode('ascii')
        begin = (start + namesize + 3) & ~3
        end = begin + size
        if end > len(data):
            raise ValueError('Truncated newc payload')
        offset = (end + 3) & ~3
        if name == 'TRAILER!!!':
            if size or any(data[offset:]):
                raise ValueError('Unexpected trailer payload/data')
            return entries
        if name in entries or name.startswith('/') or '..' in name.split('/'):
            raise ValueError('Duplicate or unsafe archive name')
        entries[name] = {'mode': oct(fields[1]), 'bytes': size,
                         'sha256': hashlib.sha256(data[begin:end]).hexdigest()}
    raise ValueError('Missing newc trailer')


def source_facts():
    receipt = json.loads((EVIDENCE / 'inputs.json').read_text())
    for path, expected in receipt['inputs'].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError('Pinned gadget prerequisite input drift: ' + path)
    musb = (ROOT / 'evidence/usb-prerequisites/ack/mediatek.c').read_text()
    for token in ['glue->role = USB_ROLE_NONE;', 'glue->phy_mode = PHY_MODE_USB_OTG;',
                  'role_sx_desc.allow_userspace_control = true;',
                  'return mtk_otg_switch_set(usb_role_switch_get_drvdata(sw), role);',
                  'phy_set_mode(glue->phy, glue->phy_mode);']:
        if token not in musb:
            raise ValueError('Controller role source drift')
    kconfig = (EVIDENCE / 'gadget-Kconfig').read_text()
    make = (EVIDENCE / 'gadget-Makefile').read_text()
    functions = (EVIDENCE / 'function-Makefile').read_text()
    for token in ['config USB_CONFIGFS\n', 'select USB_LIBCOMPOSITE', 'select USB_U_SERIAL', 'select USB_F_ACM']:
        if token not in kconfig:
            raise ValueError('Gadget Kconfig source drift')
    for text, token in [(make, 'obj-$(CONFIG_USB_LIBCOMPOSITE)'),
                        (make, 'configfs.o'), (functions, 'obj-$(CONFIG_USB_F_ACM)'),
                        (functions, 'usb_f_acm.o'), (functions, 'obj-$(CONFIG_USB_U_SERIAL)')]:
        if token not in text:
            raise ValueError('Gadget object composition drift')
    return receipt


def audit(states, entries):
    source_facts()
    expected = {'dev', 'proc', 'sys', 'dev/console', 'init'}
    if set(entries) != expected or entries['init']['mode'] != oct(0o100755):
        raise ValueError('Current diagnostic package contract changed; new review required')
    missing = {name: states.get(name, 'unavailable') for name in BUILTINS if states.get(name) != 'y'}
    return {'scope': 'Pinned source/config/package prerequisites only, not gadget or boot execution',
            'candidate_strategy': 'builtin-only configfs ACM; module-loading alternative not admitted by this audit',
            'non_builtin_required_symbols': missing,
            'archive_entries': sorted(entries), 'packaged_modules': [],
            'pid1_gadget_setup_implemented': False,
            'current_dt_role': 'otg -> PHY_MODE_USB_OTG / USB_ROLE_NONE',
            'controller_and_phy_remain_disabled': True,
            'role_api_error_propagation_qualified': False,
            'source_package_ready': False, 'transport_qualified': False,
            'loading_return_log_qualified': False,
            'blockers': ['Builtin ACM candidate still has modular/unavailable prerequisites' if missing else 'Builtin symbols alone do not configure a gadget',
                         'Current PID1 has no configfs gadget setup or module-loading path',
                         'Current DT is disabled/OTG; no device-role handoff qualified',
                         'No physical USB or independent experimental failure return/log qualification']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=EVIDENCE / 'resolved-gadget.config')
    parser.add_argument('--initramfs', type=Path, default=ROOT / 'out/diagnostic-initramfs/initramfs.cpio.gz')
    parser.add_argument('--require-ready', action='store_true')
    args = parser.parse_args()
    # Limit decompression before parsing; never extract the archive.
    with gzip.open(args.initramfs, 'rb') as stream:
        data = stream.read(8 * 1024 * 1024 + 1)
    result = audit(config_states(args.config.read_text()), archive_inventory(data))
    print(json.dumps(result, indent=2))
    if args.require_ready and not result['source_package_ready']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
