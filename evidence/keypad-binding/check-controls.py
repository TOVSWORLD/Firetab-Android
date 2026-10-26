"""Validate exact tuple coverage against actual processed compatible schema."""
import json
from pathlib import Path
from jsonschema import Draft7Validator
from ruamel.yaml import YAML
root = Path(__file__).resolve().parent
validator = Draft7Validator(json.loads((root/'processed-compatible.json').read_text()))
cases = [(['mediatek,mt8163-keypad', 'mediatek,mt6779-keypad'], True),
         (['mediatek,mt8163-keypad'], False),
         (['mediatek,mt8163-keypad', 'mediatek,wrong'], False),
         (['mediatek,mt8163-keypad', 'mediatek,mt6779-keypad', 'extra'], False),
         (['mediatek,mt8183-keypad', 'mediatek,mt6779-keypad'], True),
         (['mediatek,mt6779-keypad'], True)]
results = []
for data, expected in cases:
    accepted = validator.is_valid(data)
    assert accepted == expected, data
    results.append({'compatible': data, 'accepted': accepted, 'expected': expected})
yaml = YAML(typ='safe')
original = yaml.load((root/'original.yaml').read_text())
proposed = yaml.load((root/'proposed.yaml').read_text())
proposed['properties']['compatible']['oneOf'][1]['items'][0]['enum'].remove('mediatek,mt8163-keypad')
assert proposed == original
(root/'controls.json').write_text(json.dumps({'cases': results, 'all_other_constraints_preserved': True, 'passed': True}, indent=2)+'\n')
