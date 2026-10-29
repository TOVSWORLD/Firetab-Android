import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('thermal_audit',ROOT/'scripts/audit_thermal_source.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)


class ThermalSource(unittest.TestCase):
    def test_actual_c_ram_findings_remain_finite_and_unadmitted(self):
        result=audit.audit();self.assertEqual(result,json.loads((ROOT/'evidence/thermal-source/result.json').read_text()));self.assertEqual(result['c_controls']['signed_slope_differences'],126);self.assertFalse(result['thermal_source_port_admitted']);self.assertFalse(result['binding_match_admitted']);self.assertFalse(result['runtime_qualified'])

    def test_source_drift_fails_before_c_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);e=root/'evidence/thermal-source';shutil.copytree(ROOT/'evidence/thermal-source',e)
            p=e/'ack-auxadc_thermal.c';p.write_bytes(p.read_bytes()+b'\n')
            with patch.object(audit,'ROOT',root),patch.object(audit,'E',e),patch.object(audit.subprocess,'run') as compile_call:
                with self.assertRaises(ValueError):audit.audit()
                compile_call.assert_not_called()
