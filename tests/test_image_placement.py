import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from audit_image_placement import audit, placement


class ImagePlacement(unittest.TestCase):
    def reports(self):
        return [json.loads((ROOT/p).read_text()) for p in [
            'evidence/qemu-diagnostic/generic-runtime-result.json',
            'evidence/stock-ota-probe/boot-inspection.json',
            'evidence/stock-ota-probe/kernel-prefix-observations.json']]

    def test_actual_stock_and_new_headers_have_different_alignment(self):
        result = audit(*self.reports())
        self.assertTrue(result['stock_header_at_candidate_address']['alignment_satisfied'])
        self.assertFalse(result['diagnostic_header_at_candidate_address']['alignment_satisfied'])
        self.assertFalse(result['memory_safety_qualified'])

    def test_extent_and_alignment_boundaries(self):
        self.assertTrue(placement(0x40000000, 0, 0x1c00000)['alignment_satisfied'])
        self.assertEqual(placement(0x40080000, 0, 0x1c00000)['end_exclusive'], '0x41c80000')
        for values in [(0, 1, 1), (0, 0, 0), ((1 << 64)-1, 0, 2), (-1, 0, 1)]:
            with self.assertRaises(ValueError):
                placement(*values)

    def test_report_identity_and_header_consistency_are_checked(self):
        reports = self.reports()
        reports[2]['boot_image_sha256'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'hashes differ'):
            audit(*reports)
        reports = self.reports()
        reports[0]['arm64_header']['text_offset'] = 1
        with self.assertRaisesRegex(ValueError, 'disagree'):
            audit(*reports)
