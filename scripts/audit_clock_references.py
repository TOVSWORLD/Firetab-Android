#!/usr/bin/env python3
"""Bounded textual clock-reference audit; not C/DT/schema/runtime validation."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / 'projects/firetabs-android/kernel/clock-port/overlay'



# #29: these captured DT consumers depend on unresolved aliases or the missing
# external CTS provider. Remove a restriction only with a reviewed provider/rate
# contract; do not silently accept a dummy parent to make the audit pass.
UNQUALIFIED_HDMI = frozenset({
    'CLK_TOP_HDMI_CTS', 'CLK_TOP_HDMI_CTS_D2', 'CLK_TOP_HDMI_CTS_D3',
    'CLK_TOP_HDMI_SEL', 'CLK_MM_HDMI_SPDIF', 'CLK_MM_HDMI_ADSP',
    'CLK_MM_HDMI_PLLCK',
})


def hdmi_policy(consumers):
    rejected = sorted({x['symbol'] for x in consumers} & UNQUALIFIED_HDMI)
    if rejected:
        raise ValueError('Unqualified HDMI clock consumer(s), resolve #29 provider/rate contract: '
                         + ', '.join(rejected))
    return {'decision': 'Dependent HDMI paths unavailable to captured literal DT consumers',
            'restricted_symbols': sorted(UNQUALIFIED_HDMI),
            'captured_restricted_consumers': [],
            'scope': 'Literal captured DT only; not expanded DT/C consumers or runtime proof'}


def audit():
    providers = []
    names, parents = set(), set()
    for driver in sorted((OVERLAY / 'drivers/clk/mediatek').glob('*.c')):
        source = driver.read_text()
        header = OVERLAY / 'include/dt-bindings/clock' / ('mediatek,' + driver.stem[4:] + '.h')
        definitions = {name: int(value) for name, value in re.findall(
            r'#define\s+(CLK_\w+)\s+(\d+)', header.read_text())}
        referenced = set(re.findall(r'\bCLK_[A-Z0-9_]+\b', source))
        missing = sorted(set(definitions) - referenced)
        if missing:
            raise SystemExit(f'{driver.name}: declared IDs not mentioned: {missing}')
        # Only literal constructor names/parents and explicit parent arrays.
        # This does not prove registration paths execute or consumer routing.
        for match in re.finditer(
                r'\b[A-Z][A-Z0-9_]*\(\s*CLK_[A-Z0-9_]+,\s*"([^"]+)"(?:,\s*"([^"]+)")?', source):
            names.add(match[1])
            if match[2]:
                parents.add(match[2])
        for array in re.findall(r'static const char \* const \w+\[\]\s*=\s*\{(.*?)\};', source, re.S):
            parents.update(re.findall(r'"([^"]+)"', array))
        providers.append({'driver': driver.name, 'numeric_header_definitions': len(definitions),
                          'declared_ids_not_mentioned_in_source': missing})
    dts = (ROOT / 'evidence/dtb-compile/inputs/arch/arm64/boot/dts/mediatek/mt8163.dtsi').read_text()
    external = set(re.findall(r'clock-output-names\s*=\s*"([^"]+)"', dts))
    # Explicit provider labels in the captured MT8163 DT, not arbitrary DTS parsing.
    provider_headers = {name: name for name in [
        'topckgen', 'infracfg', 'apmixedsys', 'mfgcfg', 'mmsys', 'imgsys', 'vdecsys', 'vencsys']}
    provider_headers['audiosys'] = 'audsys'
    consumers = []
    for path in sorted((ROOT / 'evidence/dtb-compile/inputs/arch/arm64/boot/dts/mediatek').glob('*.dts*')):
        for number, line in enumerate(path.read_text().splitlines(), 1):
            for provider, symbol in re.findall(r'&([a-zA-Z0-9_]+)\s+(CLK_[A-Z0-9_]+)', line):
                if provider not in provider_headers:
                    raise SystemExit(f'Unreviewed clock provider label: {provider}')
                header = OVERLAY / 'include/dt-bindings/clock' / (
                    'mediatek,mt8163-' + provider_headers[provider] + '.h')
                match = re.search(r'#define\s+' + re.escape(symbol) + r'\s+(\d+)\b', header.read_text())
                if not match:
                    raise SystemExit(f'{provider}: clock symbol absent from its header: {symbol}')
                consumers.append({'path': str(path.relative_to(ROOT)), 'line': number,
                                  'provider': provider, 'symbol': symbol, 'id': int(match[1])})
    unresolved = sorted(parents - names - external)
    return {'scope': __doc__, 'providers': providers,
            'board_external_clock_names': sorted(external),
            'unresolved_literal_parent_names': unresolved,
            'captured_literal_clock_consumers': consumers,
            'unqualified_hdmi_policy': hdmi_policy(consumers),
            'limitations': ['Textual identifier presence is not clock registration proof.',
                           'Only literal named clock consumers in captured DT files are checked; no exhaustive C/DT expansion, schema or register audit.',
                           'No clocks or hardware were exercised.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Compare with committed textual audit report')
    args = parser.parse_args()
    result = audit()
    if args.check:
        expected = json.loads((ROOT / 'evidence/clock-port/reference-audit.json').read_text())
        if result != expected:
            raise SystemExit('Clock reference report differs; review and regenerate')
        print(f"PASS: bounded audit of {len(result['providers'])} provider sources and {len(result['captured_literal_clock_consumers'])} literal DT clock references; unresolved HDMI parents remain recorded")
    else:
        print(json.dumps(result, indent=2))
