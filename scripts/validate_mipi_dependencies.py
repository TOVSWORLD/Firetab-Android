#!/usr/bin/env python3
"""Check fresh disabled-board MIPI metadata against compiled source; no PHY admission."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
from compare_pmic_dtb import snapshot
ROOT=Path(__file__).resolve().parents[1]
PHY='/soc/dsi-phy@10215000';DSI='/soc/dsi@14012000'


def validate(graph):
    contract=json.loads((ROOT/'evidence/mipi-binding/source-contract.json').read_text())
    for path,sha in contract['sha256'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=sha:raise ValueError('Reviewed MIPI source/build input drift: '+path)
    nodes=graph['nodes'];node=nodes[PHY];consumer=nodes[DSI]
    for key,value in [('compatible',['mediatek,mt8163-mipi-tx']),('reg',[0,0x10215000,0,0x1000]),('#clock-cells',[0]),('#phy-cells',[0]),('status',['disabled']),('clock-output-names',['mipi_tx0_pll'])]:
        if node.get(key)!=value:raise ValueError('Wrong reviewed MIPI '+key)
    if node['reg'][3]<0x6c:raise ValueError('MIPI extent below source bound')
    if any(p in node for p in ['nvmem-cells','nvmem-cell-names','drive-strength-microamp','assigned-clocks','assigned-clock-parents','assigned-clock-rates']):raise ValueError('Unqualified MIPI override')
    phandles={}
    for path,n in nodes.items():
        if 'phandle' not in n:continue
        value=n['phandle']
        if len(value)!=1 or type(value[0]) is not int or not 0<value[0]<0xffffffff or value[0] in phandles:raise ValueError('Invalid/duplicate phandle')
        phandles[value[0]]=path
    clocks=node.get('clocks',[]);resets=node.get('resets',[])
    if len(clocks)!=2 or phandles.get(clocks[0])!='/soc/clock-controller@1000c000' or clocks[1]!=13:raise ValueError('Wrong MIPI reference provider/ID')
    clock=nodes[phandles[clocks[0]]]
    if clock.get('compatible')!=['mediatek,mt8163-apmixedsys'] or clock.get('#clock-cells')!=[1]:raise ValueError('Wrong reference provider type')
    if len(resets)!=2 or phandles.get(resets[0])!='/soc/clock-controller@10001000' or resets[1]!=10:raise ValueError('Wrong MIPI reset provider/ID')
    reset=nodes[phandles[resets[0]]]
    if reset.get('compatible')!=['mediatek,mt8163-infracfg','syscon'] or reset.get('#reset-cells')!=[1]:raise ValueError('Wrong reset provider type')
    for provider in [clock,reset]:
        if provider.get('status') not in [None,['okay'],['ok']]:raise ValueError('Disabled MIPI source provider')
    osc=nodes['/clocks/oscillator-26m']
    if osc.get('clock-frequency')!=[26000000] or osc.get('compatible')!=['fixed-clock'] or osc.get('#clock-cells')!=[0] or osc.get('clock-output-names')!=['clk26m'] or osc.get('status') not in [None,['okay'],['ok']]:raise ValueError('Wrong fixed reference declaration')
    if consumer.get('compatible')!=['mediatek,mt8163-dsi'] or consumer.get('status')!=['disabled']:raise ValueError('Unqualified DSI consumer activation')
    ident=node.get('phandle',[])
    if len(ident)!=1 or consumer.get('phys')!=ident:raise ValueError('DSI does not reference reviewed PHY')
    # Parse actual clock argument widths instead of searching for a phandle integer.
    values=consumer.get('clocks',[]);pos=0;owners=[]
    while pos<len(values):
        phi=values[pos];pos+=1
        if phi not in phandles:raise ValueError('Unknown DSI clock provider')
        owner=phandles[phi];width=nodes[owner].get('#clock-cells',[])
        if len(width)!=1 or not 0<=width[0]<=4 or pos+width[0]>len(values):raise ValueError('Invalid/truncated DSI clock specifier')
        args=values[pos:pos+width[0]];pos+=width[0];owners.append((owner,args))
    if len(owners)!=3 or owners[2]!=(PHY,[]) or consumer.get('clock-names')!=['engine','digital','hs']:raise ValueError('Wrong DSI PLL clock lineage')
    return {'scope':'Fresh disabled MIPI/DSI source graph only; no physical clock/reset/PHY/display admission','reference_clock_id':13,'reset_id':10,'resource_bytes':4096,'required_source_extent':108,'fixed_reference_hz':26000000,'dsi_pll_clock_reference':True,'phy_and_dsi_remain_disabled':True,'source_build_run':40859970271,'full_binding_validation_passed':False,'runtime_qualified':False}


def from_dtb(tool,dtb):
    raw=snapshot(tool,dtb);nodes={};strings=['compatible','status','clock-output-names','clock-names','nvmem-cell-names']
    keys=strings+['reg','phandle','clocks','resets','#clock-cells','#phy-cells','#reset-cells','clock-frequency','phys','nvmem-cells','drive-strength-microamp','assigned-clocks','assigned-clock-parents','assigned-clock-rates']
    for path,props in raw.items():
        node={}
        for key in keys:
            if key not in props:continue
            data=bytes(int(x,16) for x in props[key].split())
            if key in strings:node[key]=data.decode().strip('\0').split('\0')
            else:
                if len(data)%4:raise ValueError('Unaligned cell property')
                node[key]=list(struct.unpack('>'+str(len(data)//4)+'I',data))
        nodes[path]=node
    return {'nodes':nodes}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('graph',type=Path,nargs='?');p.add_argument('--dtb',type=Path);p.add_argument('--fdtget',type=Path,default=ROOT/'work/dtb-tool/build/fdtget');a=p.parse_args()
    if bool(a.graph)==bool(a.dtb):p.error('Choose graph or --dtb')
    r=validate(from_dtb(a.fdtget,a.dtb) if a.dtb else json.loads(a.graph.read_text()))
    if a.dtb:r['dtb_sha256']=hashlib.sha256(a.dtb.read_bytes()).hexdigest()
    print(json.dumps(r,indent=2))


if __name__=='__main__':main()
