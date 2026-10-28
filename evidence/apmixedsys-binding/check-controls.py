"""Actual processed AP mixed PLL provider node controls."""
import copy
import json
from pathlib import Path
from jsonschema import Draft7Validator
from ruamel.yaml import YAML
root=Path(__file__).resolve().parent
v=Draft7Validator(json.loads((root/'processed-schema.json').read_text()))
base={'compatible':['mediatek,mt8163-apmixedsys'],'reg':[[0x1000c000,0x1000]],'#clock-cells':1}
cases=[]
def case(name,change,expected):
    n=copy.deepcopy(base)
    for key,val in change.items():
        if val is None:n.pop(key,None)
        else:n[key]=val
    actual=v.is_valid(n);assert actual==expected,name
    cases.append({'name':name,'accepted':actual,'expected':expected})
case('exact MT8163',{},True)
case('invented syscon tuple',{'compatible':['mediatek,mt8163-apmixedsys','syscon']},False)
case('invented fallback',{'compatible':['mediatek,mt8163-apmixedsys','mediatek,mt8173-apmixedsys']},False)
case('unknown compatible',{'compatible':['mediatek,unknown-apmixedsys']},False)
case('missing register',{'reg':None},False)
case('extra register',{'reg':[[0,4096],[4096,4096]]},False)
case('wrong clock cell count',{'#clock-cells':0},False)
case('existing MT8173',{'compatible':['mediatek,mt8173-apmixedsys']},True)
case('existing MT8167 syscon',{'compatible':['mediatek,mt8167-apmixedsys','syscon']},True)
yaml=YAML(typ='safe');o=yaml.load((root/'original.yaml').read_text());p=yaml.load((root/'proposed.yaml').read_text());p['properties']['compatible']['oneOf'][0]['enum'].remove('mediatek,mt8163-apmixedsys');assert o==p
(root/'controls.json').write_text(json.dumps({'cases':cases,'all_other_constraints_preserved':True,'passed':True},indent=2)+'\n')
print('PASS:9 actual processed PLL-provider node controls; other constraints preserved')
