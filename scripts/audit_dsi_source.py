#!/usr/bin/env python3
"""Finite actual DSI source/ownership/packet audit; never qualify display operation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'evidence/dsi-source'


def function(source,name):
    m=re.search(r'^static (?:int|void) '+name+r'\(',source,re.M)
    if not m:raise ValueError('Missing actual DSI function '+name)
    b=source.index('{',m.start());end=b+1;depth=1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[m.start():end]


def audit():
    receipt=json.loads((E/'sources.json').read_text())
    for path,sha in receipt['sha256'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=sha:raise ValueError('Reviewed DSI input drift: '+path)
    ack=(E/'ack-mtk_dsi.c').read_text();donor=(E/'donor-mtk_dsi.c').read_text();legacy=(ROOT/'evidence/mipi-source/legacy-ddp_dsi.c').read_text();header=(ROOT/'evidence/mipi-source/legacy-ddp_reg.h').read_text()
    if '"mediatek,mt8163-dsi"' in ack or '"mediatek,mt8163-dsi"' not in donor:raise ValueError('Reviewed controller match premise changed')
    active_legacy=re.sub(r'/\*.*?\*/|//[^\n]*','',legacy,flags=re.S)
    if 'DSI_RACK_BYPASS' in active_legacy:raise ValueError('Active legacy bypass premise changed')
    for anchor in ['DISPSYS_DSI0_BASE + 0x200','DSI_REG[0]->DSI_INTEN, VM_DONE, 1']:
        if anchor not in active_legacy:raise ValueError('Legacy command/IRQ source anchor changed')
    if not re.search(r'struct DSI_CMDQ_REGS\s*\{\s*struct DSI_CMDQ data\[128\]',header):raise ValueError('Legacy queue capacity declaration changed')
    drm=(E/'mtk_drm_drv.c').read_text()
    if '"mediatek,mt8163-mmsys"' in drm or '"mediatek,mt8163-dsi"' in drm:raise ValueError('DRM master/component prerequisite changed')
    if 'of_id = of_match_node(mtk_drm_of_ids, phandle)' not in drm:raise ValueError('DRM master match ownership changed')
    descriptor=re.search(r'static const struct mtk_dsi_driver_data mt8163_dsi_driver_data = \{.*?\n};',donor,re.S).group()
    for anchor in ['.reg_cmdq_off = 0x200','.reg_vm_cmd_off = 0x130','.bypass_rack = true','.no_vm_done_irq = true']:
        if anchor not in descriptor:raise ValueError('Donor descriptor changed')
    # Retain actual packet enums/flags and controller macros, including continuations.
    enums='\n'.join(re.findall(r'^enum(?:\s+\w+)?\s*\{.*?^};',(E/'mipi_display.h').read_text(),re.M|re.S))
    definitions=[];lines=donor[:donor.index('struct mtk_phy_timing')].splitlines();i=0
    while i<len(lines):
        if lines[i].startswith('#define '):
            block=[lines[i]]
            while block[-1].endswith('\\'):
                i+=1;block.append(lines[i])
            definitions.append('\n'.join(block))
        i+=1
    flags='\n'.join(x for x in (E/'drm_mipi_dsi.h').read_text().splitlines() if x.startswith('#define MIPI_DSI_MSG_'))
    code=enums+'\n'+flags+'\n'+'\n'.join(definitions)+'\n'
    for name in ['mtk_dsi_mask','mtk_dsi_poweron','mtk_dsi_bridge_atomic_pre_enable','mtk_dsi_bridge_atomic_enable','mtk_dsi_bind','mtk_dsi_unbind']:
        code+=function(ack,name)+'\n'
    code+=function(donor,'mtk_dsi_poweron').replace('mtk_dsi_poweron(', 'donor_poweron(',1)+'\n'
    code+=re.search(r'static const struct component_ops mtk_dsi_component_ops = \{.*?\n};',ack,re.S).group()+'\n'
    for name in ['mtk_dsi_host_attach','mtk_dsi_host_detach','mtk_dsi_probe']:code+=function(ack,name)+'\n'
    code+=function(ack,'mtk_dsi_cmdq').replace('mtk_dsi_cmdq(', 'ack_cmdq(',1)+'\n'+function(donor,'mtk_dsi_cmdq').replace('mtk_dsi_cmdq(', 'donor_cmdq(',1)+'\n'
    fixture=(E/'ram.c.in').read_text().replace('/* ACTUAL_SOURCE */',code)
    with tempfile.TemporaryDirectory() as tmp:
        c=Path(tmp)/'ram.c';binary=Path(tmp)/'ram';c.write_text(fixture)
        r=subprocess.run(['cc','-std=gnu11','-Wall','-Werror','-fsanitize=address,undefined',str(c),'-o',str(binary)],capture_output=True,text=True)
        if r.returncode:raise ValueError('Actual DSI C RAM compile failed: '+r.stderr)
        subprocess.run([str(binary)],check=True)
    return {'scope':'Actual selected C/RAM witnesses and pinned source ownership; no hardware errors or whole display equivalence observed','passed':True,'invalid_format_reference_retained':True,'second_poweron_after_format_error_returns_success':True,'bridge_enable_can_follow_failed_format_with_nonzero_reference':True,'ack_and_donor_discard_phy_poweron_error':True,'encoder_created_before_failed_optional_reset_without_local_cleanup':True,'attach_callback_accepts_zero_lanes_with_mock_framework':True,'probe_failure_stages':9,'probe_host_irq_cleanup_observed':True,'component_registration_in_host_attach_not_probe':True,'legacy_cmdq_words':128,'queue_max_payload_source_bound':508,'payload509_crosses_legacy_queue_declaration':True,'payload1020_wraps_u8_cmdq_size_zero':True,'packet_mode_cases':12,'donor_non_lpm_sets_hstx_globally':True,'legacy_bypass_implementation_commented_out':True,'legacy_vm_done_enable_active':True,'master_mt8163_mmsys_match_present':False,'master_mt8163_dsi_component_match_present':False,'dsi_kernel_variant_implemented':False,'binding_admitted':False,'runtime_qualified':False}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args();r=audit()
    if a.check:
        if r!=json.loads((E/'result.json').read_text()):raise ValueError('DSI audit result drift')
    else:(E/'result.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2))


if __name__=='__main__':main()
