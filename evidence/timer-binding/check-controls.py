"""Local schema negative controls; run using the pinned dtschema environment."""
import json
from pathlib import Path
from ruamel.yaml import YAML
from jsonschema import Draft7Validator
root = Path(__file__).resolve().parent
yaml = YAML(typ='safe')
original = yaml.load((root/'original.yaml').read_text())
proposed = yaml.load((root/'proposed.yaml').read_text())
# dtschema adds tuple min/max bounds during schema processing. Use its
# actual processed schema rather than treating YAML tuple syntax as draft2020.
validator = Draft7Validator(json.loads((root/'processed-compatible.json').read_text()))
cases = [(['mediatek,mt8163-timer', 'mediatek,mt6577-timer'], True),
         (['mediatek,mt8163-timer'], False),
         (['mediatek,mt8163-timer', 'mediatek,wrong-timer'], False),
         (['mediatek,mt8163-timer', 'mediatek,mt6577-timer', 'extra'], False),
         (['mediatek,mt8173-timer', 'mediatek,mt6577-timer'], True)]
results = []
for data, expected in cases:
    actual = validator.is_valid(data)
    assert actual == expected
    results.append({'compatible': data, 'accepted': actual, 'expected': expected})
proposed['properties']['compatible']['oneOf'][1]['items'][0]['enum'].remove('mediatek,mt8163-timer')
assert proposed == original
(root/'controls.json').write_text(json.dumps({'cases': results, 'all_other_schema_constraints_preserved': True, 'passed': True}, indent=2)+'\n')
