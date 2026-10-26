import unittest
from offline_diagnostic_protocol import OfflineDiagnosticProtocol, HEADER, CALL, READ


def reply(request, payload=b'', status=0):
    _, version, op, _, seq, offset, length = HEADER.unpack(request)
    return HEADER.pack(b'FTDR', version, op, status, seq, offset, length) + payload


class ProtocolTests(unittest.TestCase):
    def test_explicit_call_completion_then_exact_read(self):
        session = OfflineDiagnosticProtocol(); call = session.request(CALL)
        self.assertFalse(session.call_completed)
        self.assertEqual(session.accept(reply(call)), b'')
        read = session.request(READ, 48, 4)
        self.assertEqual(session.accept(reply(read, b'1KTF')), b'1KTF')

    def test_no_read_before_completion_repeat_call_or_arbitrary_address(self):
        session = OfflineDiagnosticProtocol()
        for args in [(READ, 0, 4), (CALL, 1, 0), (3, 0, 0)]:
            with self.assertRaises(ValueError): session.request(*args)
        call = session.request(CALL); session.accept(reply(call))
        for args in [(CALL, 0, 0), (READ, 0, 257), (READ, 1079, 2), (READ, -1, 1), (READ, 0, 0)]:
            with self.assertRaises(ValueError): session.request(*args)

    def test_wrong_status_replay_and_truncation_poison(self):
        for mutation in [lambda q: reply(q, status=1), lambda q: reply(q)[:-1],
                         lambda q: reply(q) + b'x', lambda q: reply(q)[:8] + bytes(4) + reply(q)[12:]]:
            session = OfflineDiagnosticProtocol(); request = session.request(CALL)
            with self.assertRaises(ValueError): session.accept(mutation(request))
            with self.assertRaises(ValueError): session.request(CALL)
        session = OfflineDiagnosticProtocol(); q = session.request(CALL); response = reply(q)
        session.accept(response); session.request(READ, 0, 1)
        with self.assertRaises(ValueError): session.accept(response)

    def test_pending_and_abandoned_session_never_reused(self):
        session = OfflineDiagnosticProtocol(); session.request(CALL)
        with self.assertRaises(ValueError): session.request(CALL)
        session.abandon()
        with self.assertRaises(ValueError): session.request(CALL)
