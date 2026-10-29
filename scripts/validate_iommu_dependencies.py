#!/usr/bin/env python3
"""Check selected candidate MT8163 IOMMU/SMI declarations, not DMA/runtime behavior."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
ROOT=Path(__file__).resolve().parents[1]
PATHS={'iommu':'/soc/iommu@10205000','common':'/soc/smi@14017000',
       'larb0':'/soc/larb@14016000','larb1':'/soc/larb@16010000',
       'larb2':'/soc/larb@15001000','larb3':'/soc/larb@17001000'}
CLOCK_PATHS={'mmsys':'/soc/syscon@14000000','imgsys':'/soc/clock-controller@15000000',
             'vdecsys':'/soc/clock-controller@16000000','vencsys':'/soc/clock-controller@17000000'}


def clock_id(role,name):
    p=ROOT/'projects/firetabs-android/kernel/clock-port/overlay/include/dt-bindings/clock'/('mediatek,mt8163-'+role+'.h')
    return int(re.search(r'^#define\s+'+name+r'\s+(\d+)\s*$',p.read_text(),re.M)[1])


def validate(graph):
    nodes=graph['nodes'];clocks=graph['clock_providers'];power=graph['power_provider']
    if power['compatible']!=['mediatek,mt8163-power-controller'] or power['#power-domain-cells']!=[1]:raise ValueError('Wrong power provider')
    power_id=power['phandle'][0]
    if type(power_id) is not int or power_id<=0:raise ValueError('Invalid power provider phandle')
    required={'common':('mmsys',['CLK_MM_SMI_COMMON']*2,0),
              'larb0':('mmsys',['CLK_MM_SMI_LARB0']*2,0),
              'larb1':('vdecsys',['CLK_VDEC_CKEN','CLK_VDEC_LARB_CKEN'],1),
              'larb2':('imgsys',['CLK_IMG_LARB2_SMI']*2,3),
              'larb3':('vencsys',['CLK_VENC_CKE1','CLK_VENC_CKE0'],2)}
    phandles=[]
    for role,path in PATHS.items():
        n=nodes[path]
        if n.get('status') not in [None,['okay'],['ok']]:raise ValueError('Required node disabled: '+role)
        address=int(path.split('@')[1],16)
        if n.get('reg')!=[0,address,0,65536 if role=='larb1' else 4096]:raise ValueError('Wrong reviewed resource: '+role)
        kind='m4u' if role=='iommu' else 'smi-common' if role=='common' else 'smi-larb'
        if n.get('compatible')!=['mediatek,mt8163-'+kind]:raise ValueError('Wrong source OF tuple: '+role)
        values=n.get('phandle',[])
        if len(values)!=1 or type(values[0]) is not int or not 0<values[0]<0xffffffff:raise ValueError('Invalid node phandle')
        phandles+=values
        if role!='iommu':
            clock_role,symbols,domain=required[role];provider=clocks[clock_role]
            if provider['compatible']!=['mediatek,mt8163-'+clock_role,'syscon'] or provider['#clock-cells']!=[1]:raise ValueError('Wrong clock provider')
            phi=provider['phandle'][0]
            expected=[v for symbol in symbols for v in [phi,clock_id(clock_role,symbol)]]
            if n.get('clock-names')!=['apb','smi'] or n.get('clocks')!=expected:raise ValueError('Clock role/provider/ID drift: '+role)
            if n.get('power-domains')!=[power_id,domain]:raise ValueError('Wrong domain: '+role)
    if len(set(phandles))!=len(phandles):raise ValueError('Duplicate node phandles')
    iommu=nodes[PATHS['iommu']];common=nodes[PATHS['common']]
    if iommu.get('#iommu-cells')!=[1] or iommu.get('power-domains')!=[power_id,0]:raise ValueError('IOMMU domain/cell drift')
    if len(iommu.get('interrupts',[]))!=3:raise ValueError('One bank requires one declared IRQ')
    larbs=[]
    for i in range(4):
        n=nodes[PATHS['larb'+str(i)]]
        if n.get('mediatek,larb-id')!=[i] or n.get('mediatek,smi')!=common['phandle']:raise ValueError('Larb ID/common link drift')
        # Optional vendor-declared larb IRQ; this validates metadata, not a handler.
        if 'interrupts' in n and n['interrupts'] != [0, [205,213,217,207][i], 8]:
            raise ValueError('Vendor larb IRQ declaration drift: larb'+str(i))
        larbs+=n['phandle']
    if iommu.get('mediatek,larbs')!=larbs:raise ValueError('IOMMU must link reviewed larb0..3')
    return {'scope':'Candidate declaration dependency graph only','larbs_checked':4,'smi_common_checked':1,
            'source_clock_role_pairs_checked':5,'optional_larb_irq_contract_checked':True,'source_integration_required':True,
            'full_binding_validation_passed':False,'runtime_qualified':False}


def from_dtb(tool,dtb):
    def node(path):
        props=subprocess.check_output([str(tool),'-p',str(dtb),path],text=True,timeout=15).split();n={}
        for prop in ['compatible','reg','interrupts','mediatek,larbs','mediatek,smi','mediatek,larb-id','clock-names','clocks','power-domains','#iommu-cells','#clock-cells','#power-domain-cells','phandle','status']:
            if prop not in props:continue
            strings=prop in ['compatible','clock-names','status'];v=subprocess.check_output([str(tool),'-ts' if strings else '-tx',str(dtb),path,prop],text=True,timeout=15).split();n[prop]=v if strings else [int(x,16) for x in v]
        return n
    return {'nodes':{path:node(path) for path in PATHS.values()},
            'clock_providers':{role:node(path) for role,path in CLOCK_PATHS.items()},
            'power_provider':node('/soc/syscon@10006000/power-controller')}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('graph',type=Path,nargs='?');p.add_argument('--dtb',type=Path);p.add_argument('--fdtget',type=Path,default=ROOT/'work/dtb-tool/build/fdtget');args=p.parse_args()
    if bool(args.graph)==bool(args.dtb):p.error('Choose captured graph or --dtb')
    graph=from_dtb(args.fdtget,args.dtb) if args.dtb else json.loads(args.graph.read_text());r=validate(graph)
    if args.dtb:r['dtb_sha256']=hashlib.sha256(args.dtb.read_bytes()).hexdigest()
    print(json.dumps(r,indent=2))


if __name__=='__main__':main()
