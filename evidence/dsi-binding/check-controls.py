"""Replay full selected/type DSI controls; expose missing disabled panel graph."""
import argparse,json
from pathlib import Path
from dtschema import DTValidator
from referencing import Registry
from referencing.jsonschema import DRAFT201909
from ruamel.yaml import YAML
p=Path(__file__).resolve().parent;b=json.loads((p/'portable-schemas.json').read_text());schemas=b['schemas'];reg=Registry().with_resources((u,DRAFT201909.create_resource(s)) for u,s in schemas.items());selected=DTValidator.DtValidator(schemas[b['root']],registry=reg);always=[DTValidator.DtValidator({'if':schemas[u]['select'],'then':schemas[u]},registry=reg) for u in b['always_schemas']];cases=json.loads((p/'instances.json').read_text())
for row in cases:
 errors=list(selected.iter_errors(row['node']))
 for validator in always:errors+=list(validator.iter_errors(row['node']))
 assert (not errors)==row['accepted'],(row['name'],[str(e)[:220] for e in errors])
y=YAML(typ='safe');old=y.load((p/'dsi-original.yaml').read_text());new=y.load((p/'dsi-proposed.yaml').read_text());new['properties']['compatible']['oneOf'][0]['enum'].remove('mediatek,mt8163-dsi');new['allOf'].pop();assert old==new
result={'scope':'Actual disabled candidate missing panel graph remains rejected by selected schema; synthetic graph is shape only','count':len(cases),'older_soc_structure_preserved':True,'type_policy_pipeline_retained':True,'actual_candidate_accepted':False,'synthetic_graph_not_actual_panel':True,'runtime_qualified':False}
a=argparse.ArgumentParser();a.add_argument('--check',action='store_true');args=a.parse_args()
if args.check:assert result==json.loads((p/'controls.json').read_text())
else:(p/'controls.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(cases),'DSI type/policy controls; actual missing graph rejected')
