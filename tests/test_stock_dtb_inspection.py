import importlib.util
from pathlib import Path
import gzip
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
spec = importlib.util.spec_from_file_location('stock_dtb', Path(__file__).resolve().parents[1] / 'scripts/inspect_stock_dtb.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def dtb():
    structure = struct.pack('>I', 1) + b'\0'*4 + struct.pack('>II', 2, 9)
    size = 56 + len(structure)
    return struct.pack('>10I', 0xd00dfeed, size, 56, size, 40, 17, 16, 0, 0, len(structure)) + b'\0'*16 + structure


def kernel(suffix=None, raw=None):
    payload = gzip.compress(raw or b'\0'*56 + b'ARMd' + b'\0'*4) + (dtb()*2 if suffix is None else suffix)
    prefix = struct.pack('<II', 0x58881688, len(payload)) + b'KERNEL\0'
    return prefix.ljust(512, b'\0') + payload


class StockDTBInspection(unittest.TestCase):
    def test_streamed_member_and_multiple_exact_dtbs(self):
        report, blobs = module.split_kernel(kernel())
        self.assertTrue(report['arm64_magic'])
        self.assertEqual(blobs, [dtb(), dtb()])
        self.assertEqual(report['gzip_uncompressed_bytes'], 64)

    def test_decompression_bomb_and_truncated_member_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'budget'):
            module.split_kernel(kernel(raw=b'A'*200000), maximum=1000)
        data = kernel(suffix=b'')[:-4]
        data = data[:4] + struct.pack('<I', len(data)-512) + data[8:]
        with self.assertRaisesRegex(ValueError, 'Truncated gzip'):
            module.split_kernel(data)

    def test_prefix_declared_size_is_checked(self):
        data = bytearray(kernel())
        struct.pack_into('<I', data, 4, 1)
        with self.assertRaisesRegex(ValueError, 'name/size'):
            module.split_kernel(data)

    def test_unknown_or_overlong_dtb_suffix_is_rejected(self):
        with self.assertRaises(ValueError):
            module.split_kernel(kernel(suffix=dtb()+b'extra'))
        data = bytearray(dtb())
        struct.pack_into('>I', data, 4, 0xffffffff)
        with self.assertRaises(ValueError):
            module.split_kernel(kernel(suffix=bytes(data)))
