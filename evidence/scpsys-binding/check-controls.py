"""Exercise decoded captured hierarchy with actual dtschema and all dependencies."""
import copy
import hashlib
import json
from pathlib import Path
from dtschema import DTValidator
from referencing import Registry
from referencing.jsonschema import DRAFT201909
from ruamel.yaml import YAML
root=Path(__file__).resolve().parent
bundle=json.loads((root/'processed-schemas.json').read_text())
registry=Registry().with_resources((u,DRAFT201909.create_resource(s)) for u,s in bundle['schemas'].items())
v=DTValidator.DtValidator(bundle['schemas'][bundle['root']],registry=registry)
base=json.loads((root/'captured-node.json').read_text())
def domain(node,n):return node['power-controller']['power-domain@'+str(n)]
cases=[]
def run(name,edit,expected):
 node=copy.deepcopy(base);edit(node);accepted=v.is_valid(node)
 assert accepted==expected,(name,list(v.iter_errors(node)))
 cases.append({'name':name,'accepted':accepted,'expected':expected})
run('decoded-captured-eight-domain-hierarchy',lambda n:None,True)
run('parent-missing-reg',lambda n:n.pop('reg'),False)
run('parent-missing-child',lambda n:n.pop('power-controller'),False)
run('parent-standalone',lambda n:n.update(compatible=['mediatek,mt8163-scpsys']),False)
run('parent-missing-simple-mfd',lambda n:n.update(compatible=['mediatek,mt8163-scpsys','syscon']),False)
run('parent-two-reg',lambda n:n.update(reg=[[0,4096],[4096,4096]]),False)
run('wrong-child-soc',lambda n:n['power-controller'].update(compatible=['mediatek,mt8167-power-controller']),False)
for key in ['#power-domain-cells','#address-cells','#size-cells']:
 run('missing-controller-'+key,lambda n,k=key:n['power-controller'].pop(k),False)
run('wrong-controller-power-cells',lambda n:n['power-controller'].update({'#power-domain-cells':2}),False)
run('unsupported-new-access-controller-mode',lambda n:n['power-controller'].update({'access-controllers':[[2]]}),False)
for n in [0,4,6]:
 run('protected-domain-'+str(n)+'-missing-infracfg',lambda x,i=n:domain(x,i).pop('mediatek,infracfg'),False)
run('out-of-range-root-id',lambda n:domain(n,1).update(reg=[[8]]),False)
run('negative-id',lambda n:domain(n,1).update(reg=[[-1]]),False)
run('out-of-range-nested-id',lambda n:domain(n,6)['power-domain@7'].update(reg=[[8]]),False)
run('ignored-root-domain-supply',lambda n:domain(n,0).update({'domain-supply':[[1]]}),False)
run('ignored-nested-domain-supply',lambda n:domain(n,6)['power-domain@7'].update({'domain-supply':[[1]]}),False)
run('invalid-domain-cells',lambda n:domain(n,0).update({'#power-domain-cells':2}),False)
run('unknown-controller-property',lambda n:n['power-controller'].update({'disable-protection':True}),False)
def other(n):
 n['compatible']=['mediatek,mt8183-scpsys','syscon','simple-mfd']
 n['power-controller']['compatible']=['mediatek,mt8183-power-controller']
 n['power-controller']['access-controllers']=[[1],[2]]
 n['power-controller']['power-domain@0']['domain-supply']=[[3]]
run('existing-mt8183-two-access-controllers',other,True)
def one(n):other(n);n['power-controller']['access-controllers']=[[1]]
run('existing-mt8183-one-access-controller-rejected',one,False)
y=YAML(typ='safe')
for name in ['mt8163-scpsys','mt8163-power-controller']:
 o=y.load((root/(name+'-original.yaml')).read_text());p=y.load((root/(name+'-proposed.yaml')).read_text())
 if name=='mt8163-scpsys':
  p['properties']['compatible']['items'][0]['enum'].remove('mediatek,mt8163-scpsys');p.pop('allOf')
 else:
  p['properties']['compatible']['enum'].remove('mediatek,mt8163-power-controller');p['allOf'].pop(0);p['$defs'].pop('mt8163-domain-node')
 assert p==o,name
(root/'controls.json').write_text(json.dumps({'cases':cases,'all_unrelated_constraints_preserved':True,'passed':True,'runtime_qualified':False},indent=2)+'\n')
print('PASS:',len(cases),'actual decoded-node controls; original SoC constraints preserved')
