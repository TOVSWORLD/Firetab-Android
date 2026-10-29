import hashlib,json,re,shutil,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import apply_pwm_port as port
from audit_pwm_port import run
from audit_disp_pwm_source import function
P=ROOT/'projects/firetabs-android/kernel/pwm-port'
def fixture(root):
 lock=json.loads((P/'inputs.json').read_text())
 for row in lock['files']+lock['build_inputs']:
  if 'original_sha256'in row and row['original_sha256'] is None:continue
  p=root/row['target'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/row['source']).read_bytes())
 return lock
class PwmPort(unittest.TestCase):
 def test_actual_patched_core_callback_and_cleanup_ram(self):self.assertTrue(run()['native_passed'])
 def test_all_target_revision_source_header_definition_patch_output_negatives(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/'tree';lock=fixture(root);targets=[root/x['target'] for x in lock['files']];before=[p.read_bytes() if p.exists() else None for p in targets]
   def unchanged():self.assertEqual(before,[p.read_bytes() if p.exists() else None for p in targets])
   with self.assertRaises(ValueError):port.apply(root,'wrong')
   unchanged()
   for row in lock['files'][:1]+lock['build_inputs']:
    p=root/row['target'];b=p.read_bytes();p.write_bytes(b+b'\n')
    with self.assertRaises(ValueError):port.apply(root,lock['ack_commit'])
    p.write_bytes(b);unchanged()
   targets[1].parent.mkdir(parents=True,exist_ok=True);targets[1].write_bytes(b'existing')
   with self.assertRaises(ValueError):port.apply(root,lock['ack_commit'])
   targets[1].unlink();unchanged()
   bad=json.loads(json.dumps(lock));bad['files'][0]['patched_sha256']='0'*64;loads=json.loads
   with patch.object(port.json,'loads',side_effect=lambda s:bad if s==(P/'inputs.json').read_text() else loads(s)):
    with self.assertRaises(ValueError):port.apply(root,lock['ack_commit'])
   unchanged()
   copied=Path(tmp)/'port';shutil.copytree(P,copied)
   with patch.object(port,'PORT',copied):
    for name in ['variant-definition.json',lock['patch']]:
     p=copied/name;b=p.read_bytes();p.write_bytes(b+b'\n')
     with self.assertRaises(ValueError):port.apply(root,lock['ack_commit'])
     p.write_bytes(b);unchanged()
   repo=Path(tmp)/'repo'
   for row in lock['files']+lock['build_inputs']:
    p=repo/row['source'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/row['source']).read_bytes())
   helper=repo/lock['files'][1]['source'];helper.write_bytes(helper.read_bytes()+b'\n')
   with patch.object(port,'ROOT',repo):
    with self.assertRaises(ValueError):port.apply(root,lock['ack_commit'])
   unchanged();port.apply(root,lock['ack_commit']);after=[p.read_bytes() for p in targets]
   with self.assertRaises(ValueError):port.apply(root,lock['ack_commit'])
   self.assertEqual(after,[p.read_bytes() for p in targets])
 def test_original_bodies_descriptors_and_ops_preserved(self):
  with tempfile.TemporaryDirectory() as tmp:
   tree=Path(tmp);lock=fixture(tree);port.apply(tree,lock['ack_commit']);s=(tree/lock['files'][0]['target']).read_text();old=(ROOT/'evidence/disp-pwm-source/ack-pwm-mtk-disp.c').read_text()
   for name in ['to_mtk_disp_pwm','mtk_disp_pwm_update_bits','mtk_disp_pwm_apply','mtk_disp_pwm_get_state','mtk_disp_pwm_probe']:
    body=function(old,name);self.assertTrue(body in s or body.replace(name+'(',name+'_legacy(',1) in s,name)
   for d in re.findall(r'static const struct mtk_pwm_data \w+ = \{.*?\n};',old,re.S):self.assertIn(d,s)
   self.assertIn(re.search(r'static const struct pwm_ops mtk_disp_pwm_ops = \{.*?\n};',old,re.S).group(),s)
   self.assertIn('mediatek,mt8163-disp-pwm',s)
 def test_source_policy_build_real_target_and_final_marker(self):
  p=json.loads((P/'variant-definition.json').read_text());self.assertEqual((p['divider_mask'],p['period_mask'],p['duty_mask']),(1023,1023,8191));self.assertEqual(p['resource_minimum_bytes'],24)
  s=(ROOT/'scripts/build_pwm_provider.sh').read_text()
  for x in ['PWM_MTK_DISP','drivers/pwm/pwm-mtk-disp.o','MT8163_PWM_PROVIDER_IMAGE_COMPLETE_RUNTIME_UNQUALIFIED','build_dsi_provider.sh']:self.assertIn(x,s)
