"""Actual processed four-provider tuple/register controls."""
import copy
import json
from pathlib import Path
from jsonschema import Draft7Validator
from ruamel.yaml import YAML
root=Path(__file__).resolve().parent
v=Draft7Validator(json.loads((root/'processed-schema.json').read_text()))
cases=[]
for provider in ['imgsys','mfgcfg','vdecsys','vencsys']:
    base={'compatible':['mediatek,mt8163-'+provider,'syscon'],'reg':[[0x13000000,0x1000]],'#clock-cells':1}
    tests=[('exact',{},True),('standalone',{'compatible':[base['compatible'][0]]},False),
           ('missing-reg',{'reg':None},False),('two-reg',{'reg':[[0,4096],[4096,4096]]},False),
           ('wrong-clock-cells',{'#clock-cells':0},False),
           ('invented-fallback',{'compatible':[base['compatible'][0],'mediatek,mt8173-imgsys','syscon']},False),
           ('power-domain-policy',{'power-domains':[[1,0]]},False)]
    for name,change,expected in tests:
        node=copy.deepcopy(base)
        for key,val in change.items():
            if val is None:node.pop(key,None)
            else:node[key]=val
        actual=v.is_valid(node);assert actual==expected,(provider,name)
        cases.append({'provider':provider,'name':name,'accepted':actual,'expected':expected})
for name,node,expected in [
 ('existing-mt8183-power-domain',{'compatible':['mediatek,mt8183-mfgcfg','syscon'],'#clock-cells':1,'power-domains':[[1,0]]},True),
 ('existing-mt8167-power-domain-rejected',{'compatible':['mediatek,mt8167-mfgcfg','syscon'],'#clock-cells':1,'power-domains':[[1,0]]},False),
 ('existing-mt8173-optional-reg-preserved',{'compatible':['mediatek,mt8173-imgsys','syscon'],'#clock-cells':1},True)]:
    actual=v.is_valid(node);assert actual==expected,name
    cases.append({'name':name,'accepted':actual,'expected':expected})
yaml=YAML(typ='safe');o=yaml.load((root/'original.yaml').read_text());p=yaml.load((root/'proposed.yaml').read_text())
for provider in ['imgsys','mfgcfg','vdecsys','vencsys']:
    p['properties']['compatible']['oneOf'][0]['items'][0]['enum'].remove('mediatek,mt8163-'+provider)
assert len(p['allOf'])==2
old=p.pop('allOf')[0];p.update(old);assert o==p
(root/'controls.json').write_text(json.dumps({'cases':cases,'all_unrelated_constraints_preserved':True,'only_new_providers_require_reg':True,'passed':True},indent=2)+'\n')
print('PASS:31 actual processed node controls; existing policies preserved')
