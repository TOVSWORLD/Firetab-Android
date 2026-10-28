import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from trace_lk_fdt_destination import trace


class LKFDestination(unittest.TestCase):
    def fixture(self):
        data = bytearray(485040)
        for r in json.loads((ROOT/'evidence/lk-fdt-destination/windows.json').read_text()):
            data[r['start']:r['end']] = bytes.fromhex(r['hex'])
        return data

    def test_published_sparse_evidence_reproduces_selected_facts(self):
        expected = json.loads((ROOT/'evidence/lk-fdt-destination/report.json').read_text())['facts']
        self.assertEqual(trace(self.fixture()), expected)
        self.assertIn('0x40000100', expected['header_absent_destination'])
        self.assertIn('unproved', expected['selected_handoff'])

    def test_changed_destination_copy_capacity_and_call_instructions_rejected(self):
        for offset in [0x3ed84, 0x3ed90, 0x3edce, 0x3eb90, 0x3de2a,
                       0x3dee6, 0x3defc, 0x3e0bc, 0x3e73e]:
            data = self.fixture()
            data[offset] ^= 1
            with self.assertRaises(ValueError, msg=hex(offset)):
                trace(data)

    def test_changed_property_literal_or_reference_rejected(self):
        for offset in [0x3e09c, 0x3e9d4, 0x5f154, 0x65b14]:
            data = self.fixture()
            data[offset] ^= 1
            with self.assertRaises((ValueError, UnicodeDecodeError), msg=hex(offset)):
                trace(data)

    def test_truncated_input_rejected(self):
        with self.assertRaises(ValueError):
            trace(bytes(1024))
