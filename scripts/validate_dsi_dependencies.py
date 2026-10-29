#!/usr/bin/env python3
"""Check fresh disabled DSI source graph; no master/panel/runtime admission."""
import argparse,hashlib,json,struct
from pathlib import Path
import validate_mipi_dependencies as mipi
from compare_pmic_dtb import snapshot
ROOT=Path(__file__).resolve().parents[1];DSI=mipi.DSI;PHY=mipi.PHY

def validate(graph):
 contract=json.loads((ROOT/'evidence/dsi-binding/source-contract.json').read_text())
 for path,sha in contract['sha256'].items():
  if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=sha:raise ValueError('Reviewed DSI source/build drift: '+path)
 mipi.validate(graph);nodes=graph['nodes'];n=nodes[DSI];ph={v['phandle'][0]:k for k,v in nodes.items() if 'phandle'in v}
 for key,value in [('reg',[0,0x14012000,0,0x1000]),('interrupts',[0,195,8]),('clock-names',['engine','digital','hs']),('phy-names',['dphy']),('status',['disabled'])]:
  if n.get(key)!=value:raise ValueError('Wrong DSI '+key)
 if n['reg'][3]<0x400:raise ValueError('DSI below source extent')
 mm='/soc/syscon@14000000';domain='/soc/syscon@10006000/power-controller'
 def spec(key,owner,args):
  v=n.get(key,[])
  if not v or ph.get(v[0])!=owner or v[1:]!=args:raise ValueError('Wrong DSI '+key+' provider/ID')
 spec('resets',mm,[23]);spec('power-domains',domain,[0]);spec('phys',PHY,[])
 clocks=n.get('clocks',[])
 if len(clocks)!=5 or ph.get(clocks[0])!=mm or clocks[1]!=34 or ph.get(clocks[2])!=mm or clocks[3]!=35 or ph.get(clocks[4])!=PHY:raise ValueError('Wrong DSI clock lineage')
 for owner,key,width in [(mm,'#clock-cells',1),(mm,'#reset-cells',1),(domain,'#power-domain-cells',1)]:
  if nodes[owner].get(key)!=[width] or nodes[owner].get('status') not in [None,['okay'],['ok']]:raise ValueError('Wrong DSI dependency width/status')
 if nodes[mm].get('compatible')!=['mediatek,mt8163-mmsys','syscon']:raise ValueError('Wrong MMSYS provider')
 if any(p.startswith(DSI+'/') for p in nodes):raise ValueError('Unexpected DSI graph/child changed')
 if any(k.startswith('assigned-clock') for k in n):raise ValueError('Unqualified DSI clock override')
 return {'scope':'Fresh compiled disabled DSI dependencies only; actual graph absent','source_build_run':40871693672,'resource_bytes':4096,'source_minimum_bytes':1024,'engine_clock_id':34,'digital_clock_id':35,'mmsys_reset_id':23,'power_domain_id':0,'missing_panel_graph':True,'mmsys_master_pipeline_qualified':False,'runtime_qualified':False}

def from_dtb(tool,dtb):
 graph=mipi.from_dtb(tool,dtb);raw=snapshot(tool,dtb)
 for path,props in raw.items():
  for key in ['interrupts','power-domains','#power-domain-cells']:
   if key in props:
    b=bytes(int(x,16) for x in props[key].split())
    if len(b)%4:raise ValueError('Unaligned DSI dependency property')
    graph['nodes'][path][key]=list(struct.unpack('>'+str(len(b)//4)+'I',b))
  if 'phy-names' in props:graph['nodes'][path]['phy-names']=bytes(int(x,16) for x in props['phy-names'].split()).decode().strip('\0').split('\0')
 return graph

def main():
 p=argparse.ArgumentParser();p.add_argument('--dtb',type=Path,required=True);p.add_argument('--fdtget',type=Path,default=ROOT/'work/dtb-tool/build/fdtget');a=p.parse_args();r=validate(from_dtb(a.fdtget,a.dtb));r['dtb_sha256']=hashlib.sha256(a.dtb.read_bytes()).hexdigest();print(json.dumps(r,indent=2))
if __name__=='__main__':main()
