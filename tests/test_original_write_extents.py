from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_original_write_extents import extent,audit


class OriginalWriteExtents(unittest.TestCase):
    def test_original_layout_ranges_and_no_runtime_promotion(self):
        r=audit()
        self.assertEqual(r['boot0_components'][-1]['relative_end_exclusive'],405504)
        self.assertEqual(r['declared_new_boot_recovery_slot_bytes'],115343360)
        self.assertEqual(r['payload_tail_slack_bytes'],560640)
        self.assertFalse(r['actual_target_capacities_verified'])
        self.assertFalse(r['independent_failure_return_qualified'])
        self.assertFalse(r['physical_test_ready'])

    def test_padding_overflow_and_capacity_failures(self):
        self.assertEqual(extent(1,513)['relative_end_exclusive'],1536)
        for args in [(0,0,None),(-1,512,None),(0,513,512),(1<<64,1,None)]:
            with self.assertRaises(ValueError):extent(*args)
