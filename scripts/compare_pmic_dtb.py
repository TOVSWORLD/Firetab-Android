#!/usr/bin/env python3
"""Verify reviewed PMIC and optional sysirq node-path changes preserve all properties."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
RENAMES = {'mt6323regulator': 'regulators', 'mt6323keys': 'keys', 'mt6397codec': 'audio-codec'}
PREFIX = '/soc/pwrap@1000d000/mt6323/'


def snapshot(binary, dtb):
    result = {}
    pending = ['/']
    def query(option, node, prop=None):
        command = [str(binary), option, str(dtb), node]
        if prop is not None:
            command.append(prop)
        return subprocess.check_output(command, text=True).strip()
    while pending:
        node = pending.pop()
        result[node] = {name: query('-tbx', node, name) for name in query('-p', node).splitlines()}
        pending.extend(node.rstrip('/') + '/' + child for child in query('-l', node).splitlines())
    return result


def compare(baseline, candidate, include_sysirq=False):
    if any(PREFIX + old not in baseline for old in RENAMES):
        raise ValueError('Baseline lacks the expected PMIC child nodes')
    if include_sysirq and "/soc/intpol-controller@10200620" not in baseline:
        raise ValueError("Baseline lacks expected sysirq node")
    expected = {}
    for path, properties in baseline.items():
        newpath = path
        for old, new in RENAMES.items():
            if path == PREFIX + old or path.startswith(PREFIX + old + '/'):
                newpath = PREFIX + new + path[len(PREFIX + old):]
                break
        if include_sysirq and path == "/soc/intpol-controller@10200620":
            newpath = "/soc/interrupt-controller@10200620"
        if newpath in expected:
            raise ValueError('Rename collision')
        expected[newpath] = properties
    if expected != candidate:
        raise ValueError('Property values or unexpected node paths changed')
    return {'scope': 'Binary DT property/path comparison; no schema or hardware qualification',
            'nodes_compared': len(candidate), 'properties_compared': sum(len(x) for x in candidate.values()),
            'allowed_node_path_renames': RENAMES, 'property_values_identical': True, 'sysirq_node_renamed': include_sysirq}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fdtget', type=Path, default=ROOT / 'work/dtb-tool/build/fdtget')
    parser.add_argument('--experiment', choices=['pmic-node-names', 'sysirq-node-name'], default='pmic-node-names')
    args = parser.parse_args()
    baseline = snapshot(args.fdtget, ROOT / 'work/dtb-compile/repro/douglas.dtb')
    candidate = snapshot(args.fdtget, ROOT / 'work/dtb-compile' / args.experiment / 'douglas.dtb')
    print(json.dumps(compare(baseline, candidate, args.experiment == 'sysirq-node-name'), indent=2))


if __name__ == '__main__':
    main()
