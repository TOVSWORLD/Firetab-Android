import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from validate_douglas_bindings import apply_locked_proposal


class KeypadBinding(unittest.TestCase):
    def test_locked_exact_tuple_change_and_repeated_application_refusal(self):
        evidence = ROOT/'evidence/keypad-binding'
        original = (evidence/'original.yaml').read_bytes()
        proposed = (evidence/'proposed.yaml').read_bytes()
        self.assertEqual(proposed.replace(b'              - mediatek,mt8163-keypad\n', b''), original)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            path = source/'input/mediatek,mt6779-keypad.yaml'
            path.parent.mkdir()
            path.write_bytes(original)
            apply_locked_proposal(source, 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87', 'mt8163-keypad.json')
            self.assertEqual(path.read_bytes(), proposed)
            with self.assertRaisesRegex(ValueError, 'input hash'):
                apply_locked_proposal(source, 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87', 'mt8163-keypad.json')
