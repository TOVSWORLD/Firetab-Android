import json,sys,tempfile,shutil,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import audit_disp_pwm_source as audit
class DisplayPwmSource(unittest.TestCase):
 def test_actual_pwm_core_legacy_ram_witnesses(self):
  r=audit.audit();self.assertEqual(r,json.loads((audit.E/'result.json').read_text()));self.assertFalse(r['kernel_variant_admitted']);self.assertEqual(r['candidate_status'],'okay');self.assertEqual(r['period_operation_equal'],16384);self.assertEqual(r['commit_operation_equal'],2)
 def test_pinned_source_drift_rejected_before_compilation(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);shutil.copytree(audit.E,root/'evidence/disp-pwm-source');shutil.copytree(ROOT/'evidence/mipi-source',root/'evidence/mipi-source');shutil.copytree(ROOT/'evidence/dsi-binding',root/'evidence/dsi-binding');p=root/'evidence/disp-pwm-source/ack-pwm-mtk-disp.c';p.write_bytes(p.read_bytes()+b'\n')
   with patch.object(audit,'ROOT',root),patch.object(audit,'E',root/'evidence/disp-pwm-source'),patch.object(audit.subprocess,'run',side_effect=AssertionError('compiler must not run')):
    with self.assertRaises(ValueError):audit.audit()
