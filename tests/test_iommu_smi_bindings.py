import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('iommu_smi_bindings', ROOT/'scripts/validate_douglas_bindings.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class IOMMUSMIBindings(unittest.TestCase):
    def test_actual_locked_proposals_and_no_irq_suppression(self):
        evidence = ROOT/'evidence/iommu-smi-binding'
        for kind, relative in [('iommu', 'iommu/mediatek,iommu.yaml'),
                               ('smi-common', 'memory-controllers/mediatek,smi-common.yaml'),
                               ('smi-larb', 'memory-controllers/mediatek,smi-larb.yaml')]:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                schema = root/relative
                schema.parent.mkdir(parents=True)
                original = (evidence/(kind+'-original.yaml')).read_bytes()
                schema.write_bytes(original)
                module.apply_locked_proposal(root, 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87', 'mt8163-'+kind+'.json')
                proposed = schema.read_bytes()
                self.assertEqual(proposed, (evidence/(kind+'-proposed.yaml')).read_bytes())
                if kind == 'smi-larb':
                    self.assertNotIn(b'  interrupts:', proposed)
                    self.assertIn(b'additionalProperties: false', proposed)
                    self.assertIn(b'        - mediatek,smi', proposed)
                with self.assertRaises(ValueError):
                    module.apply_locked_proposal(root, 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87', 'mt8163-'+kind+'.json')

    def test_revision_or_original_drift_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            schema = root/'iommu/mediatek,iommu.yaml'
            schema.parent.mkdir()
            schema.write_bytes((ROOT/'evidence/iommu-smi-binding/iommu-original.yaml').read_bytes())
            with self.assertRaises(ValueError):
                module.apply_locked_proposal(root, 'wrong', 'mt8163-iommu.json')
            schema.write_bytes(schema.read_bytes()+b'\n')
            with self.assertRaises(ValueError):
                module.apply_locked_proposal(root, 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87', 'mt8163-iommu.json')
