import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from trace_lk_cpu_fixup import trace,selected_policy


class LKCPUFixup(unittest.TestCase):
    def fixture(self):
        raw=bytearray(485040)
        for r in json.loads((ROOT/'evidence/lk-cpu-fixup/windows.json').read_text()):
            raw[r['start']:r['end']]=bytes.fromhex(r['hex'])
        return raw

    def test_static_replay_and_no_psci_inference(self):
        facts=trace(self.fixture())
        self.assertEqual(facts,json.loads((ROOT/'evidence/lk-cpu-fixup/report.json').read_text())['facts'])
        self.assertIn('not PSCI',facts['psci_limit'])

    def test_selected_window_literal_table_and_guard_drift_rejected(self):
        for offset in [0x259ce,0x259d2,0x25a76,0x2579c,0x3e076,0x5ef20,0x25aa0,0x76504]:
            raw=self.fixture();raw[offset]^=1
            with self.assertRaises(ValueError,msg=hex(offset)):trace(raw)

    def test_core_selectors_default_and_threshold(self):
        for selector,limit in enumerate([4,4,4,4,4,4,4,4,3,4,4,4,2,4,1,4]):
            self.assertTrue(selected_policy(selector<<4,0,limit-1,1000)['keep'])
            self.assertFalse(selected_policy(selector<<4,0,limit,1000)['keep'])

    def test_frequency_all_nibbles_and_no_upward_change(self):
        for selector,cap in enumerate([2000000000,2000000000,1900000000,1800000000,1700000000,1600000000,1500000000,1400000000,1300000000,1200000000,1100000000,1100000000,1100000000,1100000000,1100000000,1100000000]):
            self.assertEqual(selected_policy(0,selector,0,2100000000)['clock_frequency_after'],cap)
            self.assertEqual(selected_policy(0,selector,0,500000000)['clock_frequency_after'],500000000)

    def test_independent_reads_removed_nodes_and_cluster_bit(self):
        r=selected_policy(0xe0,2,0x100,2100000000)
        self.assertEqual((r['core_limit'],r['cap_hz'],r['cluster_bit']),(1,1900000000,1))
        self.assertIsNone(selected_policy(0xe0,0,1,1000)['clock_frequency_after'])
        with self.assertRaises(ValueError):selected_policy(-1,0,0,0)
