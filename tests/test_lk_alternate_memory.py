import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from trace_lk_alternate_memory import trace,encode_alternate_ranks


class LKAlternateMemory(unittest.TestCase):
    def fixture(self):
        data=bytearray(485040)
        for r in json.loads((ROOT/'evidence/lk-alternate-memory/windows.json').read_text()):
            data[r['start']:r['end']]=bytes.fromhex(r['hex'])
        return data

    def test_selected_guard_and_callback_replay(self):
        expected=json.loads((ROOT/'evidence/lk-alternate-memory/report.json').read_text())['facts']
        self.assertEqual(trace(self.fixture()),expected)
        self.assertIn('function pointer',expected['alternate_guard'])
        self.assertIn('private',expected['privacy'])

    def test_changed_guard_got_dispatcher_and_properties_rejected(self):
        for offset in [0x3e084,0x3e1d8,0x3e228,0x148,0x150,0x520,0x3e9cc,0x76574,0x4b674,0xf50]:
            data=self.fixture();data[offset]^=1
            with self.assertRaises(ValueError,msg=hex(offset)):trace(data)

    def test_only_last_rank_adjusted_and_64bit_high_cells_zero(self):
        r=encode_alternate_ranks([(0x40000000,0x10000000),(0x50000000,0x20000000)],0x100000)
        self.assertEqual(r['dt_reg_hex'],'000000004000000000000000100000000000000050000000000000001ff00000')
        self.assertFalse(any(x['subtraction_wrapped'] for x in r['ranges']))

    def test_32bit_subtraction_wrap_is_reported_not_validated(self):
        r=encode_alternate_ranks([(0x40000000,1)],2)
        self.assertEqual(r['ranges'][0]['size'],0xffffffff)
        self.assertTrue(r['ranges'][0]['subtraction_wrapped'])
        self.assertIn('not runtime',r['scope'])

    def test_model_boundaries_and_rejections(self):
        self.assertEqual(encode_alternate_ranks([],0)['dt_reg_hex'],'')
        self.assertEqual(len(bytes.fromhex(encode_alternate_ranks([(0,0)]*4,0)['dt_reg_hex'])),64)
        for ranks,adjustment in [([(0,0)]*5,0),([(0x100000000,0)],0),([(0,-1)],0),([],0x100000000)]:
            with self.assertRaises(ValueError):encode_alternate_ranks(ranks,adjustment)
