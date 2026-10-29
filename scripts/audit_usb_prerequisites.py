#!/usr/bin/env python3
"""Audit pinned USB source/candidate prerequisites without granting transport readiness."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from validate_iommu_dependencies import clock_id

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'evidence/usb-prerequisites'
PATHS={'controller':'/soc/usb@11200000','phy':'/soc/t-phy@11210000',
       'port0':'/soc/t-phy@11210000/usb-phy@11210800',
       'port1':'/soc/t-phy@11210000/usb-phy@11210900',
       'infra':'/soc/clock-controller@10001000','apmixed':'/soc/clock-controller@1000c000'}


def source_facts():
    receipt=json.loads((EVIDENCE/'sources.json').read_text())
    for entry in receipt['ack']:
        if hashlib.sha256((ROOT/entry['local']).read_bytes()).hexdigest()!=entry['sha256']:
            raise ValueError('ACK source hash drift')
    for entry in receipt['legacy']:
        if hashlib.sha256((ROOT/entry['local']).read_bytes()).hexdigest()!=entry['retained_sha256']:
            raise ValueError('Legacy source receipt drift')
    musb=(EVIDENCE/'ack/mediatek.c').read_text()
    phy=(EVIDENCE/'ack/phy-mtk-tphy.c').read_text()
    legacy=(EVIDENCE/'legacy/usb20_phy.c').read_text()
    header=(EVIDENCE/'legacy/mtk_musb.h').read_text()
    assert '{.compatible = "mediatek,mtk-musb",}' in musb
    assert '"mediatek,generic-tphy-v1", .data = &tphy_v1_pdata' in phy
    assert all('id = "'+name+'"' in musb for name in ['main','mcu','univpll'])
    assert 'devm_of_phy_get_by_index(dev, np, 0)' in musb
    assert 'devm_clk_bulk_get_optional(subdev, TPHY_CLKS_CNT, clks)' in phy
    assert 'u2_banks->fmreg = tphy->sif_base + SSUSB_SIFSLV_V1_U2FREQ' in phy
    bank=int(re.search(r'#define\s+SSUSB_SIFSLV_V1_U2FREQ\s+(0x[0-9a-f]+)',phy)[1],16)
    value=int(re.search(r'#define\s+U3P_U2FREQ_VALUE\s+(0x[0-9a-f]+)',phy)[1],16)
    pdata=re.search(r'tphy_v1_pdata = \{(.*?)\};',phy,re.S)[1]
    ref=int(re.search(r'\.slew_ref_clock_mhz\s*=\s*(\d+)',pdata)[1])
    old_ref=int(re.search(r'#define\s+FRA\s+\((\d+)\)',legacy)[1])
    assert 'USBPHY_READ32(0xf00-0x800+0x0c)' in legacy
    active_legacy=re.sub(r'/\*.*?\*/|//[^\n]*', '', legacy, flags=re.S)
    assert 'USBPHY_WRITE8(0x15, 0x60)' in active_legacy
    assert 'USBPHY_WRITE8(0x15, value<<4)' not in active_legacy
    assert 'io_priv)+0x800+offset' in header
    assert 'pbase = of_iomap(pdev->dev.of_node, 1)' in (EVIDENCE/'legacy/probe-and-base.c').read_text()
    assert 'musb->xceiv->io_priv = ctrlp' in (EVIDENCE/'legacy/io-priv-assignment.c').read_text()
    assert '<0 0x11210000 0 0x10000>' in (EVIDENCE/'legacy/usb-resource.dtsi').read_text()
    return {'ack_v1_frequency_bank_offset':bank,'frequency_value_offset':value,
            'legacy_frequency_bank_offset':0xf00,'ack_v1_default_ref_mhz':ref,
            'legacy_formula_ref':old_ref,'legacy_applies_computed_slew':False,
            'legacy_fixed_slew_byte':0x60,'controller_fallback':'mediatek,mtk-musb',
            'phy_fallback':'mediatek,generic-tphy-v1'}


def capture(tool,dtb):
    def node(path):
        props=subprocess.check_output([str(tool),'-p',str(dtb),path],text=True,timeout=15).split();n={}
        for prop in ['compatible','reg','interrupts','interrupt-names','phys','dr_mode','clocks','clock-names','status','#phy-cells','#clock-cells','phandle']:
            if prop not in props:continue
            strings=prop in ['compatible','interrupt-names','dr_mode','clock-names','status']
            v=subprocess.check_output([str(tool),'-ts' if strings else '-tx',str(dtb),path,prop],text=True,timeout=15).split()
            n[prop]=v if strings else [int(x,16) for x in v]
        return n
    return {'nodes':{role:node(path) for role,path in PATHS.items()}}


def audit(graph):
    facts=source_facts();n=graph['nodes'];c=n['controller'];p=n['phy'];infra=n['infra'];ap=n['apmixed']
    if c.get('compatible')!=['mediatek,mt8163-musb',facts['controller_fallback']] or p.get('compatible')!=['mediatek,mt8163-tphy',facts['phy_fallback']]:
        raise ValueError('Actual reviewed fallback selection changed')
    if c.get('status')!=['disabled'] or p.get('status')!=['disabled']:
        raise ValueError('Unqualified USB activation requires a new reviewed variant/build scope')
    if c.get('reg')!=[0,0x11200000,0,4096] or p.get('reg')!=[0,0x11210000,0,2048]:raise ValueError('Reviewed USB resources drifted')
    if c.get('interrupts')!=[0,72,8] or c.get('interrupt-names')!=['mc']:raise ValueError('Controller IRQ metadata drift')
    if c.get('dr_mode')!=['otg']:raise ValueError('Reviewed mode metadata drift')
    if infra.get('compatible')!=['mediatek,mt8163-infracfg','syscon'] or ap.get('compatible')!=['mediatek,mt8163-apmixedsys']:
        raise ValueError('Wrong clock suppliers')
    if infra.get('#clock-cells')!=[1] or ap.get('#clock-cells')!=[1]:raise ValueError('Clock supplier argument drift')
    ip=infra['phandle'][0];a=ap['phandle'][0]
    expected=[ip,clock_id('infracfg','CLK_INFRA_USB'),ip,clock_id('infracfg','CLK_INFRA_USB_MCU'),a,clock_id('apmixedsys','CLK_APMIXED_UNIVPLL')]
    if c.get('clock-names')!=['main','mcu','univpll'] or c.get('clocks')!=expected:raise ValueError('Controller clock role/provider/ID drift')
    for i in range(2):
        port=n['port'+str(i)]
        if port.get('reg')!=[0,0x11210800+i*256,0,256] or port.get('#phy-cells')!=[1]:raise ValueError('PHY port resource/argument drift')
        if port.get('clock-names')!=['ref'] or port.get('clocks')!=[a,clock_id('apmixedsys','CLK_APMIXED_REF2USB_TX')]:raise ValueError('PHY reference supplier drift')
    if n['port0']['phandle']==n['port1']['phandle'] or c.get('phys')!=n['port0']['phandle']+[3]:raise ValueError('Controller must link port0/USB2')
    fragment=(ROOT/'projects/firetabs-android/kernel/diagnostic/fragment.config').read_text()
    disabled=all('# CONFIG_'+symbol+' is not set' in fragment for symbol in ['USB','USB_GADGET'])
    base=p['reg'][1];new=base+facts['ack_v1_frequency_bank_offset']+facts['frequency_value_offset'];old=base+facts['legacy_frequency_bank_offset']+facts['frequency_value_offset']
    return {'scope':'Pinned source/declared candidate prerequisites only; no USB compilation or runtime claim',
            'declaration_contract_passed':True,'source_facts':facts,
            'source_derived_frequency_value_addresses':{'ack_generic_v1':hex(new),'legacy_declared_sif':hex(old)},
            'same_frequency_bank':new==old,'candidate_controller_enabled':False,'candidate_phy_enabled':False,
            'diagnostic_fragment_requests_usb_disabled':disabled,'source_variant_qualified':False,
            'usb_build_integration_verified':False,'device_transport_qualified':False,
            'full_binding_validation_passed':False,'runtime_qualified':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('graph',type=Path,nargs='?');parser.add_argument('--dtb',type=Path)
    parser.add_argument('--fdtget',type=Path,default=ROOT/'work/dtb-tool/build/fdtget');args=parser.parse_args()
    if bool(args.graph)==bool(args.dtb):parser.error('Choose graph or --dtb')
    graph=capture(args.fdtget,args.dtb) if args.dtb else json.loads(args.graph.read_text());result=audit(graph)
    if args.dtb:result['dtb_sha256']=hashlib.sha256(args.dtb.read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
