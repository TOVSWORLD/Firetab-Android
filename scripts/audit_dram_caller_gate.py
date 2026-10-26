#!/usr/bin/env python3
"""Inspect pinned source AST only; never import or execute the candidate loader."""
import ast
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def analyze(text):
    tree = ast.parse(text)
    methods = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    upload = methods['upload_da1']
    gates = [n for n in ast.walk(upload) if isinstance(n, ast.If)
             and isinstance(n.test, ast.Call) and isinstance(n.test.func, ast.Attribute)
             and n.test.func.attr == 'set_stage2_config']
    if len(gates) != 1:
        raise ValueError('Expected exactly one direct initialization gate')
    gate = gates[0]
    stage_calls = [n for n in ast.walk(upload) if isinstance(n, ast.Call)
                   and isinstance(n.func, ast.Attribute) and n.func.attr == 'brom_send']
    gated = {id(n) for statement in gate.body for n in ast.walk(statement)}
    if not stage_calls or not all(id(n) in gated for n in stage_calls):
        raise ValueError('Stage transfer outside reviewed initialization gate')
    return {'initializer_gate_line': gate.lineno,
            'stage_transfer_lines': [n.lineno for n in stage_calls],
            'all_stage_transfers_in_truthy_initializer_branch': True,
            'caller_requires_literal_true': False,
            'local_try_handlers_in_upload_da1': sum(isinstance(n, ast.Try) for n in ast.walk(upload)),
            'scope': 'AST containment only; no protocol or runtime qualification',
            'physical_test_ready': False}


def main():
    receipt = json.loads((ROOT/'evidence/dram-response-contract/source-review.json').read_text())
    path = ROOT/'out/recovery-entry/mtkclient'/receipt['source_path']
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != receipt['sha256']:
        raise ValueError('Pinned source identity mismatch')
    print(json.dumps({'revision': receipt['revision'], 'source_path': receipt['source_path'],
                      'source_sha256': receipt['sha256'], **analyze(data.decode())}, indent=2))


if __name__ == '__main__':
    main()
