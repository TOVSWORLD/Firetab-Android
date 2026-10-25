import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('timer_bindings', ROOT/'scripts/validate_douglas_bindings.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TimerBinding(unittest.TestCase):
    def test_exact_enum_addition_requires_locked_original(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'timer/mediatek,timer.yaml'
            path.parent.mkdir()
            original = (ROOT/'evidence/timer-binding/original.yaml').read_bytes()
            path.write_bytes(original)
            module.apply_locked_proposal(Path(d), 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87', 'mt8163-timer.json')
            proposed = path.read_bytes()
            self.assertEqual(proposed, (ROOT/'evidence/timer-binding/proposed.yaml').read_bytes())
            self.assertEqual(proposed.replace(b'              - mediatek,mt8163-timer\n', b''), original)
            with self.assertRaisesRegex(ValueError, 'input hash'):
                module.apply_locked_proposal(Path(d), 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87', 'mt8163-timer.json')
