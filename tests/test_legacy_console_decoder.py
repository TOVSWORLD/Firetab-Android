import hashlib
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from decode_legacy_console import decode, MAX_BYTES, SIGNATURE


class LegacyConsoleDecoder(unittest.TestCase):
    def fixture(self, start=3, size=3, ring=b'abcXXXXX'):
        fields = [0]*16
        fields[0] = SIGNATURE
        fields[10:16] = [128+len(ring), 64, 128, start, size, len(ring)]
        return struct.pack('<16I', *fields) + bytes(64) + ring

    def test_partial_full_and_wrapped_chronological_hashes(self):
        for start, size, raw_ring, expected in [(3,3,b'abcXXXXX',b'abc'),
                (0,8,b'abcdefgh',b'abcdefgh'), (3,8,b'fghabcde',b'abcdefgh'),
                (0,0,b'XXXXXXXX',b'')]:
            result = decode(self.fixture(start,size,raw_ring))
            self.assertEqual(result['log_sha256'], hashlib.sha256(expected).hexdigest())
            self.assertEqual(result['log_bytes'],len(expected))
            self.assertFalse(result['capture_freshness_verified'])
            self.assertFalse(result['raw_log_text_emitted'])
            self.assertFalse(result['boot_qualified'])

    def test_underflow_and_impossible_partial_cursor_refused(self):
        for start,size in [(4,3),(2,3),(8,8),(0,9)]:
            with self.assertRaises(ValueError):
                decode(self.fixture(start,size))

    def test_corrupt_header_and_geometry_refused(self):
        for index,value in [(0,0),(10,999),(11,63),(11,129),(12,999),(15,7)]:
            raw = bytearray(self.fixture())
            struct.pack_into('<I',raw,index*4,value)
            with self.assertRaises(ValueError):
                decode(bytes(raw))
        for raw in [b'x'*63,b'x'*(MAX_BYTES+1),self.fixture()[:-1]]:
            with self.assertRaises(ValueError):
                decode(raw)
