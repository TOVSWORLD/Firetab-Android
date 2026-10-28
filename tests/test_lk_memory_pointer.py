import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from trace_lk_memory_pointer import trace


class LKMemoryPointer(unittest.TestCase):
    def fixture(self):
        raw=bytearray(485040)
        for r in json.loads((ROOT/'evidence/lk-memory-pointer/windows.json').read_text()):
            raw[r['start']:r['end']]=bytes.fromhex(r['hex'])
        return raw

    def test_replay_and_entry_contract_limits(self):
        facts=trace(self.fixture())
        expected=json.loads((ROOT/'evidence/lk-memory-pointer/report.json').read_text())['facts']
        self.assertEqual(facts,expected)
        self.assertEqual(facts['entry_bootarg_register'],'r4')
        self.assertEqual(int(facts['local_buffer'],16)+facts['local_buffer_bytes'],int(facts['pointer_global'],16))
        self.assertIn('not qualified',facts['relocation_caveat'])

    def test_startup_writer_copy_and_pointer_drift_rejected(self):
        for offset in [0,0x20,0x28,0x58,0x70,0x23248,0x23252,0x233a4,0x233a8,0x2347e,0x233c8,0x76320]:
            raw=self.fixture();raw[offset]^=1
            with self.assertRaises(ValueError,msg=hex(offset)):trace(raw)

    def test_truncated_input_rejected(self):
        with self.assertRaises(ValueError):trace(bytes(1024))
