"""Actual processed compatible controls; preserve all non-compatible constraints."""
import json
from pathlib import Path
from jsonschema import Draft7Validator
from ruamel.yaml import YAML
root=Path(__file__).resolve().parent
validator=Draft7Validator(json.loads((root/'processed-compatible.json').read_text()))
cases=[(['mediatek,mt8163-topckgen'],True),
       (['mediatek,mt8163-topckgen','syscon'],False),
       (['mediatek,mt8163-topckgen','mediatek,mt8173-topckgen'],False),
       (['mediatek,mt8163-topckgen','extra'],False),
       (['mediatek,unknown-topckgen'],False),
       (['mediatek,mt8173-topckgen'],True),
       (['mediatek,mt8167-topckgen','syscon'],True)]
results=[]
for value,expected in cases:
    actual=validator.is_valid(value)
    assert actual==expected,value
    results.append({'compatible':value,'accepted':actual,'expected':expected})
yaml=YAML(typ='safe');original=yaml.load((root/'original.yaml').read_text());proposed=yaml.load((root/'proposed.yaml').read_text())
proposed['properties']['compatible']['oneOf'][0]['enum'].remove('mediatek,mt8163-topckgen')
assert original==proposed
(root/'controls.json').write_text(json.dumps({'cases':results,'all_other_constraints_preserved':True,'passed':True},indent=2)+'\n')
print('PASS:7 actual processed tuple controls and exact preservation of other constraints')
