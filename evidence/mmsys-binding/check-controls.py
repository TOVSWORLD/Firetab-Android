"""Validate the processed exact MMSYS tuple and preserve all old constraints."""
import copy
import json
from pathlib import Path
from jsonschema import Draft7Validator
from ruamel.yaml import YAML
root=Path(__file__).resolve().parent
v=Draft7Validator(json.loads((root/'processed-schema.json').read_text()))
base={'$nodename':['syscon@14000000'],'compatible':['mediatek,mt8163-mmsys','syscon'],'reg':[[0x14000000,0x1000]],'#clock-cells':1,'#reset-cells':1}
cases=[]
for name,changes,expected in [
 ('captured-exact',{},True),('standalone',{'compatible':['mediatek,mt8163-mmsys']},False),
 ('missing-reg',{'reg':None},False),('two-reg',{'reg':[[0,4096],[4096,4096]]},False),
 ('missing-clock-cells',{'#clock-cells':None},False),('wrong-clock-cells',{'#clock-cells':0},False),
 ('wrong-reset-cells',{'#reset-cells':2},False),('invented-fallback',{'compatible':['mediatek,mt8163-mmsys','mediatek,mt8173-mmsys','syscon']},False),
 ('unknown-property',{'invented-property':1},False),
 ('existing-mt8173',{'compatible':['mediatek,mt8173-mmsys','syscon']},True),
 ('existing-reset-optional',{'compatible':['mediatek,mt8173-mmsys','syscon'],'#reset-cells':None},True)]:
 node=copy.deepcopy(base)
 for k,val in changes.items():
  if val is None:node.pop(k,None)
  else:node[k]=val
 actual=v.is_valid(node);assert actual==expected,(name,list(v.iter_errors(node)))
 cases.append({'name':name,'accepted':actual,'expected':expected})
y=YAML(typ='safe');o=y.load((root/'original.yaml').read_text());p=y.load((root/'proposed.yaml').read_text());p['properties']['compatible']['oneOf'][0]['items'][0]['enum'].remove('mediatek,mt8163-mmsys');assert o==p
(root/'controls.json').write_text(json.dumps({'cases':cases,'all_unrelated_constraints_preserved':True,'passed':True},indent=2)+'\n')
print('PASS:11 processed-node controls; unrelated constraints preserved')
