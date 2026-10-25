import json
from pathlib import Path
from ruamel.yaml import YAML
yaml=YAML(typ="safe")
from jsonschema import Draft202012Validator
root=Path.cwd()
proposed=yaml.load((root/'evidence/pmic-domain-selector/proposed.yaml').read_text())
original=yaml.load((root/'evidence/pmic-domain-selector/original.yaml').read_text())
mfd=yaml.load((root/'evidence/pmic-dt/ack/Documentation/devicetree/bindings/mfd/mediatek,mt6397.yaml').read_text())
selector=Draft202012Validator(proposed['select'])
cases=[('mt6323_sys_off',{'$nodename':'power-controller','compatible':['mediatek,mt6323-pwrc']},False),('generic_without_cells',{'$nodename':'power-controller','compatible':['vendor,real-domain']},True),('unnamed_compatible_absent',{'$nodename':'power-controller'},True),('different_node',{'$nodename':'uart'},False)]
results=[]
for name,data,expected in cases:
 actual=selector.is_valid(data)
 assert actual==expected
 results.append({'case':name,'selector_matches':actual,'expected':expected})
assert not Draft202012Validator(proposed).is_valid({'$nodename':'power-controller','compatible':['vendor,real-domain']})
child=mfd['properties']['power-controller']
assert Draft202012Validator(child).is_valid({'compatible':'mediatek,mt6323-pwrc'})
assert not Draft202012Validator(child).is_valid({'compatible':'mediatek,mt6323-pwrc','invented-property':True})
assert not Draft202012Validator(child).is_valid({'compatible':'vendor,wrong'})
a={k:v for k,v in proposed.items() if k!='select'}
assert a==original
out={'scope':'Actual YAML/jsonschema selector/constraint negative controls; no hardware validation','selector_cases':results,'generic_provider_missing_cells_still_rejected':True,'mfd_child_valid_sys_off_accepted':True,'mfd_child_unknown_property_rejected':True,'mfd_child_wrong_compatible_rejected':True,'all_original_domain_constraints_preserved':True,'passed':True}
(root/'evidence/pmic-domain-selector/controls.json').write_text(json.dumps(out,indent=2)+'\n')
