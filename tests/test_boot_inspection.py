"""Synthetic layouts exercise rejection paths without real firmware/device access."""
import importlib.util
from pathlib import Path
import struct
import unittest

spec = importlib.util.spec_from_file_location('boot_inspection', Path(__file__).resolve().parents[1] / 'scripts/inspect_boot_image.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture(kernel=None):
    payload = bytearray(64) if kernel is None else bytearray(kernel)
    if kernel is None:
        payload[56:60] = b'ARMd'
    header = bytearray(2048)
    header[:8] = b'ANDROID!'
    struct.pack_into('<10I', header, 8, len(payload), 0x40080000, 0, 0x44000000, 0, 0, 0x48000000, 2048, 0, 0)
    return bytes(header + payload + bytes((-len(payload)) % 2048))


class BootInspection(unittest.TestCase):
    def test_raw_arm64_layout_and_fit(self):
        result = module.inspect(fixture(), 4096)
        self.assertEqual(result['components'][0]['offset'], 2048)
        self.assertIn('ARM64', result['components'][0]['identification'])
        self.assertTrue(result['fits_supplied_partition'])
        self.assertFalse(result['signature_verified'])

    def test_no_partition_is_not_a_fit_pass(self):
        self.assertIsNone(module.inspect(fixture())['fits_supplied_partition'])

    def test_gzip_signature_does_not_assert_architecture(self):
        result = module.inspect(fixture(b'\x1f\x8b' + bytes(62)))
        self.assertIn('not validated', result['components'][0]['identification'])

    def test_unclassified_tail_counts_toward_fit(self):
        result = module.inspect(fixture() + bytes(16), 4096)
        self.assertEqual(result['unclassified_trailing_bytes'], 16)
        self.assertFalse(result['fits_supplied_partition'])

    def test_reject_truncated_padding(self):
        with self.assertRaises(ValueError):
            module.inspect(fixture()[:-1])

    def test_reject_oversized_component(self):
        data = bytearray(fixture())
        struct.pack_into('<I', data, 8, 0xffffffff)
        with self.assertRaises(ValueError):
            module.inspect(data)

    def test_reject_ambiguous_nonzero_version(self):
        data = bytearray(fixture())
        struct.pack_into('<I', data, 40, 1)
        with self.assertRaises(ValueError):
            module.inspect(data)

    def test_reject_invalid_page(self):
        data = bytearray(fixture())
        struct.pack_into('<I', data, 36, 3000)
        with self.assertRaises(ValueError):
            module.inspect(data)

    def test_reject_wrapper_or_nonboot_input(self):
        with self.assertRaises(ValueError):
            module.inspect(bytes(512) + fixture())

    def test_reject_empty_kernel(self):
        data = bytearray(fixture())
        struct.pack_into('<I', data, 8, 0)
        with self.assertRaises(ValueError):
            module.inspect(data)
