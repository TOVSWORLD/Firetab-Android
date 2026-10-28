#!/usr/bin/env python3
"""Bounded literal transition/clock trace; never execute power or device operations."""
import argparse
import itertools
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'evidence/power-port/transition-order'
FIELDS = r'PWR_(?:ON|ON_2ND|ISO|CLK_DIS|RST_B)_BIT'


def body(text, name):
    match = re.search(r'static (?:int|bool|void) ' + re.escape(name) + r'\([^)]*\)\s*\{(.*?)\n\}', text, re.S)
    if not match:
        raise ValueError('Missing reviewed function: ' + name)
    return match[1].split('\n\treturn 0;')[0]


def writes(text, style):
    if style == 'legacy':
        return [('clear:' if op == '&=' and inverse else 'set:') + field for op, inverse, field in
                re.findall(r'val\s*(\|=|&=)\s*(~?)\s*(' + FIELDS + r')\s*;', text)]
    return [op + ':' + field for op, field in re.findall(
        r'regmap_(set|clear)_bits\(scpsys->base,\s*pd->data->ctl_offs,\s*(' + FIELDS + r')\)', text)]


def mux_contract(old, new):
    def mux(text):
        match = re.search(r'MUX(?:_GATE)?_UPD\(CLK_TOP_MFG_SEL,\s*"mfg_sel",\s*mfg_parents,\s*([^)]*)\)', text, re.S)
        if not match:
            raise ValueError('Missing MFG mux definition')
        return [int(x.strip(), 0) for x in match[1].split(',')]
    def parents(text):
        match = re.search(r'mfg_parents\[\][^=]*=\s*\{(.*?)\}', text, re.S)
        return re.findall(r'"([^"]+)"', match[1])
    aliases = {name:(parent,int(mult),int(div)) for name,parent,mult,div in re.findall(
        r'FACTOR\([^,]+,\s*"([^"]+)",\s*"([^"]+)",\s*(\d+),\s*(\d+)\)',old)}
    resolved=[]
    for name in parents(old):
        if name in aliases:
            target,mult,div=aliases[name]
            if (mult,div)!=(1,1):raise ValueError('MFG parent alias is not one-to-one')
            name=target
        resolved.append(name)
    if mux(old)!=mux(new) or resolved!=parents(new):
        raise ValueError('MFG mux fields or alias-resolved parent identities differ')
    return {'register_fields':mux(new),'legacy_parent_names':parents(old),
            'candidate_parent_names':parents(new),'legacy_aliases_resolve_to_candidate':True,
            'clock_rates_measured':False}


def legacy_resume_needed(can_wake, may_wake, active):
    return False if not can_wake else active if may_wake else not active


def legacy_noirq_skip(suspend_power_off, wakeup_path, active):
    return suspend_power_off or (wakeup_path and active)


