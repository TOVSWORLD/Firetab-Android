import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from decode_offline_uart_markers import decode_markers, MAX_BYTES


class OfflineMarkers(unittest.TestCase):
    def test_complete_pairs_and_privacy(self):
        for ending in (b'RETURN', b'ERROR'):
            raw = b'private serial identifier\nFTD1 ENTRY\r\nFTD1 ' + ending + b'\r\n'
            report = decode_markers(raw)
            self.assertTrue(report['single_marker_pair_valid'])
            self.assertNotIn('private', str(report))
            self.assertFalse(report['agent_execution_verified'])
            self.assertFalse(report['capture_origin_verified'])

    def test_incomplete_ambiguous_and_corrupted(self):
        for raw in (b'', b'FTD1 ENTRY\n', b'FTD1 ENTRY\nFTD1 RETURN',
                    b'FTD1 RETURN\nFTD1 ENTRY\n',
                    b'FTD1 ENTRY\nFTD1 RETURN\nFTD1 ERROR\n',
                    b'FTD1 ENTRY\nFTD1 RETURN\nFTD1 ENTRY\nFTD1 RETURN\n',
                    b'prefix FTD1 ENTRY\nFTD1 RETURN\n',
                    b'FTD1 ENTRY\nFTD1 RETURN\nFTD1 unknown\n'):
            with self.subTest(raw=raw):
                self.assertFalse(decode_markers(raw)['single_marker_pair_valid'])
                self.assertEqual(decode_markers(raw)['reported_outcome'], 'unqualified')

    def test_bounded_input(self):
        with self.assertRaises(ValueError):
            decode_markers(b'x' * (MAX_BYTES + 1))
