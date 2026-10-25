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


def compare(baseline, candidate, include_sysirq=False, include_rdma=False):
    if any(PREFIX + old not in baseline for old in RENAMES):
        raise ValueError('Baseline lacks the expected PMIC child nodes')
    if include_sysirq and "/soc/intpol-controller@10200620" not in baseline:
        raise ValueError("Baseline lacks expected sysirq node")
    old_rdma, new_rdma = '/soc/dma-controller@14009000', '/soc/rdma@14009000'
    encode = lambda value: ' '.join(format(x, 'x') for x in value.encode()+b'\0')
    if include_rdma and (old_rdma not in baseline or baseline.get('/aliases', {}).get('rdma0') != encode(old_rdma)):
        raise ValueError('Baseline lacks expected RDMA node/alias')
    expected = {}
    for path, properties in baseline.items():
        newpath = path
        for old, new in RENAMES.items():
            if path == PREFIX + old or path.startswith(PREFIX + old + '/'):
                newpath = PREFIX + new + path[len(PREFIX + old):]
                break
        if include_sysirq and path == "/soc/intpol-controller@10200620":
            newpath = "/soc/interrupt-controller@10200620"
        if include_rdma and path == old_rdma:
            newpath = new_rdma
        if include_rdma and path == '/aliases':
            properties = {**properties, 'rdma0': encode(new_rdma)}
        if newpath in expected:
            raise ValueError('Rename collision')
        expected[newpath] = properties
    if expected != candidate:
        raise ValueError('Property values or unexpected node paths changed')
    return {'scope': 'Binary DT property/path comparison; no schema or hardware qualification',
            'nodes_compared': len(candidate), 'properties_compared': sum(len(x) for x in candidate.values()),
            'allowed_node_path_renames': RENAMES, 'property_values_identical': not include_rdma, 'sysirq_node_renamed': include_sysirq,
            'rdma_node_renamed': include_rdma, 'reviewed_alias_path_rewrites': ['rdma0'] if include_rdma else [],
            'all_other_property_values_identical': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fdtget', type=Path, default=ROOT / 'work/dtb-tool/build/fdtget')
    parser.add_argument('--experiment', choices=['pmic-node-names', 'sysirq-node-name', 'rdma-node-name'], default='pmic-node-names')
    args = parser.parse_args()
    baseline = snapshot(args.fdtget, ROOT / 'work/dtb-compile/repro/douglas.dtb')
    candidate = snapshot(args.fdtget, ROOT / 'work/dtb-compile' / args.experiment / 'douglas.dtb')
    print(json.dumps(compare(baseline, candidate, args.experiment in ['sysirq-node-name', 'rdma-node-name'], args.experiment == 'rdma-node-name'), indent=2))


if __name__ == '__main__':
    main()
