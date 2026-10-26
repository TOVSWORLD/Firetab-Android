"""Actual processed GCE tuple controls; preserve all non-compatible constraints."""
import json
from pathlib import Path
from jsonschema import Draft7Validator
from ruamel.yaml import YAML
root = Path(__file__).resolve().parent
validator = Draft7Validator(json.loads((root/'processed-compatible.json').read_text()))
cases = [(['mediatek,mt8163-gce', 'mediatek,mt8173-gce'], True),
         (['mediatek,mt8163-gce'], False),
         (['mediatek,mt8163-gce', 'mediatek,mt8183-gce'], False),
         (['mediatek,mt8163-gce', 'mediatek,mt8173-gce', 'extra'], False),
         (['mediatek,mt6795-gce', 'mediatek,mt8173-gce'], True),
         (['mediatek,mt8173-gce'], True), (['mediatek,mt8183-gce'], True)]
results = []
for value, expected in cases:
    actual = validator.is_valid(value)
    assert actual == expected, value
    results.append({'compatible': value, 'accepted': actual, 'expected': expected})
yaml = YAML(typ='safe')
original = yaml.load((root/'original.yaml').read_text())
proposed = yaml.load((root/'proposed.yaml').read_text())
first = proposed['properties']['compatible']['oneOf'][1]['items'][0]
assert first == {'enum': ['mediatek,mt6795-gce', 'mediatek,mt8163-gce']}
first.clear()
first['const'] = 'mediatek,mt6795-gce'
assert original == proposed
(root/'controls.json').write_text(json.dumps({'cases': results, 'all_other_constraints_preserved': True, 'passed': True}, indent=2)+'\n')
