#!/usr/bin/env python3
"""Verify PMIC candidate differs from baseline only in three child-node paths."""
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


def compare(baseline, candidate):
    if any(PREFIX + old not in baseline for old in RENAMES):
        raise ValueError('Baseline lacks the expected PMIC child nodes')
    expected = {}
    for path, properties in baseline.items():
        newpath = path
        for old, new in RENAMES.items():
            if path == PREFIX + old or path.startswith(PREFIX + old + '/'):
                newpath = PREFIX + new + path[len(PREFIX + old):]
                break
        if newpath in expected:
            raise ValueError('Rename collision')
        expected[newpath] = properties
    if expected != candidate:
        raise ValueError('Property values or unexpected node paths changed')
    return {'scope': 'Binary DT property/path comparison; no schema or hardware qualification',
            'nodes_compared': len(candidate), 'properties_compared': sum(len(x) for x in candidate.values()),
            'allowed_node_path_renames': RENAMES, 'property_values_identical': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fdtget', type=Path, default=ROOT / 'work/dtb-tool/build/fdtget')
    args = parser.parse_args()
    baseline = snapshot(args.fdtget, ROOT / 'work/dtb-compile/repro/douglas.dtb')
    candidate = snapshot(args.fdtget, ROOT / 'work/dtb-compile/pmic-node-names/douglas.dtb')
    print(json.dumps(compare(baseline, candidate), indent=2))


if __name__ == '__main__':
    main()
