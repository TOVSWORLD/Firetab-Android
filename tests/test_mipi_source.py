import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('mipi_audit',ROOT/'scripts/audit_mipi_source.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)


class MipiSource(unittest.TestCase):
    def test_actual_c_ram_boundaries_and_no_runtime_admission(self):
        r=audit.audit();self.assertEqual(r,json.loads((ROOT/'evidence/mipi-source/result.json').read_text()));self.assertEqual(r['controls']['legacy_donor_equal_states'],8192);self.assertEqual(r['controls']['integer_mhz_pcw_cases'],1201);self.assertFalse(r['phy_binding_admitted']);self.assertFalse(r['runtime_qualified'])

    def test_wrong_source_rejects_before_compilation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);e=root/'evidence/mipi-source';shutil.copytree(ROOT/'evidence/mipi-source',e);p=e/'donor-phy-mtk-mipi-dsi-mt8173.c';p.write_bytes(p.read_bytes()+b'\n')
            with patch.object(audit,'ROOT',root),patch.object(audit,'E',e),patch.object(audit.subprocess,'run') as call:
                with self.assertRaises(ValueError):audit.audit()
                call.assert_not_called()
