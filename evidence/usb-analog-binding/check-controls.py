import copy,json
from pathlib import Path
from dtschema import DTValidator
from referencing import Registry
from referencing.jsonschema import DRAFT201909
from ruamel.yaml import YAML
p=Path(__file__).resolve().parent
old=json.load(open(p/'portable-schemas.json'));root=old['root'];registry=Registry().with_resources((u,DRAFT201909.create_resource(s)) for u,s in old['schemas'].items());v=DTValidator.DtValidator(old['schemas'][root],registry=registry);base=json.load(open(p/'tphy-captured-nodes.json'))['/soc/t-phy@11210000'];cases=[]
def run(name,node,expected):
 actual=v.is_valid(node);assert actual==expected,(name,[str(e)[:300] for e in v.iter_errors(node)]);cases.append({'name':name,'accepted':actual,'expected':expected})
run('actual disabled candidate without overrides',base,True)
for prop in ['mediatek,eye-vrt','mediatek,eye-term']:
 for value in [0,1,2,3,4,5,6,7,8,[7],[7,1],'7']:
  n=copy.deepcopy(base);n['usb-phy@11210800'][prop]=value;run(prop+' '+str(value),n,value==7)
n=copy.deepcopy(base);n['usb-phy@11210800'].update({'mediatek,eye-vrt':7,'mediatek,eye-term':7});run('both vendor-equal overrides',n,True)
for value in [0,6,7]:
 n=copy.deepcopy(base);n['usb-phy@11210800']['mediatek,eye-src']=value;run('slew bypass '+str(value),n,False)
n=copy.deepcopy(base);n['compatible']=['mediatek,mt2701-tphy','mediatek,generic-tphy-v1'];n['reg']=n['reg'][:1];n.pop('reg-names');n['usb-phy@11210800']['mediatek,eye-vrt']=3;n['usb-phy@11210800']['mediatek,eye-term']=2;run('old SoC non-seven tuning retained',n,True)
y=YAML(typ='safe');a=y.load(Path('evidence/usb-resource-binding/tphy-proposed.yaml').read_text());b=y.load((p/'tphy-proposed.yaml').read_text());props=b['allOf'][0]['then']['patternProperties']['^(usb|pcie|sata)-phy@[0-9a-f]+$']['properties'];props.pop('mediatek,eye-vrt');props.pop('mediatek,eye-term');assert a==b
(p/'controls.json').write_text(json.dumps({'passed':True,'count':len(cases),'cases':cases,'other_policies_preserved':True,'runtime_qualified':False},indent=2)+'\n');print('PASS',len(cases),'actual decoded-node controls and structural preservation')
