import gzip
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from measure_arm64_image import measure, LK_CAPACITY


class ImageMeasurements(unittest.TestCase):
    def image(self, size=128, footprint=4096):
        raw = bytearray(size)
        struct.pack_into('<QQQ', raw, 8, 0, footprint, 10)
        raw[56:60] = b'ARMd'
        return bytes(raw)

    def test_file_length_distinct_from_runtime_footprint(self):
        raw = self.image()
        result = measure(raw, gzip.compress(raw, mtime=0))
        self.assertEqual(result['declared_runtime_bytes_beyond_file'], 3968)
        self.assertEqual(result['lk_output_capacity_margin_bytes'], LK_CAPACITY-128)
        self.assertIsNone(result['appended_dt_bytes'])
        self.assertFalse(result['boot_verified'])

    def test_exact_capacity_and_one_byte_over(self):
        for size, fits in [(LK_CAPACITY, True), (LK_CAPACITY+1, False)]:
            raw = self.image(size=size, footprint=LK_CAPACITY+4096)
            result = measure(raw, gzip.compress(raw, mtime=0))
            self.assertEqual(result['decoded_file_fits_lk_capacity'], fits)
            self.assertEqual(result['lk_output_capacity_margin_bytes'], LK_CAPACITY-size)

    def test_bad_headers_truncation_concatenation_and_wrong_payload_rejected(self):
        raw = self.image()
        packed = gzip.compress(raw, mtime=0)
        bad = bytearray(raw)
        bad[56] = 0
        for image, gz in [(raw[:63], packed), (bytes(bad), packed),
                          (self.image(128, 0), packed), (self.image(128, 64), packed),
                          (raw, packed[:-1]), (raw, packed+packed),
                          (raw, gzip.compress(raw+b'x', mtime=0)),
                          (raw, gzip.compress(raw, mtime=1))]:
            with self.assertRaises(ValueError):
                measure(image, gz)
