import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from audit_lk_input_length import audit, selected_input_length


class LKInputLength(unittest.TestCase):
    def inputs(self):
        payload = bytearray(485040)
        for item in json.loads((ROOT/'evidence/lk-input-length/windows.json').read_text()):
            payload[item['start']:item['end']] = bytes.fromhex(item['hex'])
        boot = json.loads((ROOT/'evidence/stock-ota-probe/boot-inspection.json').read_text())
        dt = json.loads((ROOT/'evidence/stock-dtb/candidate-report.json').read_text())
        return payload, boot, dt

    def test_alignment_rounds_suffix_not_destination(self):
        self.assertEqual(selected_input_length(1000, 0x45000000, 0x45000385),
                         {'scan_distance_bytes': 99, 'rounded_suffix_bytes': 100, 'selected_inflate_input_bytes': 900})
        for size, base, match in [(0, 0, 1), (100, 0xffffffff, 1), (100, 10, 10), (100, 10, 111), (0x100000, 0, 1)]:
            with self.assertRaises(ValueError):
                selected_input_length(size, base, match)

    def test_actual_output_differs_from_declared_memory_requirement(self):
        facts = audit(*self.inputs())
        self.assertEqual(facts['stock_output_capacity_margin_bytes'], 12775272)
        self.assertEqual([x['selected_inflate_input_bytes'] for x in facts['fdt_match_cases']], [7026234, 7108510])
        self.assertIsNone(facts['modern_actual_gzip_output_bytes'])
        self.assertFalse(facts['boot_verified'])
        self.assertFalse(facts['actual_dt_selection_verified'])

    def test_changed_capacity_result_or_prefix_instructions_refused(self):
        for at in (0x246ce, 0x24d88, 0x3de58, 0x3dfa6, 0x3f2fe, 0x3f316):
            payload, boot, dt = self.inputs()
            payload[at] ^= 1
            with self.assertRaises(ValueError):
                audit(payload, boot, dt)
