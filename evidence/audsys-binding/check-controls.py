"""Actual decoded-node parent metadata controls; disabled child remains globally unmatched."""
import argparse
import copy
import json
from pathlib import Path
from dtschema import DTValidator
from referencing import Registry
from referencing.jsonschema import DRAFT201909
from ruamel.yaml import YAML
p=Path(__file__).resolve().parent
bundle=json.loads((p/'portable-schemas.json').read_text());schemas=bundle['schemas']
registry=Registry().with_resources((uri,DRAFT201909.create_resource(s)) for uri,s in schemas.items())
v=DTValidator.DtValidator(schemas[bundle['root']],registry=registry)
base=json.loads((p/'captured-node.json').read_text());cases=[]
def run(name,node,expected):
 actual=v.is_valid(node)
 assert actual==expected,(name,[str(e)[:250] for e in v.iter_errors(node)])
 cases.append({'name':name,'accepted':actual,'expected':expected})
run('actual parent metadata with independently unmatched disabled MT8163 AFE child',base,True)
for key in ['compatible','reg','#clock-cells']:
 n=copy.deepcopy(base);n.pop(key);run('missing '+key,n,False)
for value in [[],[base['reg'][0],base['reg'][0]]]:
 n=copy.deepcopy(base);n['reg']=value;run('wrong reg cardinality '+str(len(value)),n,False)
for value in [0,2,[1]]:
 n=copy.deepcopy(base);n['#clock-cells']=value;run('wrong clock cells '+str(value),n,False)
for value in [['mediatek,mt8163-audsys'],['syscon','mediatek,mt8163-audsys'],['mediatek,mt8163-audsys','syscon','simple-mfd'],['mediatek,unknown-audsys','syscon']]:
 n=copy.deepcopy(base);n['compatible']=value;run('wrong compatible '+str(value),n,False)
for key,value in [('clocks',[[3,4]]),('clock-names',['aud']),('unexpected-parent',True),('audio-controller',3)]:
 n=copy.deepcopy(base);n[key]=value;run('unsupported parent property/type '+key,n,False)
n=copy.deepcopy(base);n.pop('audio-controller');run('standalone parent without optional populated child',n,True)
y=YAML(typ='safe');old=y.load((p/'audsys-original.yaml').read_text());new=y.load((p/'audsys-proposed.yaml').read_text())
values=old['properties']['compatible']['oneOf'][0]['items'][0]['enum']
for value in values:
 n=copy.deepcopy(base);n['compatible']=[value,'syscon'];n.pop('audio-controller');n.pop('reg');run('prior '+value+' still does not require reg',n,True)
n=copy.deepcopy(base);n['compatible']=['mediatek,mt2701-audsys','syscon'];run('prior MT2701 still rejects MT8163-only AFE child',n,False)
new['properties']['compatible']['oneOf'][0]['items'][0]['enum'].remove('mediatek,mt8163-audsys');original_branch=new.pop('else');new.pop('if');new.pop('then');new.update(original_branch);assert new==old
for kind in ['canonical','isolated']:
 ds=json.loads((p/(kind+'-diagnostics.json')).read_text());child=[x for x in ds if x['node']=='/soc/clock-controller@11220000/audio-controller'];assert len(child)==1 and child[0]['type']=='unmatched'
result={'scope':'Parent metadata only; disabled AFE child independently unmatched, no child/audio support','passed':True,'count':len(cases),'cases':cases,'other_soc_policy_structurally_preserved':True,'unsupported_child_diagnostic_preserved_in_both_contexts':True,'runtime_qualified':False}
parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
if args.check:assert result==json.loads((p/'controls.json').read_text())
else:(p/'controls.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(cases),'actual decoded parent controls; unsupported child remains unmatched')
