"""Closed processed PHY/type policy controls, proven against the full matched validator."""
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
reg=Registry().with_resources((u,DRAFT201909.create_resource(s)) for u,s in schemas.items())
validator=DTValidator.DtValidator(schemas[bundle['root']],registry=reg)
always=[DTValidator.DtValidator({'if':schemas[u]['select'],'then':schemas[u]},registry=reg) for u in bundle['always_schemas']]
class TypePipeline:
 def iter_errors(self,node):
  for val in always:yield from val.iter_errors(node)
v=TypePipeline()
base=json.loads((p/'captured-node.json').read_text())
out=p
cases=[]
def run(name,n,expected):
 errors=list(validator.iter_errors(n))+list(v.iter_errors(n));actual=not errors;assert actual==expected,(name,[str(e)[:200] for e in errors]);cases.append({'name':name,'accepted':actual})
run('actual disabled candidate metadata,not runtime',base,True)
for key in ['compatible','reg','clocks','clock-output-names','#phy-cells','#clock-cells','resets']:
 n=copy.deepcopy(base);n.pop(key);run('missing '+key,n,False)
for key in ['reg','clocks','resets']:
 for value in [[],base[key]+base[key],'bad']:
  n=copy.deepcopy(base);n[key]=value;run('wrong '+key+' '+str(value),n,False)
for key in ['#clock-cells','#phy-cells']:
 for value in [1,[0],'0']:
  n=copy.deepcopy(base);n[key]=value;run('wrong '+key+' '+str(value),n,False)
for key,value in [('nvmem-cells',[[1]]),('nvmem-cell-names',['calibration-data']),('drive-strength-microamp',[4000])]:
 n=copy.deepcopy(base);n[key]=value;run('rejected override '+key,n,False)
for value in [['mediatek,mt8163-mipi-tx','mediatek,mt8173-mipi-tx'],['mediatek,mt8173-mipi-tx','mediatek,mt8163-mipi-tx'],['mediatek,unknown-mipi-tx']]:
 n=copy.deepcopy(base);n['compatible']=value;run('unreviewed compatible '+str(value),n,False)
for compatible in ['mediatek,mt2701-mipi-tx','mediatek,mt8173-mipi-tx','mediatek,mt8183-mipi-tx']:
 n=copy.deepcopy(base);n['compatible']=[compatible];n.pop('resets');n['drive-strength-microamp']=[4000];n['nvmem-cells']=[[1]];n['nvmem-cell-names']=['calibration-data'];run('old overrides retained '+compatible,n,True)
 n['resets']=base['resets'];run('old reset prohibition retained '+compatible,n,False)
y=YAML(typ='safe');old=y.load((out/'dsi-original.yaml').read_text());new=y.load((out/'dsi-proposed.yaml').read_text());new['properties']['compatible']['oneOf'].remove({'const':'mediatek,mt8163-mipi-tx'});new['properties'].pop('resets');new.pop('allOf');assert new==old

result={'scope':'Source-matched disabled MIPI metadata; PHY/reset/PLL/display runtime unqualified','count':len(cases),'cases':cases,'old_soc_policy_structurally_preserved':True,'type_policy_pipeline_retained':True,'full_pipeline_equivalence_control_count':bundle['full_pipeline_control_count'],'runtime_qualified':False}
a=argparse.ArgumentParser();a.add_argument('--check',action='store_true');args=a.parse_args()
if args.check:assert result==json.loads((p/'controls.json').read_text())
else:(p/'controls.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(cases),'actual MIPI metadata/type-policy controls; old SoC structure preserved')
