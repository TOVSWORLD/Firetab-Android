"""Exercise the pinned existing-parent patch, including rejection of drift."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PORT = ROOT / 'projects/firetabs-android/kernel/clock-port'


class MmsysParentPatch(unittest.TestCase):
    def test_exact_parent_patch_and_drift_rejection(self):
        lock = json.loads((PORT / 'inputs.json').read_text())['mmsys_parent']
        original = (ROOT / 'evidence/clock-port/mmsys-parent/ack-mtk-mmsys.c').read_bytes()
        self.assertEqual(hashlib.sha256(original).hexdigest(), lock['original_sha256'])
        patch = PORT / 'mmsys-parent.patch'
        self.assertEqual(hashlib.sha256(patch.read_bytes()).hexdigest(), lock['patch_sha256'])
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / lock['target']
            target.parent.mkdir(parents=True)
            target.write_bytes(original)
            subprocess.run(['git', 'apply', '--unsafe-paths', str(patch)], cwd=d, check=True)
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), lock['patched_sha256'])
            again = subprocess.run(['git', 'apply', '--check', str(patch)], cwd=d, capture_output=True)
            self.assertNotEqual(again.returncode, 0)

    def test_retained_reset_contract_is_raw_bank_bits(self):
        # Donor MT8163 descriptor uses64 raw bit IDs; its compact reset table is
        # referenced by MT8167, not MT8163. Do not silently substitute that ABI.
        patch = (PORT / 'mmsys-parent.patch').read_text()
        self.assertIn('+\t.num_resets = 64,', patch)
        self.assertNotIn('+\t.rst_tb', patch)
        self.assertIn('"clk-mt8163-mm"', patch)
