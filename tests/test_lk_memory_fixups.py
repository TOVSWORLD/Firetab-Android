import json
from pathlib import Path
import struct
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from trace_lk_memory_fixups import trace,decode_mblocks


class LKMemoryFixups(unittest.TestCase):
    def fixture(self):
        raw=bytearray(485040)
        for r in json.loads((ROOT/'evidence/lk-memory-fixups/windows.json').read_text()):
            raw[r['start']:r['end']]=bytes.fromhex(r['hex'])
        return raw

    def test_sparse_pinned_trace_and_unresolved_runtime_values(self):
        expected=json.loads((ROOT/'evidence/lk-memory-fixups/report.json').read_text())['facts']
        self.assertEqual(trace(self.fixture()),expected)
        self.assertFalse(expected['runtime_pointer_value_file_backed'])

    def test_instruction_literal_and_pointer_drift_rejected(self):
        for offset in [0x25ada,0x25b76,0x25bde,0x25c26,0x25c5c,0x3e088,0x25d28,0x76320]:
            raw=self.fixture();raw[offset]^=1
            with self.assertRaises(ValueError,msg=hex(offset)):trace(raw)

    def test_64bit_start_size_and_ignored_record_metadata(self):
        raw=bytearray(0x38+24)
        struct.pack_into('<I',raw,0x30,1)
        struct.pack_into('<QQQ',raw,0x38,0x123456789abcdef0,0x102030405060708,0xffffffffffffffff)
        result=decode_mblocks(raw)
        self.assertEqual(result['dt_reg_hex'],'123456789abcdef00102030405060708')
        self.assertEqual(result['count'],1)

    def test_zero_and_four_record_boundaries(self):
        self.assertEqual(decode_mblocks(bytes(0x38))['dt_reg_hex'],'')
        raw=bytearray(0x38+4*24);struct.pack_into('<I',raw,0x30,4)
        for i in range(4):struct.pack_into('<QQ',raw,0x38+i*24,0x40000000+i*0x1000000,0x1000000)
        result=decode_mblocks(raw)
        self.assertEqual(len(bytes.fromhex(result['dt_reg_hex'])),64)
        self.assertEqual(result['ranges'][3]['start'],0x43000000)

    def test_over_capacity_and_truncated_snapshots_rejected(self):
        raw=bytearray(0x38+5*24);struct.pack_into('<I',raw,0x30,5)
        for snapshot in [raw,bytes(8),bytes(4097)]:
            with self.assertRaises(ValueError):decode_mblocks(snapshot)
        struct.pack_into('<I',raw,0x30,4)
        with self.assertRaises(ValueError):decode_mblocks(raw[:0x38+3*24])
