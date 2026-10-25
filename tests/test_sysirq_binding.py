import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sysirq_bindings', ROOT/'scripts/validate_douglas_bindings.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SysirqBinding(unittest.TestCase):
    def test_exact_enum_addition_requires_locked_original(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'interrupt-controller/mediatek,mt6577-sysirq.yaml'
            path.parent.mkdir()
            original = (ROOT/'evidence/sysirq-binding/original.yaml').read_bytes()
            path.write_bytes(original)
            module.apply_locked_proposal(Path(d), 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87', 'mt8163-sysirq.json')
            proposed = path.read_bytes()
            self.assertEqual(proposed, (ROOT/'evidence/sysirq-binding/proposed.yaml').read_bytes())
            self.assertEqual(proposed.replace(b'              - mediatek,mt8163-sysirq\n', b''), original)
            with self.assertRaisesRegex(ValueError, 'input hash'):
                module.apply_locked_proposal(Path(d), 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87', 'mt8163-sysirq.json')
