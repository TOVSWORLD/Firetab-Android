"""Actual processed schema controls for the decoded syscfg provider."""
import copy
import json
from pathlib import Path
from dtschema import DTValidator
from referencing import Registry
from referencing.jsonschema import DRAFT201909
from ruamel.yaml import YAML
root=Path(__file__).resolve().parent;b=json.loads((root/'processed-schemas.json').read_text())
registry=Registry().with_resources((uri,DRAFT201909.create_resource(s)) for uri,s in b['schemas'].items())
v=DTValidator.DtValidator(b['schemas'][b['root']],registry=registry)
base=json.loads((root/'captured-node.json').read_text());cases=[]
def run(name,changes,expected):
 node=copy.deepcopy(base)
 for key,val in changes.items():
  if val is None:node.pop(key,None)
  else:node[key]=val
 actual=v.is_valid(node);assert actual==expected,(name,list(v.iter_errors(node)))
 cases.append({'name':name,'accepted':actual,'expected':expected})
run('decoded-candidate',{},True)
run('standalone',{'compatible':['mediatek,mt8163-pctl-a-syscfg']},False)
run('reversed-tuple',{'compatible':['syscon','mediatek,mt8163-pctl-a-syscfg']},False)
run('missing-compatible',{'compatible':None},False)
run('unknown-soc',{'compatible':['mediatek,mt0000-pctl-a-syscfg','syscon']},False)
run('unsupported-third-compatible',{'compatible':['mediatek,mt8163-pctl-a-syscfg','syscon','simple-mfd']},False)
run('missing-reg',{'reg':None},False)
run('two-regions',{'reg':[[0,0,0,4096],[0,4096,0,4096]]},False)
run('existing-mt8173',{'compatible':['mediatek,mt8173-pctl-a-syscfg','syscon']},True)
run('existing-mt8135',{'compatible':['mediatek,mt8135-pctl-a-syscfg','syscon']},True)
run('unknown-provider-property',{'vendor,metadata':[1]},False)
run('disabled-is-schema-valid-but-reviewed-guard-rejects',{'status':['disabled']},True)
y=YAML(typ='safe');o=y.load((root/'original.yaml').read_text());p=y.load((root/'proposed.yaml').read_text())
p['select']['properties']['compatible']['contains']['enum'].remove('mediatek,mt8163-pctl-a-syscfg')
p['properties']['compatible']['items'][0]['enum'].remove('mediatek,mt8163-pctl-a-syscfg');assert p==o
(root/'controls.json').write_text(json.dumps({'scope':'Actual decoded-node Draft201909/typeSize controls; no resource/physical qualification','cases':cases,'all_unrelated_constraints_preserved':True,'passed':True,'runtime_qualified':False},indent=2)+'\n')
print('PASS:',len(cases),'actual provider-node controls; original constraints preserved')
