#!/usr/bin/env python3
"""Validate the reviewed captured MT8163 power topology, not arbitrary SoCs/runtime."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def validate(node, infracfg_phandle):
    if type(infracfg_phandle) is not int or not 0 < infracfg_phandle < 0xffffffff:
        raise ValueError('Invalid declared INFRACFG phandle')
    if node.get('compatible') != ['mediatek,mt8163-scpsys', 'syscon', 'simple-mfd']:
        raise ValueError('Wrong captured syscon parent tuple')
    controller = node.get('power-controller', {})
    if controller.get('compatible') != ['mediatek,mt8163-power-controller']:
        raise ValueError('Wrong captured power-controller child')
    if 'access-controllers' in controller:
        raise ValueError('MT8163 has no configured modern bus-protection block list')
    found = {}
    def walk(parent, parent_id=None):
        for name, child in parent.items():
            if not name.startswith('power-domain@'):
                continue
            if not isinstance(child, dict) or child.get('status') not in [None, ['okay'], ['ok']]:
                raise ValueError('Captured candidate cannot silently disable/drop domains')
            reg = child.get('reg')
            if not isinstance(reg, list) or len(reg) != 1 or not isinstance(reg[0], list) or len(reg[0]) != 1:
                raise ValueError('Domain must declare one decoded ID')
            domain_id = reg[0][0]
            if type(domain_id) is not int or not 0 <= domain_id <= 7 or domain_id in found:
                raise ValueError('Domain ID is out of range or duplicated')
            if (domain_id == 7 and parent_id != 6) or (domain_id != 7 and parent_id is not None):
                raise ValueError('Reviewed hierarchy requires only MFG under MFG_ASYNC')
            if domain_id in [0, 4, 6] and child.get('mediatek,infracfg') != [[infracfg_phandle]]:
                raise ValueError('Protected domain does not reference the reviewed INFRACFG')
            if 'domain-supply' in child:
                raise ValueError('MT8163 domain supply capability is absent')
            if len(child.get('clocks', [])) != len(child.get('clock-names', [])):
                raise ValueError('Domain clock/name count mismatch')
            if domain_id in [0, 1, 2, 3, 6] and not child.get('clocks'):
                raise ValueError('Captured model requires the basic domain clock')
            found[domain_id] = parent_id
            walk(child, domain_id)
    walk(controller)
    if set(found) != set(range(8)):
        raise ValueError('Captured candidate must retain all eight reviewed domains')
    return {'scope': 'Captured candidate topology only; no power/clock sequencing or runtime proof',
            'domain_ids': sorted(found), 'mfg_parent': found[7],
            'protected_ids': [0, 4, 6], 'infracfg_phandle': infracfg_phandle,
            'clock_name_counts_consistent': True, 'runtime_qualified': False}


def from_dtb(binary, dtb):
    """Read only the fixed reviewed DT paths; domains use one-cell clock providers."""
    def get(option, path, prop=None):
        args = [str(binary), option, str(dtb), path]
        if prop is not None:
            args.append(prop)
        return subprocess.check_output(args, text=True).strip().split()
    def strings(path, prop):
        return get('-ts', path, prop)
    def numbers(path, prop):
        return [int(x) for x in get('-tu', path, prop)]
    parent_path = '/soc/syscon@10006000'
    controller_path = parent_path + '/power-controller'
    infra_path = '/soc/clock-controller@10001000'
    if strings(infra_path, 'compatible') != ['mediatek,mt8163-infracfg', 'syscon']:
        raise ValueError('Captured INFRACFG target tuple changed')
    def read(path):
        result = {}
        properties = get('-p', path)
        for key in ['compatible', 'status', 'clock-names']:
            if key in properties:
                result[key] = strings(path, key)
        for key in ['reg', 'mediatek,infracfg']:
            if key in properties:
                result[key] = [numbers(path, key)]
        for key in ['domain-supply', 'access-controllers']:
            if key in properties:
                result[key] = True  # Presence itself is unsupported by this model.
        if 'clocks' in properties:
            cells = numbers(path, 'clocks')
            if len(cells) % 2:
                raise ValueError('Captured clock specifiers must be phandle plus one ID')
            result['clocks'] = [cells[i:i+2] for i in range(0, len(cells), 2)]
        for child in get('-l', path):
            if child.startswith('power-domain@'):
                result[child] = read(path + '/' + child)
        return result
    node = {'compatible': strings(parent_path, 'compatible'), 'power-controller': read(controller_path)}
    phandle = numbers(infra_path, 'phandle')
    if len(phandle) != 1:
        raise ValueError('INFRACFG must have one declared phandle')
    return node, phandle[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('node', type=Path, nargs='?')
    parser.add_argument('--dtb', type=Path)
    parser.add_argument('--fdtget', type=Path, default=Path(__file__).resolve().parents[1] / 'work/dtb-tool/build/fdtget')
    parser.add_argument('--infracfg-phandle', type=int)
    args = parser.parse_args()
    if bool(args.node) == bool(args.dtb):
        parser.error('Choose one decoded node JSON or --dtb')
    if args.dtb:
        if args.infracfg_phandle is not None:
            parser.error('DTB mode resolves its own declared INFRACFG phandle')
        node, phandle = from_dtb(args.fdtget, args.dtb)
    else:
        node, phandle = json.loads(args.node.read_text()), args.infracfg_phandle
    result = validate(node, phandle)
    if args.dtb:
        result['dtb_sha256'] = hashlib.sha256(args.dtb.read_bytes()).hexdigest()
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
