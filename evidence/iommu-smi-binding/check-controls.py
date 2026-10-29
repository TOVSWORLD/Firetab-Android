import copy,json
from pathlib import Path
from dtschema import DTValidator
from referencing import Registry
from referencing.jsonschema import DRAFT201909
out=Path(__file__).resolve().parent;root=out.parents[1]
cases=[]
for kind,paths in [('iommu',['/soc/iommu@10205000']),('smi-common',['/soc/smi@14017000']),('smi-larb',['/soc/larb@14016000','/soc/larb@16010000','/soc/larb@15001000','/soc/larb@17001000'])]:
 bundle=json.loads((out/(kind+'-processed-schemas.json')).read_text());schemas=bundle['schemas']
 registry=Registry().with_resources((uri,DRAFT201909.create_resource(schema)) for uri,schema in schemas.items())
 validator=DTValidator.DtValidator(schemas[bundle['root']],registry=registry)
 nodes=json.loads((out/(kind+'-captured-nodes.json')).read_text())
 for path in paths:
  base=nodes[path]
  def run(name,changes,expected):
   n=copy.deepcopy(base)
   for k,value in changes.items():
    if value is None:n.pop(k,None)
    else:n[k]=value
   actual=validator.is_valid(n);assert actual==expected,(kind,path,name,[str(e)[:300] for e in validator.iter_errors(n)])
   cases.append({'node':path,'name':name,'accepted':actual,'expected':expected})
  
  if kind=='smi-larb':
   run('actual candidate rejects unsupported IRQ',{},False)
   base=copy.deepcopy(base);base.pop('interrupts')
  run('decoded candidate without unused IRQ' if kind=='smi-larb' else 'actual decoded candidate',{},True);run('missing reg',{'reg':None},False);run('unknown compatible',{'compatible':['mediatek,mt0000-'+kind]},False)
  if kind=='iommu':
   run('missing IRQ',{'interrupts':None},False);run('missing larbs',{'mediatek,larbs':None},False);run('wrong IOMMU cells',{'#iommu-cells':2},False)
   run('no unnecessary bclk or infracfg',{'clocks':None,'mediatek,infracfg':None},True)
   run('existing mt8167',{'compatible':['mediatek,mt8167-m4u']},True)
  else:
   run('missing clocks',{'clocks':None},False);run('missing power domain',{'power-domains':None},False);run('reversed clock names',{'clock-names':['smi','apb']},False);run('extra clock role',{'clock-names':['apb','smi','async']},False)
   if kind=='smi-common':run('existing mt8173',{'compatible':['mediatek,mt8173-smi-common']},True)
   if kind=='smi-larb':run('existing mt8173 ID4',{'compatible':['mediatek,mt8173-smi-larb'],'mediatek,larb-id':4},True);run('missing common supplier',{'mediatek,smi':None},False);run('out of range larb ID',{'mediatek,larb-id':4},False)
(out/'controls.json').write_text(json.dumps({'scope':'Actual decoded-node controls; actual larb IRQ rejection retained; no hardware qualification','cases':cases,'passed':True,'runtime_qualified':False},indent=2)+'\n');print('PASS',len(cases),'actual decoded-node controls')

y=__import__('ruamel.yaml',fromlist=['YAML']).YAML(typ='safe')
for kind in ['iommu','smi-common','smi-larb']:
 original=y.load((out/(kind+'-original.yaml')).read_text());proposal=y.load((out/(kind+'-proposed.yaml')).read_text())
 compatible='mediatek,mt8163-'+('m4u' if kind=='iommu' else kind)
 proposal['properties']['compatible']['oneOf'][0]['enum'].remove(compatible)
 if kind=='smi-common':proposal['allOf'][-1]['if']['properties']['compatible']['enum'].remove(compatible)
 if kind=='smi-larb':proposal['allOf'].pop()
 assert proposal==original,kind
print('PASS: all original SoC constraints preserved structurally')
