import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('dsi_audit',ROOT/'scripts/audit_dsi_source.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)


class DsiSource(unittest.TestCase):
    def test_actual_c_lifecycle_queue_witnesses_and_no_admission(self):
        r=audit.audit();self.assertEqual(r,json.loads((ROOT/'evidence/dsi-source/result.json').read_text()));self.assertTrue(r['ack_and_donor_discard_phy_poweron_error']);self.assertTrue(r['invalid_format_reference_retained']);self.assertEqual(r['queue_max_payload_source_bound'],508);self.assertFalse(r['dsi_kernel_variant_implemented']);self.assertFalse(r['runtime_qualified'])

    def test_source_drift_rejects_before_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);e=root/'evidence/dsi-source';shutil.copytree(ROOT/'evidence/dsi-source',e);p=e/'ack-mtk_dsi.c';p.write_bytes(p.read_bytes()+b'\n')
            with patch.object(audit,'ROOT',root),patch.object(audit,'E',e),patch.object(audit.subprocess,'run') as call:
                with self.assertRaises(ValueError):audit.audit()
                call.assert_not_called()
