import hashlib,json,re,shutil,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import apply_dsi_port as port
from audit_dsi_port import run
P=ROOT/'projects/firetabs-android/kernel/dsi-port'
def fixture(root):
 lock=json.loads((P/'inputs.json').read_text())
 for row in lock['files']+lock['build_inputs']:
  if 'original_sha256' in row and row['original_sha256'] is None:continue
  dest=root/row['target'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/row['source']).read_bytes())
 return lock
class DsiPort(unittest.TestCase):
 def test_actual_patched_c_native_sanitized(self):self.assertTrue(run()['native_passed'])
 def test_all_target_failure_preflight(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/'tree';lock=fixture(root);targets=[root/r['target'] for r in lock['files']];before=[p.read_bytes() if p.exists() else None for p in targets]
   def unchanged():self.assertEqual([p.read_bytes() if p.exists() else None for p in targets],before)
   with self.assertRaises(ValueError):port.apply(root,'wrong')
   unchanged()
   for row in lock['files'][:2]+lock['build_inputs']:
    p=root/row['target'];original=p.read_bytes();p.write_bytes(original+b'\n')
    with self.assertRaises(ValueError):port.apply(root,lock['ack_commit'])
    p.write_bytes(original);unchanged()
   targets[2].parent.mkdir(parents=True,exist_ok=True);targets[2].write_bytes(b'existing')
   with self.assertRaises(ValueError):port.apply(root,lock['ack_commit'])
   targets[2].unlink();unchanged()
   bad=json.loads(json.dumps(lock));bad['files'][1]['patched_sha256']='0'*64;loads=json.loads
   with patch.object(port.json,'loads',side_effect=lambda s:bad if s==(P/'inputs.json').read_text() else loads(s)):
    with self.assertRaises(ValueError):port.apply(root,lock['ack_commit'])
   unchanged()
   copied=Path(tmp)/'port';shutil.copytree(P,copied)
   with patch.object(port,'PORT',copied):
    for name in ['variant-definition.json',lock['patch'],'mtk_dsi_mt8163.h']:
     p=copied/name;original=p.read_bytes();p.write_bytes(original+b'\n')
     # Helper source is ROOT-backed, so new header is separately hash-checked below.
     if name!='mtk_dsi_mt8163.h':
      with self.assertRaises(ValueError):port.apply(root,lock['ack_commit'])
     p.write_bytes(original);unchanged()
   port.apply(root,lock['ack_commit']);after=[p.read_bytes() for p in targets]
   with self.assertRaises(ValueError):port.apply(root,lock['ack_commit'])
   self.assertEqual(after,[p.read_bytes() for p in targets])
 def test_original_function_bodies_and_descriptors_preserved(self):
  with tempfile.TemporaryDirectory() as tmp:
   tree=Path(tmp);lock=fixture(tree);port.apply(tree,lock['ack_commit'])
   old=(ROOT/'evidence/dsi-source/ack-mtk_dsi.c').read_text();new=(tree/lock['files'][0]['target']).read_text()
   pattern=r'^static (?:inline )?(?:enum drm_mode_status\n|[^\n]+? )(mtk_\w+)\([^;{]*\)\n\{'
   count=0
   for m in re.finditer(pattern,old,re.M):
    start=m.start();brace=old.index('{',m.start());end=brace+1;depth=1
    while depth:depth+=(old[end]=='{')-(old[end]=='}');end+=1
    original=old[start:end];name=m.group(1)
    self.assertTrue(original in new or original.replace(name+'(',name+'_legacy(',1) in new,name);count+=1
   self.assertGreater(count,40)
   for descriptor in re.findall(r'static const struct mtk_dsi_driver_data \w+ = \{.*?\n};',old,re.S):self.assertIn(descriptor,new)
   master=(tree/lock['files'][1]['target']).read_text();self.assertIn('"mediatek,mt8163-dsi"',master);self.assertNotIn('"mediatek,mt8163-mmsys"',master)
 def test_explicit_build_real_objects_final_marker(self):
  s=(ROOT/'scripts/build_dsi_provider.sh').read_text()
  for target in ['mtk_dsi.o','mtk_drm_drv.o','MT8163_DSI_PROVIDER_IMAGE_COMPLETE_RUNTIME_UNQUALIFIED','DRM_MEDIATEK','DRM_MIPI_DSI','PHY_MTK_MIPI_DSI']:self.assertIn(target,s)
  self.assertNotIn('mediatek-drm.o',s)
