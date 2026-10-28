"""Actual processed dtschema controls for decoded candidate watchdog node."""
import copy
import json
from pathlib import Path
from dtschema import DTValidator
from referencing import Registry
from referencing.jsonschema import DRAFT201909
from ruamel.yaml import YAML
root=Path(__file__).resolve().parent
b=json.loads((root/'processed-schemas.json').read_text())
registry=Registry().with_resources((uri,DRAFT201909.create_resource(s)) for uri,s in b['schemas'].items())
v=DTValidator.DtValidator(b['schemas'][b['root']],registry=registry)
base=json.loads((root/'captured-node.json').read_text());cases=[]
def run(name,changes,expected):
 node=copy.deepcopy(base)
 for key,value in changes.items():
  if value is None:node.pop(key,None)
  else:node[key]=value
 actual=v.is_valid(node)
 assert actual==expected,(name,list(v.iter_errors(node)))
 cases.append({'name':name,'accepted':actual,'expected':expected})
run('decoded-candidate',{},True)
run('missing-compatible',{'compatible':None},False)
run('unknown-compatible',{'compatible':['mediatek,mt0000-wdt']},False)
run('unsupported-fallback',{'compatible':['mediatek,mt8163-wdt','mediatek,mt6589-wdt']},False)
run('missing-reg',{'reg':None},False)
run('two-reg',{'reg':[[0,0,0,4096],[0,4096,0,4096]]},False)
run('missing-optional-irq',{'interrupts':None},True)
run('two-irq',{'interrupts':[[0,128,8],[0,129,8]]},False)
run('wrong-reset-cells',{'#reset-cells':2},False)
run('optional-reset-provider',{'#reset-cells':None},True)
run('unknown-property',{'invented-ignore-watchdog':True},False)
for n,expected in [(1,False),(2,True),(31,True),(32,False)]:
 run('timeout-'+str(n),{'timeout-sec':[n]},expected)
run('disable-extrst',{'mediatek,disable-extrst':True},True)
run('reset-by-toprgu',{'mediatek,reset-by-toprgu':True},True)
run('existing-mt6589-unchanged-timeout-policy',{'compatible':['mediatek,mt6589-wdt'],'timeout-sec':[60]},True)
run('existing-mt8183',{'compatible':['mediatek,mt8183-wdt']},True)
y=YAML(typ='safe');o=y.load((root/'original.yaml').read_text());p=y.load((root/'proposed.yaml').read_text());p['properties']['compatible']['oneOf'][0]['enum'].remove('mediatek,mt8163-wdt');p['allOf'].pop();assert p==o
(root/'controls.json').write_text(json.dumps({'scope':'Actual decoded-node Draft201909/typeSize controls; no runtime watchdog/reset claim','cases':cases,'all_unrelated_constraints_preserved':True,'passed':True,'runtime_qualified':False},indent=2)+'\n')
print('PASS:',len(cases),'actual decoded-node controls; existing constraints preserved')
