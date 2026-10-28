"""Validate actual processed infracfg tuple and required reset contract."""
import copy
import json
from pathlib import Path
from jsonschema import Draft7Validator
from ruamel.yaml import YAML
root=Path(__file__).resolve().parent
schema=json.loads((root/'processed-schema.json').read_text())
v=Draft7Validator(schema)
base={'compatible':['mediatek,mt8163-infracfg','syscon'],'reg':[[0x10001000,0x1000]],'#clock-cells':1,'#reset-cells':1}
cases=[]
def case(name,change,expected):
    node=copy.deepcopy(base)
    for key,val in change.items():
        if val is None:node.pop(key,None)
        else:node[key]=val
    actual=v.is_valid(node)
    assert actual==expected,(name,list(v.iter_errors(node)))
    cases.append({'name':name,'accepted':actual,'expected':expected})
case('exact tuple and one-cell reset',{},True)
case('standalone tuple rejected',{'compatible':['mediatek,mt8163-infracfg']},False)
case('invented fallback rejected',{'compatible':['mediatek,mt8163-infracfg','mediatek,mt8173-infracfg','syscon']},False)
case('missing reset declaration rejected',{'#reset-cells':None},False)
case('wrong reset cells rejected',{'#reset-cells':0},False)
case('wrong clock cells rejected',{'#clock-cells':2},False)
case('missing register rejected',{'reg':None},False)
case('multiple register ranges rejected',{'reg':[[0x10001000,0x1000],[0x10002000,0x1000]]},False)
case('existing MT8173 reset required',{'compatible':['mediatek,mt8173-infracfg','syscon'],'#reset-cells':None},False)
case('existing MT8173 valid',{'compatible':['mediatek,mt8173-infracfg','syscon']},True)
case('existing MT8167 optional-reset policy preserved',{'compatible':['mediatek,mt8167-infracfg','syscon'],'#reset-cells':None},True)
yaml=YAML(typ='safe');o=yaml.load((root/'original.yaml').read_text());p=yaml.load((root/'proposed.yaml').read_text())
p['properties']['compatible']['oneOf'][0]['items'][0]['enum'].remove('mediatek,mt8163-infracfg')
p['if']['properties']['compatible']['contains']['enum'].remove('mediatek,mt8163-infracfg')
assert o==p
(root/'controls.json').write_text(json.dumps({'cases':cases,'only_exact_compatible_and_reset_requirement_added':True,'all_other_constraints_preserved':True,'passed':True},indent=2)+'\n')
print('PASS:11 actual processed node controls including reset requirement; unrelated constraints preserved')
