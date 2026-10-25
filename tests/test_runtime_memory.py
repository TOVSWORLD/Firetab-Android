import copy
import json
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from decode_runtime_memory import decode, vendor, regions


class RuntimeMemory(unittest.TestCase):
    def report(self):
        return json.loads((ROOT/'evidence/stock-facts/runtime-contract.json').read_text())

    def test_actual_rank_and_bank_reconciliation(self):
        result = decode(self.report())
        self.assertEqual(result['physical_bytes'], 1536*1024*1024)
        self.assertEqual(result['usable_dt_bytes'], 1430*1024*1024)
        self.assertEqual(result['excluded_from_usable_dt'], [{'start': 0x99600000, 'bytes': 106*1024*1024}])
        self.assertFalse(result['boot_qualified'])

    def mutate(self, suffix, change):
        report = self.report()
        record = next(r for r in report['selected_records'] if r['name'].endswith(suffix))
        record['hex'] = change(bytearray.fromhex(record['hex'])).hex()
        return report

    def test_invalid_layout_counts_and_lengths(self):
        for count in [0, 5, 0xffffffff]:
            with self.assertRaises(ValueError):
                vendor(struct.pack('<I', count)+bytes(68))
        with self.assertRaises(ValueError):
            vendor(bytes(71))

    def test_rank_reference_and_reg_disagreement(self):
        def bad_rank(data):
            struct.pack_into('<I', data, 24, 4)
            return data
        with self.assertRaisesRegex(ValueError, 'rank outside'):
            decode(self.mutate('mblock_info', bad_rank))
        def bad_reg(data):
            data[-1] = 1
            return data
        with self.assertRaisesRegex(ValueError, 'disagree'):
            decode(self.mutate('/reg', bad_reg))

    def test_overlapping_zero_and_overflowing_ranges(self):
        for items in [[{'start': 0, 'bytes': 0}],
                      [{'start': (1 << 64)-1, 'bytes': 2}],
                      [{'start': 0, 'bytes': 10}, {'start': 9, 'bytes': 2}]]:
            with self.assertRaises(ValueError):
                regions(items)

    def test_duplicate_or_unavailable_properties_refused(self):
        report = self.report()
        report['selected_records'].append(copy.deepcopy(report['selected_records'][0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            decode(report)
        report = self.report()
        next(r for r in report['selected_records'] if r['name'].endswith('/reg'))['available'] = False
        with self.assertRaisesRegex(ValueError, 'unavailable'):
            decode(report)
