"""Actual processed MT8163 non-bridge PMIC-wrapper contract controls."""
import copy
import json
from pathlib import Path
from dtschema import DTValidator
from referencing import Registry
from referencing.jsonschema import DRAFT201909
from ruamel.yaml import YAML
root=Path(__file__).resolve().parent
bundle=json.loads((root/'processed-schemas.json').read_text())
registry=Registry().with_resources((u,DRAFT201909.create_resource(s)) for u,s in bundle['schemas'].items())
v=DTValidator.DtValidator(bundle['schemas'][bundle['root']],registry=registry)
base={'compatible':['mediatek,mt8163-pwrap'],'reg':[[0x1000d000,4096]],'reg-names':['pwrap'],'interrupts':[[0,161,4]],'clocks':[[1,0],[2,1]],'clock-names':['spi','wrap'],'resets':[[3,7]],'reset-names':['pwrap'],'pmic':{'compatible':['mediatek,mt6323']}}
tests=[('exact-candidate',{},True)]
for k in ['reg','reg-names','interrupts','clocks','clock-names','resets','reset-names','pmic']:
 tests.append(('missing-'+k,{k:None},False))
tests += [('bridge-registers',{'reg':[[0,4096],[4096,4096]],'reg-names':['pwrap','pwrap-bridge']},False),('bridge-resets',{'resets':[[3,7],[3,8]],'reset-names':['pwrap','pwrap-bridge']},False),('wrong-mapping-name',{'reg-names':['other']},False),('wrong-reset-name',{'reset-names':['other']},False),('syscon-fallback',{'compatible':['mediatek,mt8163-pwrap','syscon']},False),('wrong-clock-order',{'clock-names':['wrap','spi']},False),('one-clock',{'clocks':[[1,0]],'clock-names':['spi']},False),('two-interrupts',{'interrupts':[[0,161,4],[0,162,4]]},False),('unexpected-power-domain',{'power-domains':[[1,0]]},False),('wrong-parent-child-name',{'pmic':None,'mt6323':base['pmic']},False),('existing-mt8135-bridge',{'compatible':['mediatek,mt8135-pwrap'],'reg':[[0,4096],[4096,4096]],'reg-names':['pwrap','pwrap-bridge'],'resets':[[3,7],[3,8]],'reset-names':['pwrap','pwrap-bridge']},True),('existing-mt2701-optional-reset-child',{'compatible':['mediatek,mt2701-pwrap'],'resets':None,'reset-names':None,'pmic':None},True),('existing-mt8173-power-domain',{'compatible':['mediatek,mt8173-pwrap'],'power-domains':[[1,0]]},True)]
cases=[]
for name,change,expected in tests:
 node=copy.deepcopy(base)
 for k,val in change.items():
  if val is None:node.pop(k,None)
  else:node[k]=val
 actual=v.is_valid(node);assert actual==expected,(name,list(v.iter_errors(node)))
 cases.append({'name':name,'accepted':actual,'expected':expected})
y=YAML(typ='safe');o=y.load((root/'original.yaml').read_text());p=y.load((root/'proposed.yaml').read_text());p['properties']['compatible']['oneOf'][0]['items'][0]['enum'].remove('mediatek,mt8163-pwrap');assert len(p['allOf'])==3;p['allOf'].pop(0);assert p==o
(root/'controls.json').write_text(json.dumps({'cases':cases,'all_unrelated_constraints_preserved':True,'passed':True,'limits':'Parent schema does not prove PMIC transport, first-child compatible support or voltage; full MFD schema and actual driver checks are separate'},indent=2)+'\n')
print('PASS:',len(cases),'actual dtschema controls; original constraints preserved')
