#!/usr/bin/env python3
"""Validate reviewed AUDSYS parent source/DT metadata; never qualify the disabled AFE child."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
from compare_pmic_dtb import snapshot
ROOT=Path(__file__).resolve().parents[1]
PARENT='/soc/clock-controller@11220000'
CHILD=PARENT+'/audio-controller'


def source_layout():
    receipt=json.loads((ROOT/'evidence/audsys-binding/source-contract.json').read_text())
    for path,expected in receipt['sha256'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=expected:raise ValueError('Reviewed AUDSYS source/build input drift: '+path)
    source=(ROOT/'projects/firetabs-android/kernel/clock-port/overlay/drivers/clk/mediatek/clk-mt8163-audsys.c').read_text()
    header=(ROOT/'projects/firetabs-android/kernel/clock-port/overlay/include/dt-bindings/clock/mediatek,mt8163-audsys.h').read_text()
    ids={name:int(value) for name,value in re.findall(r'^#define\s+(CLK_AUDIO_\w+)\s+(\d+)\s*$',header,re.M)}
    tables=re.findall(r'^\s*(?:GATE_AUD|AUD_DIV_GATE|AUD_MUX_DIV)\((CLK_AUDIO_\w+),',source,re.M)
    if sorted(ids.values())!=list(range(19)) or len(tables)!=19 or set(tables)!=set(ids):raise ValueError('AUDSYS clock ID/table coverage changed')
    offsets=[int(v,16) for v in re.findall(r'^#define AUDIO_CLK_AUDDIV_[01]\s+(0x[0-9a-f]+)',source,re.M)]
    offsets += [int(v,0) for v in re.findall(r'\.(?:set|clr|sta)_ofs\s*=\s*(0x[0-9a-f]+|\d+)',source)]
    if not offsets:raise ValueError('No reviewed AUDSYS offsets')
    common=(ROOT/'evidence/clock-port/ack/drivers/clk/mediatek/clk-mtk.c').read_text()
    for anchor in ['base = devm_platform_ioremap_resource(pdev, 0)','of_clk_add_hw_provider(node, of_clk_hw_onecell_get, clk_data)']:
        if anchor not in common:raise ValueError('Common parent resource/provider path changed')
    for anchor in ['.compatible = "mediatek,mt8163-audsys"','devm_of_platform_populate(&pdev->dev)','of_platform_depopulate(&pdev->dev)']:
        if anchor not in source:raise ValueError('Parent match/child ownership changed')
    gates=(ROOT/'evidence/audsys-binding/ack/clk-gate.c').read_text()
    syscon=(ROOT/'evidence/audsys-binding/ack/syscon.c').read_text()
    platform=(ROOT/'evidence/audsys-binding/ack/platform.c').read_text()
    if 'regmap = device_node_to_regmap(node)' not in gates or 'return device_node_get_regmap(np, true, false)' not in syscon:
        raise ValueError('Gate regmap resource-management path changed')
    if '.val_bits = 32' not in syscon or 'reg_io_width = 4' not in syscon:
        raise ValueError('Selected default syscon access width changed')
    if '!of_device_is_available(np)' not in platform or 'devres_add(dev, ptr)' not in platform:
        raise ValueError('Managed/disabled child ownership path changed')
    return {'clock_ids':ids,'gates':len(re.findall(r'^\s*GATE_AUD\(CLK_AUDIO_',source,re.M)),
            'composites':len(re.findall(r'^\s*(?:AUD_DIV_GATE|AUD_MUX_DIV)\(CLK_AUDIO_',source,re.M)),'required_extent_bytes':max(offsets)+4,
            'build_run':receipt['build']['run'],'selected_syscon_default_bits':32,
            'regmap_manages_optional_clock_reset':False,'child_binding_covered':False}


def validate(graph):
    layout=source_layout();nodes=graph['nodes'];parent=nodes[PARENT];child=nodes[CHILD]
    if parent.get('compatible')!=['mediatek,mt8163-audsys','syscon'] or parent.get('#clock-cells')!=[1]:raise ValueError('Wrong AUDSYS provider contract')
    if parent.get('reg')!=[0,0x11220000,0,0x1000]:raise ValueError('Wrong reviewed AUDSYS resource')
    if parent['reg'][3]<layout['required_extent_bytes']:raise ValueError('AUDSYS resource too small for actual tables')
    if any(key in parent for key in ['reg-io-width','big-endian','little-endian','native-endian','clocks','resets','hwlocks']):raise ValueError('Unreviewed AUDSYS regmap/resource overrides')
    if parent.get('status') not in [None,['okay'],['ok']]:raise ValueError('Reviewed AUDSYS parent disabled')
    if child.get('compatible')!=['mediatek,mt8163-afe-pcm'] or child.get('status')!=['disabled']:
        raise ValueError('Unqualified AFE child activation/selection')
    phandles={};providers={}
    for path,node in nodes.items():
        if 'phandle' not in node:continue
        values=node['phandle']
        if len(values)!=1 or type(values[0]) is not int or not 0<values[0]<0xffffffff or values[0] in phandles:raise ValueError('Invalid/duplicate DT phandle')
        phandles[values[0]]=path
        if '#clock-cells' in node:
            cells=node['#clock-cells']
            if len(cells)!=1 or type(cells[0]) is not int or not 0<=cells[0]<=4:raise ValueError('Invalid clock provider argument width')
            providers[values[0]]=(path,cells[0])
    parent_id=parent.get('phandle',[])
    if len(parent_id)!=1 or providers.get(parent_id[0])!=(PARENT,1):raise ValueError('AUDSYS provider phandle missing')
    uses=[]
    for path,node in nodes.items():
        for prop in ['clocks','assigned-clocks','assigned-clock-parents']:
            if prop not in node:continue
            values=node[prop];pos=0
            while pos<len(values):
                phi=values[pos];pos+=1
                if phi==0 and prop!='clocks':continue
                if phi not in providers:raise ValueError('Unknown clock provider in '+path)
                provider,width=providers[phi]
                args=values[pos:pos+width]
                if len(args)!=width:raise ValueError('Truncated clock specifier in '+path)
                pos+=width
                if provider==PARENT:
                    if len(args)!=1 or type(args[0]) is not int or args[0] not in layout['clock_ids'].values():raise ValueError('Out-of-range AUDSYS consumer ID')
                    uses.append({'node':path,'property':prop,'id':args[0]})
    if not uses or not any(x['node']==CHILD for x in uses):raise ValueError('Reviewed AUDSYS consumer lineage missing')
    return {'scope':'Fresh source-DTB AUDSYS parent metadata, not clock/audio runtime',
            'parent':PARENT,'resource_bytes':parent['reg'][3],'source_layout':layout,
            'audsys_clock_references':uses,'child_remains_disabled':True,
            'child_binding_covered':False,'full_binding_validation_passed':False,'runtime_qualified':False}


def from_dtb(tool,dtb):
    raw=snapshot(tool,dtb);nodes={}
    for path,props in raw.items():
        n={}
        for key in ['compatible','status','reg','phandle','#clock-cells','clocks','assigned-clocks','assigned-clock-parents','reg-io-width','big-endian','little-endian','native-endian','resets','hwlocks']:
            if key not in props:continue
            data=bytes(int(x,16) for x in props[key].split())
            if key in ['compatible','status']:n[key]=data.decode().strip('\0').split('\0')
            else:
                if len(data)%4:raise ValueError('Unaligned DT cell property')
                n[key]=list(struct.unpack('>'+str(len(data)//4)+'I',data))
        nodes[path]=n
    return {'nodes':nodes}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('graph',type=Path,nargs='?');p.add_argument('--dtb',type=Path);p.add_argument('--fdtget',type=Path,default=ROOT/'work/dtb-tool/build/fdtget');args=p.parse_args()
    if bool(args.graph)==bool(args.dtb):p.error('Choose graph or --dtb')
    result=validate(from_dtb(args.fdtget,args.dtb) if args.dtb else json.loads(args.graph.read_text()))
    if args.dtb:result['dtb_sha256']=hashlib.sha256(args.dtb.read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
