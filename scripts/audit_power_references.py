#!/usr/bin/env python3
"""Compare named PMIC wrapper register offsets; no runtime power qualification."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def audit():
    legacy = (ROOT / 'evidence/power-port/legacy/drivers/misc/mediatek/pmic_wrap/mt8163/pwrap_hal.h').read_text()
    source = (ROOT / 'evidence/power-port/donor/drivers/soc/mediatek/mtk-pmic-wrap.c').read_text()
    old = {name: int(offset, 16) for name, offset in re.findall(
        r'#define\s+PMIC_WRAP_(\w+)\s+\(\(PMIC_WRAP_BASE\s*\+\s*(0x[0-9a-fA-F]+)', legacy)}
    block = re.search(r'static const int mt8163_regs\[\]\s*=\s*\{(.*?)\n\};', source, re.S)[1]
    candidate = {name: int(offset, 16) for name, offset in re.findall(
        r'\[PWRAP_(\w+)\]\s*=\s*(0x[0-9a-fA-F]+)', block)}
    shared = sorted(old.keys() & candidate.keys())
    mismatches = [{'name': name, 'legacy': old[name], 'candidate': candidate[name]}
                  for name in shared if old[name] != candidate[name]]
    if mismatches:
        raise SystemExit(f'Wrapper register offset differences require review: {mismatches}')
    return {'scope': 'Static register offsets only; no transaction, initialization, voltage or power-sequencing validation',
            'shared_named_registers': len(shared), 'mismatches': mismatches,
            'candidate_only_named_registers': sorted(candidate.keys() - old.keys()),
            'legacy_only_named_registers': sorted(old.keys() - candidate.keys())}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    report = audit()
    if args.check:
        expected = json.loads((ROOT / 'evidence/power-port/pwrap-register-audit.json').read_text())
        if report != expected:
            raise SystemExit('Power register audit changed; review before regenerating')
        print(f"PASS: {report['shared_named_registers']} shared named PMIC wrapper offsets match legacy")
    else:
        print(json.dumps(report, indent=2))
