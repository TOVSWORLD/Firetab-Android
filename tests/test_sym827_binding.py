import json
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate_douglas_bindings import apply_locked_proposal
E=ROOT/'evidence/sym827-binding'


class Sym827Binding(unittest.TestCase):
    def test_locked_patch_and_source_build_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp);schema=source/'regulator/fcs,fan53555.yaml';schema.parent.mkdir();schema.write_bytes((E/'fan53555-original.yaml').read_bytes());original=schema.read_bytes()
            with self.assertRaises(ValueError):apply_locked_proposal(source,'wrong','mt8163-sym827.json')
            self.assertEqual(schema.read_bytes(),original)
            apply_locked_proposal(source,'d9318bdb4c34e8b2d997b4f67ced56b120b22b87','mt8163-sym827.json')
            self.assertEqual(schema.read_bytes(),(E/'fan53555-proposed.yaml').read_bytes())
            with self.assertRaises(ValueError):apply_locked_proposal(source,'d9318bdb4c34e8b2d997b4f67ced56b120b22b87','mt8163-sym827.json')
        build=json.loads((ROOT/'evidence/sym827-port/build-result.json').read_text());lock=json.loads((ROOT/'projects/firetabs-android/kernel/regulator-port/inputs.json').read_text())
        self.assertTrue(build['passed']);self.assertEqual(build['repository_head'],'dec1a898f0f49782cff96daaa61b6f364d6930b4');self.assertEqual(build['final_hashes']['source/drivers/regulator/fan53555.c'],lock['patched_sha256']);self.assertFalse(build['runtime_qualified'])

    def test_exact_diagnostic_deltas_and_preserved_full_failures(self):
        for kind,before,after in [('canonical',33,32),('isolated',27,26)]:
            delta=json.loads((E/(kind+'-delta.json')).read_text());report=json.loads((E/(kind+'-report.json')).read_text())
            self.assertEqual((delta['before'],delta['after']),(before,after));self.assertEqual(len(delta['removed']),1);self.assertEqual(delta['removed'][0]['node'],'/soc/i2c@11008000/regulator@60');self.assertEqual(delta['removed'][0]['type'],'unmatched');self.assertFalse(delta['added']);self.assertFalse(report['passed']);self.assertEqual(report['wrapper_exit'],1)
            diagnostics=json.loads((E/(kind+'-diagnostics.json')).read_text());self.assertEqual(len(diagnostics),after);self.assertTrue(any(x['node']=='/soc/clock-controller@11220000/audio-controller' and x['type']=='unmatched' for x in diagnostics))
        contract=json.loads((E/'source-contract.json').read_text())
        for path,expected in contract['sha256'].items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),expected)
        self.assertEqual((E/'doc-validate.stderr').read_bytes(),b'')
        controls=json.loads((E/'controls.json').read_text());self.assertEqual(controls['count'],22);self.assertTrue(controls['older_soc_policy_structurally_preserved']);self.assertFalse(controls['runtime_qualified'])
