#!/usr/bin/env python3
"""Audit pinned cached Python as syntax only. Never load upstream modules."""
import ast
import hashlib
import json
from pathlib import Path
from audit_recovery_entry_escrow import functions, calls

ROOT = Path(__file__).resolve().parents[1]


def local_reachability(source, root):
    _, funcs = functions(source)
    seen, todo = set(), [root]
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        seen.add(name)
        for call in calls(funcs[name]):
            callee = call['callee']
            if callee.startswith('self.') and callee.count('.') == 1:
                target = callee[5:]
                if target in funcs and target not in seen:
                    todo.append(target)
    return {
        'root': root,
        'same_file_reachable_methods': sorted(seen),
        'external_calls_not_resolved': sorted({c['callee'] for name in seen
            for c in calls(funcs[name])
            if not (c['callee'].startswith('self.') and c['callee'][5:] in funcs)}),
        'reachable_storage_write_methods': sorted(seen & {
            'writeflash', 'formatflash', 'sdmmc_write_data', 'sdmmc_write_image'}),
        'scope': 'Syntactic same-file self.method closure only; not a device-effect proof',
    }


def partition_switch_facts(source):
    _, funcs = functions(source)
    read = funcs['readflash']
    discarded = [n.lineno for n in ast.walk(read) if isinstance(n, ast.Expr)
        and isinstance(n.value, ast.Call)
        and ast.unparse(n.value.func) == 'self.sdmmc_switch_part']
    switch = funcs['sdmmc_switch_part']
    returns_false = any(isinstance(n, ast.Return) and isinstance(n.value, ast.Constant)
                        and n.value.value is False for n in ast.walk(switch))
    if not discarded or not returns_false:
        raise ValueError('Expected unchecked partition switch changed; re-audit')
    return {'discarded_switch_result_lines': discarded,
            'switch_can_return_false': returns_false,
            'wrong_region_read_possible_if_selection_fails': True,
            'failure_observed_on_device': False,
            'backup_region_identity_qualified': False}


def main():
    index = json.loads((ROOT / 'evidence/recovery-bootstrap/source-index.json').read_text())
    loaded = {}
    for record in index['files']:
        data = (ROOT / 'out/recovery-entry/mtkclient' / record['source_path']).read_bytes()
        if len(data) != record['bytes'] or hashlib.sha256(data).hexdigest() != record['sha256']:
            raise ValueError('Pinned source cache mismatch')
        loaded[record['source_path']] = data.decode()
    legacy = loaded['mtkclient/Library/DA/legacy/dalegacy_lib.py']
    _, funcs = functions(legacy)
    report = {
        'revision': index['revision'],
        'legacy_upload': local_reachability(legacy, 'upload_da'),
        'legacy_read': local_reachability(legacy, 'readflash'),
        'partition_switch': partition_switch_facts(legacy),
        'bootstrap_upload_external_calls': calls(funcs['upload_da1']),
        'stage2_configuration_external_calls': calls(funcs['set_stage2_config']),
        'agent_binary_or_payload_audited': False,
        'backend_selected_on_actual_device_verified': False,
        'globally_persistence_free_verified': False,
        'mac_cli_import_closure_complete': False,
        'physical_test_ready': False,
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
