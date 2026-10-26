#!/usr/bin/env python3
"""Inspect pinned cached selector AST and Git metadata; never run upstream code."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def selector_facts(source):
    tree = ast.parse(source)
    funcs = {x.name: x for x in ast.walk(tree) if isinstance(x, ast.FunctionDef)}
    parse = funcs['parse_da_loader']
    tautologies = [x.lineno for x in ast.walk(parse) if isinstance(x, ast.Compare)
        and len(x.ops) == 1 and isinstance(x.ops[0], ast.Eq)
        and ast.dump(x.left) == ast.dump(x.comparators[0])
        and isinstance(x.left, ast.Attribute) and x.left.attr == 'hw_sub_code']
    if not tautologies:
        raise ValueError('Expected selector source changed; re-audit')
    setup = funcs['setup']
    attrs = sorted({x.attr for x in ast.walk(setup) if isinstance(x, ast.Attribute)})
    return {'dedup_subcode_self_comparison_lines': tautologies,
            'setup_reads_subcode': 'hw_sub_code' in attrs,
            'setup_reads_hardware_version': 'hw_version' in attrs,
            'setup_reads_software_version': 'sw_version' in attrs,
            'actual_device_selection_verified': False,
            'subcode_compatibility_failure_observed_on_device': False}


def main():
    index = json.loads((ROOT/'evidence/recovery-agent/source-index.json').read_text())
    loaded = {}
    for item in index['files']:
        raw = (ROOT/'out/recovery-entry/mtkclient'/item['source_path']).read_bytes()
        if len(raw) != item['bytes'] or hashlib.sha256(raw).hexdigest() != item['sha256']:
            raise ValueError('Pinned source mismatch')
        loaded[item['source_path']] = raw.decode()
    raw = (ROOT/'out/recovery-entry/mtkclient-tree.json').read_bytes()
    if len(raw) != index['tree_bytes'] or hashlib.sha256(raw).hexdigest() != index['tree_sha256']:
        raise ValueError('Pinned Git tree mismatch')
    tree = json.loads(raw)
    if tree['truncated']:
        raise ValueError('Incomplete repository inventory')
    loaders = [{k: x[k] for k in ('path', 'sha', 'size')} for x in tree['tree']
        if x['type'] == 'blob' and ('MTK_AllInOne_DA' in x['path'].split('/')[-1]
                                   or 'MTK_DA' in x['path'].split('/')[-1])]
    payload = next({k:x[k] for k in ('path','sha','size')} for x in tree['tree']
                  if x['path'] == 'mtkclient/payloads/mt8163_payload.bin')
    report = {'revision':index['revision'],
        'selection':selector_facts(loaded['mtkclient/Library/DA/daconfig.py']),
        'default_filename_candidates':loaders,
        'candidate_total_bytes':sum(x['size'] for x in loaders),
        'security_bootstrap_payload_metadata':payload,
        'metadata_sha_kind':'Git blob SHA1, not downloaded-content SHA256 or vendor signature',
        'candidate_binaries_downloaded':False, 'selected_da_binary_identified':False,
        'vendor_signature_verified':False, 'physical_test_ready':False,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
