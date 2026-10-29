import importlib.util
from pathlib import Path
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('usb_resource_bindings',ROOT/'scripts/validate_douglas_bindings.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class USBResourceBindings(unittest.TestCase):
    def test_actual_locked_profiles_and_no_broad_old_soc_resource_change(self):
        evidence=ROOT/'evidence/usb-resource-binding'
        for kind,relative in [('musb','usb/mediatek,musb.yaml'),('tphy','phy/mediatek,tphy.yaml')]:
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as directory:
                root=Path(directory);schema=root/relative;schema.parent.mkdir(parents=True)
                schema.write_bytes((evidence/(kind+'-original.yaml')).read_bytes())
                module.apply_locked_proposal(root,'d9318bdb4c34e8b2d997b4f67ced56b120b22b87','mt8163-'+kind+'.json')
                proposed=schema.read_bytes();self.assertEqual(proposed,((ROOT/'evidence/usb-analog-binding/tphy-proposed.yaml') if kind=='tphy' else evidence/(kind+'-proposed.yaml')).read_bytes())
                if kind=='tphy':
                    self.assertIn(b'    minItems: 1\n    maxItems: 2',proposed)
                    self.assertIn(b'    else:\n      properties:\n        reg:\n          maxItems: 1\n        reg-names: false',proposed)
                    self.assertIn(b'            mediatek,eye-src: false',proposed)
                    for field in ['vrt','term']:
                        self.assertIn(('            mediatek,eye-'+field+':\n              const: 7').encode(),proposed)
                with self.assertRaises(ValueError):module.apply_locked_proposal(root,'d9318bdb4c34e8b2d997b4f67ced56b120b22b87','mt8163-'+kind+'.json')

    def test_wrong_revision_or_source_drift_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);schema=root/'phy/mediatek,tphy.yaml';schema.parent.mkdir();schema.write_bytes((ROOT/'evidence/usb-resource-binding/tphy-original.yaml').read_bytes())
            with self.assertRaises(ValueError):module.apply_locked_proposal(root,'wrong','mt8163-tphy.json')
            schema.write_bytes(schema.read_bytes()+b'\n')
            with self.assertRaises(ValueError):module.apply_locked_proposal(root,'d9318bdb4c34e8b2d997b4f67ced56b120b22b87','mt8163-tphy.json')
