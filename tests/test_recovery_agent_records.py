import sys
from pathlib import Path
import struct
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from probe_recovery_agent_records import parse_records, Ranges


def fixture(width):
    raw=bytearray(width*2)
    fields=[0xDADA,0x8163,0,0xCA00]
    fields += [4096,0,0,3] if width==0xD8 else [0,0,4096,0,0,3]
    struct.pack_into('<'+'H'*len(fields),raw,0,*fields)
    start=16 if width==0xD8 else 20
    for i in range(3):
        struct.pack_into('<IIIII',raw,start+20*i,1000+i*100,100,0,0,16)
    return raw


class AgentRecordTests(unittest.TestCase):
    def test_both_record_layouts_without_exporting_target_addresses(self):
        for width in [0xD8,0xDC]:
            rows=parse_records(fixture(width),2,width,2000)
            self.assertEqual(rows[0]['hardware_version'],0xCA00)
            self.assertEqual(rows[0]['regions'][1]['bytes'],100)
            self.assertNotIn('address',str(rows))

    def test_count_bounds_signature_bounds_and_truncation(self):
        with self.assertRaises(ValueError):parse_records(b'',2049,0xDC,2000)
        with self.assertRaises(ValueError):parse_records(fixture(0xDC)[:-1],2,0xDC,2000)
        raw=fixture(0xDC);struct.pack_into('<I',raw,20+16,101)
        with self.assertRaises(ValueError):parse_records(raw,2,0xDC,2000)
        with self.assertRaises(ValueError):parse_records(fixture(0xDC),2,0xDC,1050)

    def test_ignored_range_body_is_never_read(self):
        class Response:
            status=200
            headers={}
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,*args):raise AssertionError('Full body must not be read')
        with patch('urllib.request.urlopen',return_value=Response()):
            with self.assertRaises(ValueError):Ranges().read({'path':'unused','size':1000},0,108)

    def test_budget_fails_before_network(self):
        reader=Ranges();reader.bytes=3*1024*1024
        with patch('urllib.request.urlopen',side_effect=AssertionError('No request allowed')):
            with self.assertRaises(ValueError):reader.read({'path':'unused','size':1000},0,108)
