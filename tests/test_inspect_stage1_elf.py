import struct
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from inspect_stage1_elf import inspect_elf


def fixture():
    data = bytearray(128)
    data[:7] = b'\x7fELF\x01\x01\x01'
    struct.pack_into('<HHIIIIIHHHHHH', data, 16, 2, 40, 1, 0x1001, 52, 0, 0, 52, 32, 1, 0, 0, 0)
    struct.pack_into('<8I', data, 52, 1, 96, 0x1000, 0x1000, 16, 32, 5, 16)
    return data


class LayoutTests(unittest.TestCase):
    def test_thumb_entry_and_bss_extent(self):
        result = inspect_elf(fixture())
        self.assertTrue(result['entry_executable_file_coverage'])
        self.assertEqual(result['load_segments'][0]['memory_bytes'], 32)
        self.assertFalse(result['runtime_placement_verified'])

    def test_rejects_entry_in_bss_or_non_executable_segment(self):
        for offset, value in [(24, 0x1010), (52 + 24, 4)]:
            data = fixture(); struct.pack_into('<I', data, offset, value)
            with self.assertRaises(ValueError): inspect_elf(data)

    def test_rejects_malformed_extents_and_alignment(self):
        for offset, value in [(28, 120), (52 + 16, 100), (52 + 20, 8), (52 + 28, 3), (52 + 8, 0xfffffff0)]:
            data = fixture(); struct.pack_into('<I', data, offset, value)
            with self.assertRaises(ValueError): inspect_elf(data)
