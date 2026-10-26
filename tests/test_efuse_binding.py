from pathlib import Path
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from validate_douglas_bindings import apply_locked_proposal


class EfuseBinding(unittest.TestCase):
    def test_locked_generic_tuple_only_and_wrong_revision_rejected(self):
        e = ROOT/'evidence/efuse-binding'
        original, proposed = (e/'original.yaml').read_bytes(), (e/'proposed.yaml').read_bytes()
        self.assertEqual(proposed.replace(b'              - mediatek,mt8163-efuse\n', b''), original)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            path = source/'nvmem/mediatek,efuse.yaml'
            path.parent.mkdir()
            path.write_bytes(original)
            with self.assertRaisesRegex(ValueError, 'input hash'):
                apply_locked_proposal(source, '0'*40, 'mt8163-efuse.json')
            apply_locked_proposal(source, 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87', 'mt8163-efuse.json')
            self.assertEqual(path.read_bytes(), proposed)
            with self.assertRaisesRegex(ValueError, 'input hash'):
                apply_locked_proposal(source, 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87', 'mt8163-efuse.json')
