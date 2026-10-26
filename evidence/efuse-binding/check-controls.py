"""Actual processed efuse tuple controls; preserve decoding-specific branches."""
import json
from pathlib import Path
from jsonschema import Draft7Validator
from ruamel.yaml import YAML
root = Path(__file__).resolve().parent
validator = Draft7Validator(json.loads((root/'processed-compatible.json').read_text()))
cases = [(['mediatek,mt8163-efuse', 'mediatek,efuse'], True),
         (['mediatek,mt8163-efuse'], False),
         (['mediatek,mt8163-efuse', 'mediatek,mt8186-efuse'], False),
         (['mediatek,mt8163-efuse', 'mediatek,efuse', 'extra'], False),
         (['mediatek,mt8173-efuse', 'mediatek,efuse'], True),
         (['mediatek,mt8173-efuse'], True),
         (['mediatek,mt8188-efuse', 'mediatek,mt8186-efuse'], True),
         (['mediatek,mt8186-efuse'], True),
         (['mediatek,efuse'], False)]
checked = []
for value, expected in cases:
    actual = validator.is_valid(value)
    assert actual == expected, value
    checked.append({'compatible': value, 'accepted': actual, 'expected': expected})
yaml = YAML(typ='safe')
original = yaml.load((root/'original.yaml').read_text())
proposed = yaml.load((root/'proposed.yaml').read_text())
branches = proposed['properties']['compatible']['oneOf']
found = [b for b in branches if 'items' in b and 'mediatek,mt8163-efuse' in b['items'][0].get('enum', [])]
assert len(found) == 1
found[0]['items'][0]['enum'].remove('mediatek,mt8163-efuse')
assert proposed == original
(root/'controls.json').write_text(json.dumps({'cases': checked, 'all_other_constraints_preserved': True, 'passed': True}, indent=2)+'\n')
