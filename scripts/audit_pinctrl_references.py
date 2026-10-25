#!/usr/bin/env python3
"""Compare captured MT8163 pin tables and literal DT mux references; no hardware tests."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PORT = ROOT / 'projects/firetabs-android/kernel/pinctrl-port/overlay'


def table(text):
    result = {}
    for block in re.split(r'\bMTK_PIN\(', text)[1:]:
        pin = re.search(r'PINCTRL_PIN\((\d+),\s*"([^"]+)"\)', block)
        if pin:
            if pin[1] in result:
                raise SystemExit('Duplicate pin descriptor')
            result[pin[1]] = {
                'name': pin[2],
                'eint': re.search(r'MTK_EINT_FUNCTION\(([^)]+)\)', block)[1],
                'functions': dict(re.findall(r'MTK_FUNCTION\((\d+),\s*"([^"]+)"\)', block))}
    if set(result) != {str(x) for x in range(155)}:
        raise SystemExit('Unexpected pin range')
    return result


def audit():
    rel = Path('drivers/pinctrl/mediatek/pinctrl-mtk-mt8163.h')
    candidate = table((PORT / rel).read_text())
    legacy = table((ROOT / 'evidence/pinctrl-port/legacy' / rel).read_text())
    if candidate != legacy:
        raise SystemExit('Donor and captured legacy pin descriptors differ')
    header = (PORT / 'include/dt-bindings/pinctrl/mt8163-pinfunc.h').read_text()
    definitions = {key: (pin, function) for key, pin, function in re.findall(
        r'#define\s+(MT8163_PIN_\w+)\s+\(MTK_PIN_NO\((\d+)\)\s*\|\s*(\d+)\)', header)}
    consumers = {}
    for path in sorted((ROOT / 'evidence/dtb-compile/inputs/arch/arm64/boot/dts/mediatek').glob('*.dts*')):
        for symbol in re.findall(r'\bMT8163_PIN_[A-Z0-9_]+\b', path.read_text()):
            pin, function = definitions[symbol]
            consumers[symbol] = {'pin': int(pin), 'function': int(function),
                                 'driver_function': candidate[pin]['functions'][function]}
    return {'scope': __doc__, 'identical_legacy_descriptor_count': len(candidate),
            'unique_literal_dt_pin_functions': consumers,
            'legacy_goodix_gpio_descriptors': {n: candidate[n] for n in ['35', '46']},
            'limitations': ['No full preprocessor/schema validation or electrical routing test.',
                           'A GPIO number and its EINT line are distinct identifiers.',
                           'No interrupt/drive-strength/debounce behavior was measured.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = audit()
    if args.check:
        expected = json.loads((ROOT / 'evidence/pinctrl-port/reference-audit.json').read_text())
        if result != expected:
            raise SystemExit('Pinctrl report changed; review before regenerating')
        print('PASS: 155 legacy pin descriptors match; 15 unique literal DT mux references checked')
    else:
        print(json.dumps(result, indent=2))
