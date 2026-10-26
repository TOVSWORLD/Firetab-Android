from pathlib import Path
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from validate_douglas_bindings import apply_locked_proposal


class GCEBinding(unittest.TestCase):
    def test_only_exact_fallback_branch_changed_and_hash_guard_holds(self):
        e = ROOT/'evidence/gce-binding'
        original, proposed = (e/'original.yaml').read_bytes(), (e/'proposed.yaml').read_bytes()
        old = b'          - const: mediatek,mt6795-gce\n'
        new = b'          - enum:\n              - mediatek,mt6795-gce\n              - mediatek,mt8163-gce\n'
        self.assertEqual(proposed.replace(new,old), original)
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder)
            path = source/'mailbox/mediatek,gce-mailbox.yaml'
            path.parent.mkdir()
            path.write_bytes(original)
            apply_locked_proposal(source,'d9318bdb4c34e8b2d997b4f67ced56b120b22b87','mt8163-gce.json')
            self.assertEqual(path.read_bytes(), proposed)
            with self.assertRaisesRegex(ValueError,'input hash'):
                apply_locked_proposal(source,'d9318bdb4c34e8b2d997b4f67ced56b120b22b87','mt8163-gce.json')
