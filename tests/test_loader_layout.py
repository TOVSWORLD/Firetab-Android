import hashlib
from pathlib import Path
import struct
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from inspect_loader_layout import preloader_layout, lk_layout, address_window, checked_file


def gfh():
    data = bytearray(256)
    struct.pack_into('<IHH', data, 0, 0x014d4d4d, 56, 0)
    data[8:20] = b'FILE_INFO\0\0\0'
    struct.pack_into('<5I', data, 28, 0x200000, len(data), 512, 64, 16)
    return data


class LoaderLayout(unittest.TestCase):
    def test_gfh_code_mapping_preserves_header_and_signature_extent(self):
        data = gfh()
        result = preloader_layout(data)
        self.assertEqual(result['declared_code_start'], 0x200040)
        self.assertEqual(result['payload_bytes'], 176)
        self.assertEqual(address_window(data, result, 0x200050, 0x200040)['file_offset'], 80)
        self.assertFalse(result['signature_verified'])

    def test_malformed_gfh_bounds_and_identity_refused(self):
        for offset, value in [(28, 0xfffffff0), (32, 255), (36, 1), (40, 10), (44, 255)]:
            data = gfh()
            struct.pack_into('<I', data, offset, value)
            with self.assertRaises(ValueError):
                preloader_layout(data)
        with self.assertRaises(ValueError):
            preloader_layout(bytes(55))
        data = gfh()
        data[8] = ord('X')
        with self.assertRaises(ValueError):
            preloader_layout(data)

    def test_lk_default_address_is_not_a_verified_base(self):
        data = bytearray(544)
        struct.pack_into('<II', data, 0, 0x58881688, 32)
        data[8:10] = b'LK'
        struct.pack_into('<II', data, 40, 0xffffffff, 0xffffffff)
        result = lk_layout(data)
        self.assertTrue(result['uses_preloader_default_address'])
        self.assertFalse(result['actual_load_base_verified'])
        data[-1:] = b''
        with self.assertRaises(ValueError):
            lk_layout(data)

    def test_address_window_outside_payload_or_wrong_file_hash_refused(self):
        data = bytes(gfh())
        layout = preloader_layout(data)
        for address, base in [(0, -1), (0, 1), (1 << 32, 0), (0x2000ef, 0x200040)]:
            with self.assertRaises(ValueError):
                address_window(data, layout, address, base)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'loader.bin'
            path.write_bytes(data)
            self.assertEqual(checked_file(path, hashlib.sha256(data).hexdigest()), data)
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                checked_file(path, 'wrong')
