import copy,json
from pathlib import Path
from dtschema import DTValidator
from referencing import Registry
from referencing.jsonschema import DRAFT201909
from ruamel.yaml import YAML
out=Path(__file__).resolve().parent
cases=[]
for kind,paths in [('musb',['/soc/usb@11200000','/soc/usb@11270000']),('tphy',['/soc/t-phy@11210000'])]:
 bundle=json.loads((out/(kind+'-processed-schemas.json')).read_text());schemas=bundle['schemas']
 registry=Registry().with_resources((uri,DRAFT201909.create_resource(schema)) for uri,schema in schemas.items())
 validator=DTValidator.DtValidator(schemas[bundle['root']],registry=registry)
 nodes=json.loads((out/(kind+'-captured-nodes.json')).read_text())
 for path in paths:
  base=nodes[path]
  def run(name,changes,expected):
   node=copy.deepcopy(base)
   for key,val in changes.items():
    if val is None:node.pop(key,None)
    else:node[key]=val
   actual=validator.is_valid(node);assert actual==expected,(name,[str(e)[:300] for e in validator.iter_errors(node)])
   cases.append({'node':path,'name':name,'accepted':actual,'expected':expected})
  run('actual disabled metadata; no runtime admission',{},True)
  run('missing reg',{'reg':None},False)
  if kind=='musb':
   run('missing PHY',{'phys':None},False);run('wrong clock order',{'clock-names':['mcu','main','univpll']},False);run('missing IRQ',{'interrupts':None},False)
   run('existing mt2701 contract',{'compatible':['mediatek,mt2701-musb','mediatek,mtk-musb']},True)
  else:
   run('missing frequency bank',{'reg':base['reg'][:1]},False)
   run('missing names',{'reg-names':None},False)
   run('wrong names',{'reg-names':['u2-frequency','sif']},False)
   run('extra resource',{'reg':base['reg']+[base['reg'][1]]},False)
   run('unused reference override',{'mediatek,src-ref-clk-mhz':48},False)
   run('unused coefficient override',{'mediatek,src-coef':28},False)
   child=copy.deepcopy(base['usb-phy@11210800']);child['mediatek,eye-src']=6
   run('child EYE bypass forbidden',{'usb-phy@11210800':child},False)
   child['mediatek,eye-src']=0;run('explicit zero EYE presence forbidden',{'usb-phy@11210800':child},False)
   run('old V1 one resource retained',{'compatible':['mediatek,mt2701-tphy','mediatek,generic-tphy-v1'],'reg':base['reg'][:1],'reg-names':None},True)
   run('old V1 still rejects two resources',{'compatible':['mediatek,mt2701-tphy','mediatek,generic-tphy-v1'],'reg-names':None},False)
   run('old V2 optional reg retained',{'compatible':['mediatek,mt2712-tphy','mediatek,generic-tphy-v2'],'reg':None,'reg-names':None},True)
y=YAML(typ='safe')
for kind in ['musb','tphy']:
 old=y.load((out/(kind+'-original.yaml')).read_text());new=y.load((out/(kind+'-proposed.yaml')).read_text())
 if kind=='musb':new['properties']['compatible']['items'][0]['enum'].remove('mediatek,mt8163-musb')
 else:
  new['properties']['compatible']['oneOf'][0]['items'][0]['enum'].remove('mediatek,mt8163-tphy');new['properties']['reg']['maxItems']=1;new['properties']['reg'].pop('minItems');new['properties'].pop('reg-names');new.pop('allOf')
 assert new==old,kind
(out/'controls.json').write_text(json.dumps({'scope':'Schema metadata only, not driver readiness; disabled USB1/port1 remains unsupported','cases':cases,'prior_constraints_preserved':True,'passed':True,'runtime_qualified':False},indent=2)+'\n');print('PASS',len(cases),'actual decoded-node controls and prior-SoC structure')
