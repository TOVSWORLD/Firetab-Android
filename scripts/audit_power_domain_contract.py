#!/usr/bin/env python3
"""Compare pinned legacy/candidate domain IDs and register/protection values."""
import argparse
import ast
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'evidence/power-port/domain-contract'


def definitions(text):
    text = text.replace('\\\n', '')
    return dict(re.findall(r'^[ \t]*#define[ \t]+(\w+)[ \t]+([^\n]+)', text, re.M))


def value(expression, macros, seen=()):
    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return node.value
        if isinstance(node, ast.Name) and node.id in macros and node.id not in seen:
            return value(macros[node.id], macros, seen + (node.id,))
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            return visit(node.left) | visit(node.right)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            args = [visit(x) for x in node.args]
            if node.func.id == 'BIT' and len(args) == 1 and 0 <= args[0] < 32:
                return 1 << args[0]
            if node.func.id == 'GENMASK' and len(args) == 2 and 0 <= args[1] <= args[0] < 32:
                return ((1 << (args[0] + 1)) - 1) ^ ((1 << args[1]) - 1)
        raise ValueError('Unsupported register expression: ' + expression)
    return visit(ast.parse(' '.join(expression.split()), mode='eval').body)


def domains(text):
    result = {}
    for symbol, body in re.findall(r'\[(MT8163_POWER_DOMAIN_\w+)\]\s*=\s*\{(.*?)\n\t\},', text, re.S):
        name = re.search(r'\.name\s*=\s*"(\w+)"', body)[1]
        if name in result:
            raise ValueError('Duplicate domain name: ' + name)
        result[name] = (symbol, body)
    if len(result) != 8:
        raise ValueError('Expected eight real MT8163 domains')
    return result


def compare(old, new, old_macros, new_macros):
    before, after = domains(old), domains(new)
    if set(before) != set(after):
        raise ValueError('Domain set changed')
    rows = []
    for name in sorted(before):
        old_id, old_body = before[name]
        new_id, new_body = after[name]
        ids = [value(old_id, old_macros), value(new_id, new_macros)]
        if ids[0] != ids[1]:
            raise ValueError('Domain ID mismatch: ' + name)
        fields = {}
        for field in ['sta_mask', 'ctl_offs', 'sram_pdn_bits', 'sram_pdn_ack_bits']:
            # GENMASK contains a comma; consume the entire assignment line.
            extract = lambda body: re.search(r'\.' + field + r'\s*=\s*([^\n]+),', body)[1]
            a, b = value(extract(old_body), old_macros), value(extract(new_body), new_macros)
            if a != b:
                raise ValueError('Domain field mismatch: ' + name + '.' + field)
            fields[field] = b
        old_bp = re.search(r'\.bus_prot_mask\s*=\s*([^,]+),', old_body)
        new_bp = re.search(r'BUS_PROT_INFRA_UPDATE_TOPAXI\(([^)]+)\)', new_body)
        a = value(old_bp[1], old_macros) if old_bp else 0
        b = value(new_bp[1], new_macros) if new_bp else 0
        if a != b:
            raise ValueError('Bus-protection mismatch: ' + name)
        rows.append({'name': name, 'id': ids[1], 'register_fields': fields,
                     'bus_protection_mask': b,
                     'legacy_active_wakeup': '.active_wakeup = true' in old_body,
                     'candidate_active_wakeup': 'MTK_SCPD_ACTIVE_WAKEUP' in new_body})
    return rows


def load_sources():
    legacy = (EVIDENCE / 'legacy-scpsys.c').read_text()
    candidate = (ROOT / 'projects/firetabs-android/kernel/power-port/overlay/drivers/pmdomain/mediatek/mt8163-pm-domains.h').read_text()
    old_macros = definitions(legacy + '\n' + (EVIDENCE / 'legacy-infracfg.h').read_text() + '\n' + (EVIDENCE / 'legacy-power.h').read_text())
    patch = (ROOT / 'projects/firetabs-android/kernel/power-port/provider.patch').read_text()
    added = '\n'.join(line[1:] for line in patch.splitlines() if line.startswith('+') and not line.startswith('+++'))
    new_macros = definitions((ROOT / 'evidence/power-port/ack/drivers/pmdomain/mediatek/mtk-pm-domains.h').read_text() + '\n' + added + '\n' + (ROOT / 'projects/firetabs-android/kernel/power-port/overlay/include/dt-bindings/power/mediatek,mt8163-power-controller.h').read_text())
    return legacy, candidate, old_macros, new_macros


def audit():
    legacy, candidate, old_macros, new_macros = load_sources()
    rows = compare(legacy, candidate, old_macros, new_macros)
    for symbol in ['SPM_PWR_STATUS', 'SPM_PWR_STATUS_2ND']:
        if value(symbol, old_macros) != value(symbol, new_macros):
            raise ValueError('Power status register mismatch: ' + symbol)
    header = (ROOT / 'evidence/power-port/ack/drivers/pmdomain/mediatek/mtk-pm-domains.h').read_text().replace('\\\n', '')
    update = re.search(r'#define[ \t]+BUS_PROT_UPDATE\([^)]*\)([^\n]+)', header)[1]
    topaxi = re.search(r'#define[ \t]+BUS_PROT_INFRA_UPDATE_TOPAXI\([^)]*\)([^\n]+)', header)[1]
    if 'BUS_PROT_REG_UPDATE' not in update or 'IGNORE' in update or 'BUS_PROT_UPDATE(' not in topaxi:
        raise ValueError('Bus-protection flags require review')
    core = (ROOT / 'evidence/power-port/ack/drivers/pmdomain/mediatek/mtk-pm-domains.c').read_text()
    for helper in ['scpsys_bus_protect_set', 'scpsys_bus_protect_clear']:
        body = re.search(r'static int ' + helper + r'\(.*?\n\{(.*?)\n\}', core, re.S)[1]
        if 'return regmap_read_poll_timeout' not in body:
            raise ValueError('Bus-protection acknowledgement polling changed')
    return {'scope': __doc__, 'domains': rows,
            'shared_status_registers': {s: value(s, new_macros) for s in ['SPM_PWR_STATUS', 'SPM_PWR_STATUS_2ND']},
            'bus_protection_flags': 'Register-update path with set/clear acknowledgement polling; no ignore-clear-ack flag in MT8163 operations',
            'policy_differences': ['All eight legacy active-wakeup callbacks return true; candidate has no ACTIVE_WAKEUP capability. Suspend semantics require qualification.',
                                   'Legacy MFG owns the mfg clock; captured modern DT places it on MFG_ASYNC parent. Parent-before-child hierarchy remains, exact clock/power ordering is not equivalent proof.'],
            'error_handling_difference': 'Legacy ignores initial genpd power_on return; ACK propagates failed domain power_on and runs cleanup. Hardware state after partial failure is not qualified.',
            'probe_side_effects': ['ACK powers each available domain on during registration unless KEEP_DEFAULT_OFF; no MT8163 entry sets that capability.',
                                   'Pwrap enables clocks/DCM and may reset/reinitialize the wrapper/PMIC transport when INIT_DONE2 is clear.',
                                   'No MT8163 domain requests DOMAIN_SUPPLY; per-domain regulator control is absent. Other consumer supplies are separate.'],
            'runtime_qualified': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = audit()
    if args.check:
        if result != json.loads((EVIDENCE / 'report.json').read_text()):
            raise SystemExit('Power-domain contract changed; review source differences')
        print('PASS: eight IDs,32 domain fields, three nonzero bus masks and two status offsets; policy differences remain unqualified')
    else:
        print(json.dumps(result, indent=2))
