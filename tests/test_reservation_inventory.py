import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from inventory_reservations import inventory, cells, overlap


class Reservations(unittest.TestCase):
    def test_actual_static_reservations_do_not_explain_top_gap(self):
        memory = json.loads((ROOT/'evidence/runtime-memory/result.json').read_text())
        dt = json.loads((ROOT/'evidence/stock-dtb/candidate-report.json').read_text())
        result = inventory(memory, dt)
        self.assertEqual(len(result['fixed_reservations']), 4)
        self.assertTrue(all(x['inside_runtime_usable_bank'] for x in result['fixed_reservations']))
        self.assertEqual(result['fixed_overlap_top_exclusion_bytes'], 0)
        self.assertEqual(result['fixed_bytes'], 0x550000)
        self.assertEqual(len(result['dynamic_reservations']), 1)
        self.assertFalse(result['reservation_ownership_verified'])

    def test_cell_width_and_extent_refusal(self):
        for value in ['0 1 0', '0 1 0 0', '0 100000000 0 1', 'ffffffff ffffffff 0 2']:
            with self.assertRaises(ValueError):
                cells(value)

    def test_half_open_interval_boundaries(self):
        self.assertEqual(overlap({'start': 0, 'bytes': 4}, {'start': 4, 'bytes': 2}), 0)
        self.assertEqual(overlap({'start': 0, 'bytes': 4}, {'start': 3, 'bytes': 2}), 1)
