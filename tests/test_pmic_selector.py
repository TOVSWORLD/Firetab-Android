import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pmic_bindings', ROOT/'scripts/validate_douglas_bindings.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PMICSelector(unittest.TestCase):
    def test_locked_proposal_adds_only_select_and_preserves_constraints(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'power/power-domain.yaml'
            path.parent.mkdir()
            original = (ROOT/'evidence/pmic-domain-selector/original.yaml').read_bytes()
            path.write_bytes(original)
            module.apply_locked_proposal(Path(d), 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87', 'pmic-domain-selector.json')
            proposed = path.read_bytes()
            self.assertEqual(proposed, (ROOT/'evidence/pmic-domain-selector/proposed.yaml').read_bytes())
            start, end = proposed.index(b'select:\n'), proposed.index(b'\nproperties:\n')
            self.assertEqual(proposed[:start]+proposed[end+1:], original)
            self.assertEqual(proposed.count(b'const: mediatek,mt6323-pwrc'), 1)
            with self.assertRaisesRegex(ValueError, 'input hash'):
                module.apply_locked_proposal(Path(d), 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87', 'pmic-domain-selector.json')
