"""Actual decoded SYM827 metadata controls; physical bank/voltage remain unqualified."""
import argparse
import copy
import json
import hashlib
import sys
from pathlib import Path
from dtschema import DTValidator
from referencing import Registry
from referencing.jsonschema import DRAFT201909
from ruamel.yaml import YAML
p=Path(__file__).resolve().parent
bundle=json.loads((p/'portable-schemas.json').read_text())
registry=Registry().with_resources((uri,DRAFT201909.create_resource(s)) for uri,s in bundle['schemas'].items())
val=DTValidator.DtValidator(bundle['schemas'][bundle['root']],registry=registry)
base=json.loads((p/'captured-node.json').read_text())
cases=[]
def run(name,n,expected):
 actual=val.is_valid(n);assert actual==expected,(name,[str(e)[:200] for e in val.iter_errors(n)]);cases.append({'name':name,'accepted':actual})
run('actual candidate metadata; physical active bank not qualified',base,True)
for selector in [0,1,2,[],[1],[1,0],'1']:
 n=copy.deepcopy(base);n['fcs,suspend-voltage-selector']=selector;run('selector '+str(selector),n,selector in [0,1] and isinstance(selector,int))
n=copy.deepcopy(base);n.pop('fcs,suspend-voltage-selector');run('missing explicit bank',n,False)
for key,value in [('vsel-gpios',[[1,34,0]]),('vsel-gpio',[[1,34,0]]),('en-gpio',[[1,34,0]])]:
 n=copy.deepcopy(base);n[key]=value;run('unowned '+key,n,False)
for compatible in ['silergy,syr827','silergy,syr828','fcs,fan53555','fcs,fan53526','rockchip,rk8600','rockchip,rk8602','tcs,tcs4525']:
 n=copy.deepcopy(base);n['compatible']=[compatible];n.pop('fcs,suspend-voltage-selector');run('old optional selector '+compatible,n,True)
for key in ['compatible','reg']:
 n=copy.deepcopy(base);n.pop(key);run('missing '+key,n,False)
n=copy.deepcopy(base);n['compatible']=['silergy,sym827-regulator'];run('legacy ABI not alias',n,False)

y=YAML(typ='safe');old=y.load((p/'fan53555-original.yaml').read_text());new=y.load((p/'fan53555-proposed.yaml').read_text())
new['properties']['compatible']['oneOf'][0]['enum'].remove('silergy,sym827');new['allOf'].pop();assert new==old
result={'scope':'Source-matched metadata; physical identity/GPIO34/DVS/active bank/voltage handoff remain unqualified','passed':True,'count':len(cases),'cases':cases,'older_soc_policy_structurally_preserved':True,'runtime_qualified':False}
parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--dtb',type=Path);a=parser.parse_args()
if a.dtb:
 root=p.parents[1];sys.path.insert(0,str(root/'scripts'))
 from compare_pmic_dtb import snapshot
 contract=json.loads((p/'source-contract.json').read_text())
 assert hashlib.sha256(a.dtb.read_bytes()).hexdigest()==contract['canonical_dtb_sha256']
 assert snapshot(root/'work/dtb-tool/build/fdtget',a.dtb)['/soc/i2c@11008000/regulator@60']==json.loads((p/'captured-raw-node.json').read_text())
if a.check:assert result==json.loads((p/'controls.json').read_text())
else:(p/'controls.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(cases),'actual decoded SYM827 controls; older SoC policies preserved')
