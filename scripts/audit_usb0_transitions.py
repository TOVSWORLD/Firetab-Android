#!/usr/bin/env python3
"""Finite pinned USB0 source-expression comparison; no MMIO or readiness grant."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'evidence/usb0-transition-review'


def active(source):
    return re.sub(r'/\*.*?\*/|//[^\n]*', '', source, flags=re.S)


def function(source, name):
    match = re.search(r'\b' + re.escape(name) + r'\([^;]*?\)\s*\{', source, re.S)
    if not match:
        raise ValueError('Missing function: ' + name)
    start = match.end(); depth = 1
    for end in range(start, len(source)):
        depth += (source[end] == '{') - (source[end] == '}')
        if not depth:
            return source[start:end]
    raise ValueError('Unterminated function: ' + name)


def compare_states(bits, old, new):
    equal = 0; difference = 0; first = None
    for state in range(1 << bits):
        left, right = old(state), new(state)
        equal += left == right
        difference |= left ^ right
        if left != right and first is None:
            first = {'initial': hex(state), 'legacy': hex(left), 'modern': hex(right)}
    return {'states': 1 << bits, 'equal': equal, 'difference_mask': hex(difference),
            'first_counterexample': first}


def audit():
    receipt = json.loads((EVIDENCE / 'inputs.json').read_text())
    for path, expected in receipt['inputs'].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError('Pinned source drift: ' + path)
    old = active((ROOT / 'evidence/usb-prerequisites/legacy/usb20_phy.c').read_text())
    phy = active((ROOT / 'evidence/usb-prerequisites/ack/phy-mtk-tphy.c').read_text())
    musb = active((ROOT / 'evidence/usb-prerequisites/ack/mediatek.c').read_text())
    # The first legacy definition is the empty FPGA stub; select the real branch.
    recover = function(old[old.index('#else', old.index('#ifdef FPGA_PLATFORM')):], 'usb_phy_recover')
    for token in ['USBPHY_CLR8(0x18, 0x08)', 'USBPHY_SET8(0x18, 0x06)',
                  'USBPHY_SET8(0x05, 0x77)', 'USBPHY_CLR8(0x6c, 0x10)',
                  'USBPHY_SET8(0x6c, 0x2E)', 'USBPHY_SET8(0x6d, 0x3E)']:
        if token not in recover:
            raise ValueError('Legacy active recovery expression drift: ' + token)
    for token in ['#define PA6_RG_U2_SQTH\t\tGENMASK(3, 0)',
                  '#define PA1_RG_VRT_SEL\t\t\tGENMASK(14, 12)',
                  '#define PA1_RG_TERM_SEL\t\tGENMASK(10, 8)',
                  'PA6_RG_U2_SQTH, 2)', 'if (instance->eye_vrt)', 'if (instance->eye_term)',
                  'tmp |= P2C_FORCE_IDDIG | P2C_RG_IDDIG',
                  'tmp &= ~(P2C_FORCE_IDDIG | P2C_RG_IDDIG)']:
        if token not in phy:
            raise ValueError('Modern expression drift: ' + token)
    for name, bit in [('FORCE_IDDIG', 9), ('RG_VBUSVALID', 5), ('RG_SESSEND', 4), ('RG_AVALID', 2), ('RG_IDDIG', 1)]:
        if not re.search(r'#define\s+P2C_' + name + r'\s+BIT\(' + str(bit) + r'\)', phy):
            raise ValueError('Role bit drift: ' + name)
    results = {
        'rx_threshold_recover_vs_init': compare_states(8, lambda x: (x & ~8) | 6, lambda x: (x & ~15) | 2),
        'eye_no_properties': compare_states(16, lambda x: x | 0x7700, lambda x: x),
        'eye_explicit_7_7_expression_only': compare_states(16, lambda x: x | 0x7700, lambda x: (x & ~0x7700) | 0x7700),
        'role_recover_vs_poweron_device': compare_states(16, lambda x: (x & ~0x10) | 0x3e2e,
                                                       lambda x: ((x | 0x24) & ~0x10) | 0x202),
        'role_recover_vs_poweron_otg': compare_states(16, lambda x: (x & ~0x10) | 0x3e2e,
                                                    lambda x: ((x | 0x24) & ~0x10) & ~0x202),
    }
    clock = function(old[old.index('#else', old.index('#ifdef FPGA_PLATFORM')):], 'usb_enable_clock')
    probe = active((EVIDENCE / 'legacy-clock-probe.c').read_text())
    if any('devm_clk_get(&pdev->dev, "' + n + '")' not in probe for n in ['usbpll', 'usb', 'usbmcu', 'icusb']):
        raise ValueError('Legacy CCF prepare prerequisites drift')
    if 'clk_enable(icusb_clk)' in old or 'clk_disable(icusb_clk)' in old:
        raise ValueError('Legacy ICUSB enable ownership changed')
    if 'enable_clock(MT_CG_INFRA_ICUSB' not in clock or 'clk_enable(usb_clk)' not in clock:
        raise ValueError('Legacy CLKMGR/CCF branch drift')
    for token in ['clk_bulk_prepare_enable(MTK_MUSB_CLKS_NUM, glue->clks)',
                  'phy_init(glue->phy)', 'phy_power_on(glue->phy)', 'phy_set_mode(glue->phy, glue->phy_mode)']:
        if token not in musb:
            raise ValueError('Modern clock/callback ownership drift')
    graph = json.loads((ROOT / 'evidence/usb-prerequisites/candidate-graph.json').read_text())['nodes']
    if graph['controller']['dr_mode'] != ['otg'] or graph['port0']['clocks'] != [22, 14]:
        raise ValueError('Reviewed candidate role/reference drift')
    props = json.loads((EVIDENCE / 'port0-properties.json').read_text())
    if any('mediatek,eye-' in p for p in props['properties']):
        raise ValueError('Candidate tuning metadata changed')
    return {'scope': 'Pinned isolated source expressions/ownership only; not sequence or hardware equivalence',
            'comparisons': results,
            'legacy_ccf_prepare_names': ['usbpll', 'usb', 'usbmcu', 'icusb'],
            'legacy_ccf_first_enable_order': ['usbpll', 'usb', 'usbmcu'],
            'legacy_clkmgr_icusb_gate_is_separate_branch': True,
            'modern_musb_bulk_names': ['main', 'mcu', 'univpll'],
            'modern_phy_optional_bulk_names': ['ref', 'da_ref'],
            'candidate_port0_ref': 'apmixedsys CLK_APMIXED_REF2USB_TX (14); separate from UNIVPLL (2)',
            'activation_allowed': False, 'device_tested': False,
            'next_source_acceptance': 'Select MT8163-specific RX/eye policy and device-role force-bit ownership, then implement only justified changes with RAM mocks and exact-head USB build; retain disabled DT and runtime gates.'}


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
