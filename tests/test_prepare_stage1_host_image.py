import struct
import unittest
from test_inspect_stage1_elf import fixture
from prepare_stage1_host_image import prepare_host_image


class HostImageTests(unittest.TestCase):
    def source(self):
        data = fixture()
        data.extend(bytes(40))
        struct.pack_into('<I', data, 32, 128)
        struct.pack_into('<HH', data, 46, 40, 1)
        struct.pack_into('<I', data, 24, 1)
        struct.pack_into('<II', data, 60, 0, 0)
        data[96:112] = bytes(range(1, 17))
        return data

    def test_preserves_file_and_initializes_tail_without_word_patching(self):
        image, receipt = prepare_host_image(self.source())
        self.assertEqual(image, bytes(range(1, 17)) + bytes(16))
        self.assertEqual(receipt['segment_zero_fill_bytes'], 16)
        self.assertFalse(receipt['physical_test_ready'])

    def test_zero_fills_gap_between_segments(self):
        data = self.source()
        struct.pack_into('<H', data, 44, 2)
        struct.pack_into('<8I', data, 84, 1, 120, 48, 48, 4, 8, 6, 1)
        data[120:124] = b'abcd'
        image, receipt = prepare_host_image(data)
        self.assertEqual(image[32:48], bytes(16))
        self.assertEqual(image[48:56], b'abcd' + bytes(4))
        self.assertEqual(receipt['gap_zero_fill_bytes'], 16)

    def test_rejects_nonzero_base_mismatched_physical_and_excess_size(self):
        cases = []
        data = fixture(); cases.append(data)
        for offset, value in [(64, 4), (72, 65537)]:
            data = self.source(); struct.pack_into('<I', data, offset, value); cases.append(data)
        for data in cases:
            with self.assertRaises(ValueError): prepare_host_image(data)

    def test_rejects_overlapping_memory_extents(self):
        data = self.source(); struct.pack_into('<H', data, 44, 2)
        struct.pack_into('<8I', data, 84, 1, 120, 8, 8, 4, 8, 6, 1)
        with self.assertRaises(ValueError): prepare_host_image(data)
