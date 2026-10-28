#!/usr/bin/env python3
"""Check reviewed candidate pinctrl syscfg phandle and source register extent."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
ROOT=Path(__file__).resolve().parents[1]


def source_layout():
    base=ROOT/'projects/firetabs-android/kernel/pinctrl-port'
    inputs=json.loads((base/'inputs.json').read_text())
    sources={}
    for x in inputs['inputs'][:2]:
        p=base/'overlay'/x['target'];raw=p.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=x['sha256']:raise ValueError('Pinned pinctrl source drift')
        sources[p.name]=raw.decode()
    common=ROOT/'evidence/pinctrl-port/ack/drivers/pinctrl/mediatek/pinctrl-mtk-common.c'
    expected=json.loads((ROOT/'evidence/pinctrl-binding/source-contract.json').read_text())['sha256'][str(common.relative_to(ROOT))]
    if hashlib.sha256(common.read_bytes()).hexdigest()!=expected:raise ValueError('Common driver drift')
    c=sources['pinctrl-mt8163.c'];header=sources['pinctrl-mtk-mt8163.h']
    pins=[int(v) for v in re.findall(r'PINCTRL_PIN\((\d+),',header)]
    if pins!=list(range(155)):raise ValueError('Reviewed pin span changed')
    descriptor=c.split('static const struct mtk_pinctrl_devdata mt8163_pinctrl_data = {',1)[1].split('.eint_hw',1)[0]
    def scalar(name):return int(re.search(r'\.'+name+r'\s*=\s*(0x[0-9a-f]+|\d+)',descriptor)[1],0)
    if scalar('type1_start')!=scalar('type1_end'):raise ValueError('Second regmap would require a new audit')
    offsets=[];table_counts={}
    for macro,position in [('MTK_PIN_DRV_GRP',1),('MTK_PIN_PUPD_SPEC_SR',1),('MTK_PIN_IES_SMT_SPEC',2)]:
        values=[int(v.split(',')[position].strip(),0) for v in re.findall(macro+r'\(([^)]+)\)',c)]
        if not values:raise ValueError('Missing selected source table')
        offsets.extend(values);table_counts[macro]=len(values)
    for pin in pins:
        port=((pin>>scalar('mode_shf'))&scalar('port_mask'))<<scalar('port_shf')
        offsets.extend(port+scalar(n) for n in ['dir_offset','pullen_offset','pullsel_offset','dout_offset','din_offset'])
        offsets.append(((pin//scalar('mode_per_reg'))<<scalar('port_shf'))+scalar('pinmux_offset'))
    last_word=max(offsets)+2*scalar('port_align')
    return {'pin_count':len(pins),'table_counts':table_counts,'maximum_reviewed_base_offset':max(offsets),
            'conservative_last_word_offset':last_word,'required_extent_bytes':last_word+4,
            'scope':'Selected descriptor/tables with conservative set/clear aliases; not all possible MMIO or hardware proof'}


def validate(pair):
    provider=pair['provider'];consumer=pair['consumer'];layout=source_layout()
    if provider.get('compatible')!=['mediatek,mt8163-pctl-a-syscfg','syscon']:raise ValueError('Wrong syscfg provider tuple')
    if consumer.get('compatible')!=['mediatek,mt8163-pinctrl']:raise ValueError('Wrong consumer tuple')
    phandle=provider.get('phandle')
    if type(phandle) is not int or not 0<phandle<0xffffffff:raise ValueError('Missing/invalid provider phandle')
    if consumer.get('mediatek,pctl-regmap')!=[[phandle]]:raise ValueError('Consumer must target the actual one-map provider')
    if provider.get('status') not in [None,['okay'],['ok']]:raise ValueError('Provider disabled')
    reg=provider.get('reg')
    if not isinstance(reg,list) or len(reg)!=1 or not isinstance(reg[0],list) or len(reg[0])!=4 or reg[0][:3]!=[0,0x10005000,0]:raise ValueError('Wrong reviewed provider resource')
    if any(type(cell) is not int or not 0<=cell<=0xffffffff for cell in reg[0]):raise ValueError('Invalid register cells')
    extent=reg[0][3]
    if type(extent) is not int or extent<layout['required_extent_bytes']:raise ValueError('Provider resource too small for selected source accesses')
    if extent!=0x1000:raise ValueError('Unreviewed register extent change')
    return {'scope':'Fresh declared-DTB/provider/source extent check only','provider_phandle':phandle,
            'resource_bytes':extent,'source_layout':layout,'runtime_qualified':False}


def from_dtb(tool,dtb):
    provider='/soc/syscon@10005000';consumer='/soc/pinctrl@1000b000'
    def query(path,key,strings=False):
        cmd=[str(tool),'-ts' if strings else '-tx',str(dtb),path,key]
        text=subprocess.check_output(cmd,text=True,timeout=15).strip()
        return text.split() if strings else [int(x,16) for x in text.split()]
    phandle=query(provider,'phandle')
    if len(phandle)!=1:raise ValueError('Expected single provider phandle')
    props=subprocess.check_output([str(tool),'-p',str(dtb),provider],text=True,timeout=15).split()
    node={'compatible':query(provider,'compatible',True),'reg':[query(provider,'reg')],'phandle':phandle[0]}
    if 'status' in props:node['status']=query(provider,'status',True)
    return {'provider':node,'consumer':{'compatible':query(consumer,'compatible',True),
            'mediatek,pctl-regmap':[[x] for x in query(consumer,'mediatek,pctl-regmap')]}}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('pair',type=Path,nargs='?');p.add_argument('--dtb',type=Path);p.add_argument('--fdtget',type=Path,default=ROOT/'work/dtb-tool/build/fdtget');args=p.parse_args()
    if bool(args.pair)==bool(args.dtb):p.error('Choose decoded pair JSON or --dtb')
    pair=from_dtb(args.fdtget,args.dtb) if args.dtb else json.loads(args.pair.read_text());result=validate(pair)
    if args.dtb:result['dtb_sha256']=hashlib.sha256(args.dtb.read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
