import struct
import unittest
import test_prepare_stage1_host_image as host_fixture
from inspect_stage1_relocations import inspect_relocations


class RelocationTests(unittest.TestCase):
    def test_plain_table_does_not_claim_position_independence(self):
        result = inspect_relocations(host_fixture.HostImageTests().source())
        self.assertEqual(result['section_count'], 1)
        self.assertFalse(result['runtime_position_independence_verified'])

    def test_rejects_missing_truncated_or_oversized_table(self):
        for field, fmt, value in [(48, '<H', 0), (32, '<I', 160), (48, '<H', 257)]:
            data = host_fixture.HostImageTests().source(); struct.pack_into(fmt, data, field, value)
            with self.assertRaises(ValueError): inspect_relocations(data)

    def test_rejects_nonempty_rel_rela_and_dynamic_sections(self):
        for kind, length in [(9, 8), (4, 12), (6, 8)]:
            data = host_fixture.HostImageTests().source()
            struct.pack_into('<10I', data, 128, 0, kind, 0, 0, 96, length, 0, 0, 4, length)
            with self.assertRaises(ValueError): inspect_relocations(data)

    def test_rejects_bad_section_file_extent_and_relocation_record(self):
        for kind, offset, size, entsize in [(1, 160, 16, 0), (9, 96, 7, 8)]:
            data = host_fixture.HostImageTests().source()
            struct.pack_into('<10I', data, 128, 0, kind, 0, 0, offset, size, 0, 0, 4, entsize)
            with self.assertRaises(ValueError): inspect_relocations(data)
