import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from offline_dram_session import OfflineDramSession
from test_offline_dram_evidence import fixture


class DramSessionTests(unittest.TestCase):
    def test_ordered_complete_synthetic_session_never_authorizes_transfer(self):
        session=OfflineDramSession(expected_ack=b'A',local_emi_bytes=188)
        for name,data in fixture().items():
            result=session.accept(name,data)
        self.assertEqual(session.state,'decoded')
        self.assertFalse(result['stage_transfer_authorized'])
        self.assertEqual(session.fields,{})
        with self.assertRaises(RuntimeError):session.accept('version_reply',b'A')
        self.assertEqual(session.state,'invalid')

    def test_duplicate_reordered_and_short_events_poison_session(self):
        for events in [[('status',bytes(4))], [('version_reply',b'A')]*2,
                       [('version_reply',b'')], [('version_reply',b'?')]]:
            session=OfflineDramSession(expected_ack=b'A',local_emi_bytes=188)
            with self.assertRaises(ValueError):
                for name,data in events:session.accept(name,data)
            self.assertEqual(session.state,'invalid')
            self.assertEqual(session.fields,{})
            with self.assertRaises(RuntimeError):session.accept('version_reply',b'A')

    def test_abort_at_every_incomplete_boundary_discards_all_fields(self):
        events=list(fixture().items())
        for count in range(len(events)):
            session=OfflineDramSession(expected_ack=b'A',local_emi_bytes=188)
            for name,data in events[:count]:self.assertIsNone(session.accept(name,data))
            session.abort()
            self.assertEqual(session.fields,{})
            with self.assertRaises(RuntimeError):session.accept(*events[count])
