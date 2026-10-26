import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_stock_checked_length import checked_length


class CheckedLengthTests(unittest.TestCase):
    def test_both_payloads_and_two_pages_count_toward_limit(self):
        self.assertEqual(checked_length(1,1,2048),8192)
        self.assertEqual(checked_length(2048,2048,2048),8192)
        self.assertGreater(checked_length(10*1024*1024,8*1024*1024,2048),16*1024*1024)

    def test_unreviewed_or_overflow_arithmetic_is_rejected(self):
        for values in [(0,1,2048),(1,1,0),(1,1,513),(0xffffffff,1,2048),(-1,1,2048)]:
            with self.assertRaises(ValueError):checked_length(*values)
