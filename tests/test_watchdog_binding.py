import importlib.util
from pathlib import Path
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('watchdog_bindings',ROOT/'scripts/validate_douglas_bindings.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class WatchdogBinding(unittest.TestCase):
    def test_patch_changes_only_new_soc_contract(self):
        evidence=ROOT/'evidence/watchdog-binding'
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);schema=root/'watchdog/mediatek,mtk-wdt.yaml';schema.parent.mkdir()
            original=(evidence/'original.yaml').read_bytes();schema.write_bytes(original)
            module.apply_locked_proposal(root,'d9318bdb4c34e8b2d997b4f67ced56b120b22b87','mt8163-watchdog.json')
            proposed=schema.read_bytes();self.assertEqual(proposed,(evidence/'proposed.yaml').read_bytes())
            addition=b'''  - if:
      properties:
        compatible:
          contains:
            const: mediatek,mt8163-wdt
    then:
      properties:
        timeout-sec:
          minimum: 2
          maximum: 31
'''
            self.assertEqual(proposed.replace(b'          - mediatek,mt8163-wdt\n',b'').replace(addition,b''),original)
            with self.assertRaises(ValueError):module.apply_locked_proposal(root,'d9318bdb4c34e8b2d997b4f67ced56b120b22b87','mt8163-watchdog.json')

    def test_wrong_revision_or_input_cannot_apply(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);schema=root/'watchdog/mediatek,mtk-wdt.yaml';schema.parent.mkdir()
            schema.write_bytes((ROOT/'evidence/watchdog-binding/original.yaml').read_bytes())
            with self.assertRaises(ValueError):module.apply_locked_proposal(root,'wrong','mt8163-watchdog.json')
            schema.write_bytes(schema.read_bytes()+b'\n')
            with self.assertRaises(ValueError):module.apply_locked_proposal(root,'d9318bdb4c34e8b2d997b4f67ced56b120b22b87','mt8163-watchdog.json')
