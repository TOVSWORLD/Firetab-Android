"""Exercise the actual processed MT8163 GPIO/EINT probe prerequisites."""
import copy
import json
from pathlib import Path
from dtschema import DTValidator
from referencing import Registry
from referencing.jsonschema import DRAFT201909
from ruamel.yaml import YAML
root=Path(__file__).resolve().parent
bundle=json.loads((root/'processed-schemas.json').read_text())
registry=Registry().with_resources((uri,DRAFT201909.create_resource(doc)) for uri,doc in bundle['schemas'].items())
v=DTValidator.DtValidator(bundle['schemas'][bundle['root']],registry=registry)
base={'$nodename':['pinctrl@1000b000'],'compatible':['mediatek,mt8163-pinctrl'],'reg':[[0x1000b000,4096]],'mediatek,pctl-regmap':[[1]],'gpio-controller':True,'#gpio-cells':2,'interrupt-controller':True,'#interrupt-cells':2,'interrupts':[[0,153,4],[0,154,4],[0,155,4]]}
cases=[]
tests=[('captured-exact',{},True)]
for key in ['reg','mediatek,pctl-regmap','gpio-controller','#gpio-cells','interrupt-controller','interrupts','#interrupt-cells']:
 tests.append(('missing-'+key,{key:None},False))
tests += [('wrong-gpio-cells',{'#gpio-cells':3},False),('wrong-interrupt-cells',{'#interrupt-cells':1},False),('two-reg',{'reg':[[0,4096],[4096,4096]]},False),('fallback',{'compatible':['mediatek,mt8163-pinctrl','mediatek,mt8167-pinctrl']},False),('zero-parent-irqs',{'interrupts':[]},False),('four-parent-irqs',{'interrupts':[[0,153,4]]*4},False),('one-parent-irq',{'interrupts':[[0,153,4]]},True),('three-regmaps',{'mediatek,pctl-regmap':[[1],[2],[3]]},False),('zero-regmaps',{'mediatek,pctl-regmap':[]},False),('unknown-property',{'invented-property':True},False),('existing-optional-reg',{'compatible':['mediatek,mt8173-pinctrl'],'reg':None},True)]
for name,change,expected in tests:
 node=copy.deepcopy(base)
 for k,val in change.items():
  if val is None:node.pop(k,None)
  else:node[k]=val
 actual=v.is_valid(node);assert actual==expected,(name,list(v.iter_errors(node)))
 cases.append({'name':name,'accepted':actual,'expected':expected})
y=YAML(typ='safe');o=y.load((root/'original.yaml').read_text());p=y.load((root/'proposed.yaml').read_text());p['properties']['compatible']['enum'].remove('mediatek,mt8163-pinctrl');assert len(p['allOf'])==2;p['allOf'].pop();assert p==o
(root/'controls.json').write_text(json.dumps({'cases':cases,'all_unrelated_constraints_preserved':True,'passed':True},indent=2)+'\n')
print('PASS:',len(cases),'processed-node controls; old constraints preserved')
