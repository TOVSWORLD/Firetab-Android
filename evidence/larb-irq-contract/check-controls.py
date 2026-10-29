"""Actual processed MT8163-only optional IRQ controls; no hardware qualification."""
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
registry=Registry().with_resources((uri,DRAFT201909.create_resource(s)) for uri,s in bundle['schemas'].items())
v=DTValidator.DtValidator(bundle['schemas'][bundle['root']],registry=registry)
nodes=json.loads((root/'captured-nodes.json').read_text());cases=[]
for path,base in nodes.items():
    def run(name,change,expected):
        n=copy.deepcopy(base)
        for key,val in change.items():
            if val is None:n.pop(key,None)
            else:n[key]=val
        actual=v.is_valid(n)
        assert actual==expected,(name,list(v.iter_errors(n)))
        cases.append({'node':path,'name':name,'accepted':actual,'expected':expected})
    run('actual vendor-declared single IRQ',{},True)
    run('optional IRQ absent',{'interrupts':None},True)
    run('two IRQs rejected',{'interrupts':base['interrupts']*2},False)
    run('unrelated unknown property rejected',{'vendor,unknown':[1]},False)
    run('old mt8173 retains IRQ prohibition',{'compatible':['mediatek,mt8173-smi-larb']},False)
    run('old mt8167 retains IRQ prohibition',{'compatible':['mediatek,mt8167-smi-larb']},False)
    run('old mt8173 without IRQ remains valid',{'compatible':['mediatek,mt8173-smi-larb'],'interrupts':None},True)
    run('supplier still required',{'mediatek,smi':None},False)
    run('ID range still enforced',{'mediatek,larb-id':4},False)
    run('clock order still enforced',{'clock-names':['smi','apb']},False)
y=YAML(typ='safe');old=y.load((root/'prior-proposed.yaml').read_text());new=y.load((root/'proposed.yaml').read_text())
new['properties'].pop('interrupts');new['allOf'][-1].pop('else');assert new==old
source=json.loads((root/'source-report.json').read_text())
for name,receipt in source['sources'].items():
    if 'excerpt_sha256' in receipt:assert hashlib.sha256((root/name).read_bytes()).hexdigest()==receipt['excerpt_sha256']
assert 'irq_of_parse_and_map(node, 0)' in (root/'legacy-m4u-probe.c').read_text()
assert 'request_irq(m4u_dev->irq_num[m4u_id], MTK_M4U_isr' in (root/'legacy-m4u-request.c').read_text()
assert 'platform_get_resource(pdev, IORESOURCE_MEM, 0)' in (root/'legacy-larb-probe.c').read_text()
(root/'controls.json').write_text(json.dumps({'scope':'Actual decoded-node optional resource contract; not handler or wiring proof','cases':cases,'prior_unrelated_constraints_preserved':True,'passed':True,'runtime_qualified':False},indent=2)+'\n')
print('PASS:',len(cases),'actual controls; prior constraints and source receipts verified')
