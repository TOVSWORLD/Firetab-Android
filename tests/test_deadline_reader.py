from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from offline_deadline_reader import OfflineDeadlineReader


class DeadlineReaderTests(unittest.TestCase):
    def test_exact_reads_preserve_packet_tail_without_extra_callback(self):
        calls=[]
        def packet(size,timeout):calls.append((size,timeout));return b'abcdefgh'
        reader=OfflineDeadlineReader(packet,packet_bytes=8,deadline_seconds=2,clock=lambda:0)
        self.assertEqual(reader.read_exact(3),b'abc')
        self.assertEqual(reader.read_exact(5),b'defgh')
        self.assertEqual(calls,[(8,1000)])

    def test_positive_timeout_shrinks_with_total_deadline_and_never_zero(self):
        now=[0];calls=[]
        def packet(size,timeout):
            calls.append(timeout);now[0]+=0.2;return b'x'
        reader=OfflineDeadlineReader(packet,packet_bytes=1,deadline_seconds=0.55,clock=lambda:now[0])
        with self.assertRaises(TimeoutError):reader.read_exact(3)
        self.assertEqual(len(calls),3)
        self.assertTrue(all(want<=got<=want+1 for got,want in zip(calls,[550,350,150])))
        self.assertTrue(all(t>0 for t in calls));self.assertTrue(reader.failed)
        with self.assertRaises(RuntimeError):reader.read_exact(1)

    def test_short_packets_accumulate_but_empty_oversized_errors_poison_stream(self):
        pieces=iter([b'ab',b'c',b'd'])
        reader=OfflineDeadlineReader(lambda size,timeout:next(pieces),packet_bytes=4,deadline_seconds=1,clock=lambda:0)
        self.assertEqual(reader.read_exact(4),b'abcd')
        for data in [b'',b'abcde',None]:
            reader=OfflineDeadlineReader(lambda size,timeout:data,packet_bytes=4,deadline_seconds=1)
            with self.assertRaises(ValueError):reader.read_exact(1)
            self.assertTrue(reader.failed)
        def failed(size,timeout):raise OSError('synthetic disconnect')
        reader=OfflineDeadlineReader(failed,packet_bytes=4,deadline_seconds=1)
        with self.assertRaises(OSError):reader.read_exact(1)
        self.assertTrue(reader.failed)

    def test_bad_budget_rejected_and_zero_budget_cannot_be_native_timeout(self):
        for kwargs in [{'packet_bytes':0,'deadline_seconds':1},
                       {'packet_bytes':4,'deadline_seconds':float('nan')},
                       {'packet_bytes':4,'deadline_seconds':1,'max_native_ms':0}]:
            with self.assertRaises(ValueError):OfflineDeadlineReader(lambda *a,**k:b'',**kwargs)
        reader=OfflineDeadlineReader(lambda size,timeout:b'x',packet_bytes=1,deadline_seconds=0.0001,clock=lambda:0)
        self.assertEqual(reader.read_exact(1),b'x')