def audit():
    old=(ROOT/'evidence/power-port/domain-contract/legacy-scpsys.c').read_text()
    new=(ROOT/'evidence/power-port/ack/drivers/pmdomain/mediatek/mtk-pm-domains.c').read_text()
    on_old,off_old=body(old,'scpsys_power_on'),body(old,'scpsys_power_off')
    on_new,off_new=body(new,'scpsys_ctl_pwrseq_on'),body(new,'scpsys_ctl_pwrseq_off')
    if on_old.index('clk_prepare_enable') > on_old.index('val |= PWR_ON_BIT'):
        raise ValueError('Legacy basic clock is no longer before domain-on')
    if off_old.index('clk_disable_unprepare') < off_old.index('val &= ~PWR_ON_2ND_BIT'):
        raise ValueError('Legacy basic clock disabled before domain-off request')
    common_on,common_off=body(new,'scpsys_power_on'),body(new,'scpsys_power_off')
    if common_on.index('clk_bulk_prepare_enable(pd->num_clks') > common_on.index('scpsys_ctl_pwrseq_on'):
        raise ValueError('ACK basic clock no longer precedes power sequence')
    if common_off.index('clk_bulk_disable_unprepare(pd->num_clks') < common_off.index('readx_poll_timeout(scpsys_domain_is_on'):
        raise ValueError('ACK basic clock disabled before off acknowledgement')
    core=(EVIDENCE/'legacy-genpd.c').read_text()
    resume=''.join(body(core,'resume_needed').split())
    suspend=''.join(body(core,'pm_genpd_suspend_noirq').split())
    resume_noirq=''.join(body(core,'pm_genpd_resume_noirq').split())
    if 'returndevice_may_wakeup(dev)?active_wakeup:!active_wakeup;' not in resume or '!device_can_wakeup(dev)' not in resume:
        raise ValueError('Legacy resume predicate changed; rederive model')
    predicate='genpd->suspend_power_off||(dev->power.wakeup_path&&genpd_dev_active_wakeup(genpd,dev))'
    if predicate not in suspend or predicate not in resume_noirq:
        raise ValueError('Legacy noirq predicate changed; rederive model')
    legacy_clock=(ROOT/'evidence/kernel-audit/legacy/drivers/clk/mediatek/clk-mt8163.c').read_text()
    candidate_clock=(ROOT/'projects/firetabs-android/kernel/clock-port/overlay/drivers/clk/mediatek/clk-mt8163-topckgen.c').read_text()
    legacy_header=(EVIDENCE/'legacy-clock.h').read_text()
    candidate_header=(ROOT/'projects/firetabs-android/kernel/clock-port/overlay/include/dt-bindings/clock/mediatek,mt8163-topckgen.h').read_text()
    ids=lambda h:{name:int(re.search(r'#define\s+CLK_TOP_'+name+r'_SEL\s+(\d+)',h)[1]) for name in ['MFG','MM']}
    candidate_symbols={int(v):k for k,v in re.findall(r'#define\s+(CLK_TOP_\w+)\s+(\d+)',candidate_header)}
    stock=json.loads((EVIDENCE/'observed-stock-clock-abi.json').read_text())['observation']
    cells=stock['scpsys_clock_cells'];phandle=stock['topckgen_phandle']
    if stock['scpsys_clock_names'] != ['mfg','mm'] or stock['topckgen_compatible'] != ['mediatek,mt8163-topckgen'] or stock['topckgen_clock_cells'] != [1]:
        raise ValueError('Observed stock clock names/provider/cell shape changed')
    if cells != [phandle,ids(legacy_header)['MFG'],phandle,ids(legacy_header)['MM']]:
        raise ValueError('Observed stock clock cells do not match reviewed legacy names/IDs')
    candidate_node=json.loads((ROOT/'evidence/scpsys-binding/captured-node.json').read_text())['power-controller']['power-domain@6']
    if candidate_node.get('clock-names')!=['mfg'] or candidate_node['power-domain@7'].get('clocks'):
        raise ValueError('Candidate MFG clock ownership changed; review ordering')
    old_mfg=re.search(r'\[MT8163_POWER_DOMAIN_MFG\]\s*=\s*\{(.*?)\n\t\}',old,re.S)[1]
    if '.clk_id = {MT8163_CLK_MFG}' not in old_mfg:
        raise ValueError('Legacy MFG clock ownership changed')
    old_dts=(EVIDENCE/'legacy-mt8163.dtsi').read_text()
    if not re.search(r'clocks\s*=\s*<&topckgen CLK_TOP_MFG_SEL>,\s*<&topckgen CLK_TOP_MM_SEL>;\s*clock-names\s*=\s*"mfg", "mm";',old_dts):
        raise ValueError('Legacy provider-to-name pairing changed')
    return {'scope':__doc__,'normal_non_modem_non_rtff_success_path_only':True,
            'control_writes':{'legacy_on':writes(on_old,'legacy'),'ack_on':writes(on_new,'ack'),
                              'legacy_off':writes(off_old,'legacy'),'ack_off':writes(off_new,'ack')},
            'clock_owner':{'legacy':'MFG domain','candidate':'MFG_ASYNC parent','same_lifetime_proven':False},
            'mux_definition':mux_contract(legacy_clock,candidate_clock),
            'clock_abi':{'legacy_source_and_observed_stock':ids(legacy_header),'candidate':ids(candidate_header),
                         'candidate_meaning_of_stock_numeric_ids':{k:candidate_symbols[v] for k,v in ids(legacy_header).items()},
                         'stock_cells_are_not_candidate_ids':True,'loader_matching_dtb_required':True,
                         'experimental_dtb_handoff_observed':False},
            'legacy_resume_model':[{'can_wake':c,'may_wake':m,'active_callback':a,'resume_needed':legacy_resume_needed(c,m,a)} for c,m,a in itertools.product([False,True],repeat=3)],
            'legacy_noirq_model':[{'suspend_power_off':s,'wakeup_path':w,'active_callback':a,'skip_stop_start':legacy_noirq_skip(s,w,a)} for s,w,a in itertools.product([False,True],repeat=3)],
            'wakeup_qualification':{'legacy_predicates_source_checked':True,'python_boolean_model_not_kernel_execution':True,
                                    'ack_header_contract':'ACTIVE_WAKEUP requests domain retention for attached wakeup-path devices',
                                    'ack_genpd_implementation_acquired':False,'capability_change_justified':False},
            'limits':['Power-off reset/clock-disable and ON/ON_2ND ordering differs; no MMIO equivalence claim.',
                      'Same mux fields and one-to-one alias parents do not measure rates or transition timing.',
                      'Do not substitute stock DTB for matching candidate; actual loading/return/log gates remain open.'],
            'hardware_transition_tested':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args();result=audit()
    if args.check:
        if result!=json.loads((EVIDENCE/'report.json').read_text()):raise SystemExit('Transition audit changed; review before regenerating')
        print('PASS: literal power/clock trace and stock/candidate clock ABI checked; wakeup implementation and runtime remain unqualified')
    else:print(json.dumps(result,indent=2))
