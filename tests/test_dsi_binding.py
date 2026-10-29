import copy,hashlib,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate_douglas_bindings import apply_locked_proposal
import validate_dsi_dependencies as guard
E=ROOT/'evidence/dsi-binding'
class DsiBinding(unittest.TestCase):
 def test_source_build_and_locked_patch(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'display/mediatek/mediatek,dsi.yaml';p.parent.mkdir(parents=True);p.write_bytes((E/'dsi-original.yaml').read_bytes());original=p.read_bytes()
   with self.assertRaises(ValueError):apply_locked_proposal(Path(tmp),'wrong','mt8163-dsi.json')
   self.assertEqual(p.read_bytes(),original);apply_locked_proposal(Path(tmp),'d9318bdb4c34e8b2d997b4f67ced56b120b22b87','mt8163-dsi.json');self.assertEqual(p.read_bytes(),(E/'dsi-proposed.yaml').read_bytes())
  build=json.loads((ROOT/'evidence/dsi-kernel-integration/build-result.json').read_text());lock=json.loads((ROOT/'projects/firetabs-android/kernel/dsi-port/inputs.json').read_text());self.assertTrue(build['passed']);self.assertEqual(build['repository_head'],'2109781474e29dd4f9ce5523fdaf7aa6c2bf2822')
  for row in lock['files']:self.assertEqual(build['final_hashes']['source/'+row['target']],row['patched_sha256'])
  for symbol in ['DRM_MEDIATEK','DRM_MIPI_DSI','DRM_PANEL','PHY_MTK_MIPI_DSI']:self.assertEqual(build['resolved_symbols'][symbol],'y')
 def test_actual_graph_and_dependency_negatives(self):
  graph=json.loads((E/'captured-graph.json').read_text());r=guard.validate(graph);self.assertTrue(r['missing_panel_graph']);self.assertFalse(r['runtime_qualified'])
  for key,val in [('reg',[0,0x14012000,0,0x3fc]),('interrupts',[0,194,8]),('clocks',[40,35,40,34,42]),('resets',[40,24]),('power-domains',[21,1]),('phys',[1]),('phy-names',['bad']),('status',['okay']),('assigned-clock-rates',[26000000])]:
   n=copy.deepcopy(graph);n['nodes'][guard.DSI][key]=val
   with self.assertRaises(ValueError,msg=key):guard.validate(n)
  n=copy.deepcopy(graph);n['nodes'][guard.DSI+'/port']={}
  with self.assertRaises(ValueError):guard.validate(n)
  for path,key,val in [('/soc/syscon@14000000','#reset-cells',[0]),('/soc/syscon@14000000','#clock-cells',[0]),('/soc/syscon@10006000/power-controller','#power-domain-cells',[0]),('/soc/syscon@14000000','status',['disabled'])]:
   n=copy.deepcopy(graph);n['nodes'][path][key]=val
   with self.assertRaises(ValueError):guard.validate(n)
 def test_controls_preserve_missing_graph_and_failed_contexts(self):
  c=json.loads((E/'controls.json').read_text());self.assertEqual(c['count'],40);self.assertFalse(c['actual_candidate_accepted']);self.assertTrue(c['older_soc_structure_preserved']);self.assertTrue(c['type_policy_pipeline_retained'])
  for kind,before,after in [('canonical',31,30),('isolated',25,24)]:
   d=json.loads((E/(kind+'-delta.json')).read_text());self.assertEqual((d['before'],d['after']),(before,after));self.assertEqual(d['removed'][0]['node'],guard.DSI);self.assertFalse(d['added']);self.assertFalse(d['full_passed'])
   ds=json.loads((E/(kind+'-diagnostics.json')).read_text());self.assertEqual(len(ds),after);self.assertTrue(any(x['node']=='/soc/clock-controller@11220000/audio-controller' and x['type']=='unmatched' for x in ds))
  for path,sha in json.loads((E/'source-contract.json').read_text())['sha256'].items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),sha)
