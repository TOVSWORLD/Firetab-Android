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

    def test_compact_dsi_and_lcm_mapping(self):
        patch = (PORT / 'mmsys-parent.patch').read_text()
        self.assertIn('+\t.rst_tb = mmsys_mt8163_rst_tb,', patch)
        self.assertIn('+\t.num_resets = ARRAY_SIZE(mmsys_mt8163_rst_tb),', patch)
        self.assertNotIn('+\t.num_resets = 64,', patch)
        import re
        header = (PORT / 'overlay/drivers/soc/mediatek/mt8163-mmsys.h').read_text()
        table = {name: (int(bank), int(bit)) for name, bank, bit in re.findall(
            r'\[(MT8163_MMSYS_RST_\w+)\]\s*= MMSYS_RST_NR\((\d+), (\d+)\)', header)}
        self.assertEqual(len(table), 34)
        self.assertEqual(table['MT8163_MMSYS_RST_DSI'], (0, 24))
        self.assertEqual(table['MT8163_MMSYS_RST_LCM'], (4, 0))
        self.assertEqual(0x140 + table['MT8163_MMSYS_RST_LCM'][0] * 4, 0x150)
        lock = json.loads((PORT / 'inputs.json').read_text())['mmsys_parent']
        self.assertEqual(hashlib.sha256(header.encode()).hexdigest(), lock['routing_overlay_sha256'])
