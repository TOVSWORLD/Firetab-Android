"""Check actual processed compatible tuples with the pinned local schema environment."""
import json
from pathlib import Path
from ruamel.yaml import YAML
from jsonschema import Draft7Validator
root = Path(__file__).resolve().parent
yaml = YAML(typ='safe')
result = []
for name, fallback, previous in [('mt8163-mmc', 'mt2701-mmc', 'mt7623-mmc'),
                                  ('mt8163-uart-dma', 'mt6577-uart-dma', 'mt8365-uart-dma')]:
    folder = root/name
    validator = Draft7Validator(json.loads((folder/'processed-compatible.json').read_text()))
    first, second = 'mediatek,'+name, 'mediatek,'+fallback
    cases = [([first, second], True), ([first], False), ([first, 'mediatek,wrong'], False),
             ([first, second, 'extra'], False), (['mediatek,'+previous, second], True), ([second], True)]
    checked = []
    for data, expected in cases:
        actual = validator.is_valid(data)
        assert actual == expected, (name, data)
        checked.append({'compatible': data, 'accepted': actual, 'expected': expected})
    original = yaml.load((folder/'original.yaml').read_text())
    proposed = yaml.load((folder/'proposed.yaml').read_text())
    if name == 'mt8163-mmc':
        proposed['properties']['compatible']['oneOf'][1]['items'][0] = {'const': 'mediatek,mt7623-mmc'}
    else:
        proposed['properties']['compatible']['oneOf'][0]['items'][0]['enum'].remove(first)
    assert proposed == original
    result.append({'proposal': name, 'cases': checked, 'all_other_constraints_preserved': True})
(root/'controls.json').write_text(json.dumps({'results': result, 'passed': True}, indent=2)+'\n')
