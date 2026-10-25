"""Actual processed tuple checks in the pinned local schema environment."""
import json
from pathlib import Path
from ruamel.yaml import YAML
from jsonschema import Draft7Validator
root = Path(__file__).resolve().parent
yaml = YAML(typ='safe')
result = []
for c in json.loads((root/'changes.json').read_text())['changes']:
    folder = root/c['name']
    validator = Draft7Validator(json.loads((folder/'processed-compatible.json').read_text()))
    first, second = 'mediatek,'+c['name'], 'mediatek,'+c['fallback']
    cases = [([first, second], True), ([first], False), ([first, 'mediatek,wrong'], False),
             ([first, second, 'extra'], False), (['mediatek,'+c['previous'], second], True), ([second], True)]
    checked = []
    for data, expected in cases:
        actual = validator.is_valid(data)
        assert actual == expected, (c['name'], data)
        checked.append({'compatible': data, 'accepted': actual, 'expected': expected})
    original = yaml.load((folder/'original.yaml').read_text())
    proposed = yaml.load((folder/'proposed.yaml').read_text())
    branches = proposed['properties']['compatible']['oneOf']
    if c['name'] == 'mt8163-spi':
        assert branches[1] == {'items': [{'const': first}, {'const': second}]}
        branches.pop(1)
    else:
        found = [x for x in branches if 'items' in x and first in x['items'][0].get('enum', [])]
        assert len(found) == 1
        found[0]['items'][0]['enum'].remove(first)
    assert proposed == original
    result.append({'proposal': c['name'], 'cases': checked, 'all_other_constraints_preserved': True})
(root/'controls.json').write_text(json.dumps({'results': result, 'passed': True}, indent=2)+'\n')
