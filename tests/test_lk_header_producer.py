import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from trace_lk_header_producer import trace


class LKHeaderProducer(unittest.TestCase):
    def fixture(self):
        data = bytearray(485040)
        for item in json.loads((ROOT/'evidence/lk-header-producer/anchors.json').read_text())['ranges']:
            raw = bytes.fromhex(item['hex'])
            data[item['offset']:item['offset']+len(raw)] = raw
        return data

    def test_header_global_join_and_distinct_alignments(self):
        facts = trace(self.fixture())
        self.assertEqual(facts['header_magic_reference']['text'], 'ANDROID!')
        self.assertEqual(facts['shared_got_payload_offset'], '0x761f4')
        self.assertEqual(facts['k64_header_address_alignment_bytes'], 512*1024)
        self.assertEqual(facts['decompression_output_capacity_bytes'], 28*1024*1024)
        self.assertFalse(facts['header_pointer_value_available_in_file'])
        self.assertFalse(facts['whole_loader_compatibility_verified'])
        self.assertFalse(facts['runtime_boot_verified'])

    def test_mutated_header_slot_and_code_cannot_reuse_static_claims(self):
        for at in (0x2495c, 0x3ef78, 0x3e998, 0x7643c, 0x3ed86,
                   0x3de60, 0x3e11a, 0x3f3fc, 0x3f2f8, 0x5e080):
            data = self.fixture()
            data[at] ^= 1
            with self.assertRaises(ValueError):
                trace(data)

    def test_truncated_payload_refused(self):
        with self.assertRaises(ValueError):
            trace(self.fixture()[:-1])
