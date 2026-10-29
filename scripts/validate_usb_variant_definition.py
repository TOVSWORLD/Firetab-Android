#!/usr/bin/env python3
"""Finite source bitvector/resource definition checks; no MMIO or hardware proof."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from audit_usb_prerequisites import source_facts,EVIDENCE
ROOT=Path(__file__).resolve().parents[1]
DEFINITION=ROOT/'projects/firetabs-android/kernel/usb-port/variant-definition.json'


def legacy_byte(state):
    return (state & ~0xff00) | 0x6000


def ack_field(state,calibration_completed):
    # ACK init clears HS_100U; explicit eye-src6 skips measurement/oscillator clear.
    result=((state & ~0x7000) | 0x6000) & ~(1<<11)
    return result & ~(1<<15) if calibration_completed else result


def validate_resources(resources):
    if len({r['name'] for r in resources})!=len(resources):raise ValueError('Duplicate resource names')
    for r in resources:
        if type(r['start']) is not int or type(r['length']) is not int or r['start']<0 or r['length']<=0:
            raise ValueError('Invalid interval')
    for a,b in itertools.combinations(resources,2):
        if a['start']<b['start']+b['length'] and b['start']<a['start']+a['length']:
            raise ValueError('Overlapping ownership: '+a['name']+'/'+b['name'])
    return {r['name']:r for r in resources}


def validate(definition):
    facts=source_facts()
    helper_path=ROOT/'evidence/usb-variant-definition/phy-mtk-io.h'
    helper_receipt=json.loads((helper_path.parent/'helper-source.json').read_text())
    if hashlib.sha256(helper_path.read_bytes()).hexdigest()!=helper_receipt['sha256']:raise ValueError('RMW helper source drift')
    helper=helper_path.read_text()
    assert 'tmp &= ~mask;' in helper and 'tmp |= val & mask;' in helper
    assert 'mtk_phy_update_bits(reg, mask, FIELD_PREP(mask, val));' in helper
    assert 'tmp &= ~bits;' in helper
    source=(EVIDENCE/'ack/phy-mtk-tphy.c').read_text()
    legacy=(EVIDENCE/'legacy/usb20_phy.c').read_text()
    assert 'if (instance->eye_src || !tphy->src_ref_clk || !tphy->src_coef)' in source
    assert 'PA5_RG_U2_HSTX_SRCTRL\t\tGENMASK(14, 12)' in source
    assert 'PA5_RG_U2_HS_100U_U3_EN\tBIT(11)' in source
    assert 'PA5_RG_U2_HSTX_SRCAL_EN\tBIT(15)' in source
    assert 'readl_poll_timeout(fmreg + U3P_U2FREQ_FMMONR1, tmp,' in source
    assert '(tmp & P2F_USB_FM_VALID), 10, 200)' in source
    assert 'timeout = jiffies + 3 * HZ' in legacy
    assert 'devm_ioremap_resource(dev, sif_res)' in source
    assert 'devm_ioremap_resource(subdev, &res)' in source
    if definition['compatible']!='mediatek,mt8163-tphy' or definition['allowed_phy_types']!=[3]:raise ValueError('Unreviewed variant/type')
    r=validate_resources(definition['resources'])
    expected={'sif':(0x11210000,0x800,'parent'),'u2-frequency':(0x11210f00,0x100,'parent'),
              'port0':(0x11210800,0x100,'child0'),'port1':(0x11210900,0x100,'child1')}
    if set(r)!=set(expected):raise ValueError('Missing or extra resource')
    for name,(start,length,owner) in expected.items():
        if (r[name]['start'],r[name]['length'],r[name]['owner'])!=(start,length,owner):raise ValueError('Source resource drift: '+name)
    f=definition['frequency_bank'];s=definition['slew_policy']
    if f['resource']!='u2-frequency' or f['value_offset']!=12 or f['monitor_offset']!=16 or f['control_offset']!=0 or f['access_width']!=4 or f['cycle_count']!=1024 or f['timeout_us']!=3000000:
        raise ValueError('Frequency policy drift')
    if max(f['value_offset'],f['monitor_offset'],f['control_offset'])+f['access_width']>r[f['resource']]['length']:raise ValueError('Frequency access outside owned resource')
    if s['kind']!='measure_then_vendor_fixed_byte' or s['byte_offset']!=0x15 or s['byte_value']!=0x60 or s['field_mask']!=0x7000 or s['field_value']!=6 or s['oscillator_mask']!=0x8000 or s['measurement_required'] is not True:
        raise ValueError('Applied-byte/measurement policy drift')
    if s['timeout_action']!='cleanup_then_fixed_byte' or s['zero_measurement_action']!='cleanup_then_fixed_byte' or s['explicit_eye_override_action']!='reject':raise ValueError('Unqualified shortcut/error policy')
    if any(definition[k] is not False for k in ['candidate_enable_allowed','kernel_implementation_complete','build_integration_verified','runtime_qualified','non_mt8163_changes_allowed']):raise ValueError('Unqualified readiness promotion')
    counts={'calibrated_field_hypothesis_equal':0,'eye_src6_shortcut_equal':0};masks={'calibrated_field_hypothesis':0,'eye_src6_shortcut':0}
    for state in range(65536):
        old=legacy_byte(state)
        for name,completed in [('calibrated_field_hypothesis',True),('eye_src6_shortcut',False)]:
            new=ack_field(state,completed)
            counts[name+'_equal']+=old==new
            masks[name]|=old^new
    assert counts=={'calibrated_field_hypothesis_equal':8192,'eye_src6_shortcut_equal':4096}
    assert masks=={'calibrated_field_hypothesis':0x700,'eye_src6_shortcut':0x8700}
    return {'scope':'Exhaustive isolated 16-bit source expressions and interval ownership only; not whole PHY behavior',
            'states_checked':65536,'equal_counts':counts,'difference_masks':{k:hex(v) for k,v in masks.items()},
            'counterexample':{'initial':'0x8700','legacy':hex(legacy_byte(0x8700)),
                             'field_after_measurement':hex(ack_field(0x8700,True)),
                             'eye_src6_shortcut':hex(ack_field(0x8700,False))},
            'field6_is_not_byte_write_equivalence':True,'fixed_eye_shortcut_not_selected':True,
            'resource_intervals_disjoint':True,'frequency_value_address':hex(r['u2-frequency']['start']+f['value_offset']),
            'ack_current_timeout_us':200,'legacy_deadline':'3*HZ; selected definition converts intent to3000000us, not exact scheduling equivalence',
            'candidate_unchanged':True,'kernel_implementation_complete':False,'build_integration_verified':False,'runtime_qualified':False}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('definition',nargs='?',type=Path,default=DEFINITION);args=p.parse_args()
    result=validate(json.loads(args.definition.read_text()));result['definition_sha256']=hashlib.sha256(args.definition.read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
