import unittest
from offline_diagnostic_protocol import OfflineDiagnosticProtocol, HEADER, CALL, READ
from offline_diagnostic_dispatcher import OfflineDiagnosticDispatcher


class DispatcherTests(unittest.TestCase):
    def test_synthetic_call_completion_and_full_image_read(self):
        image = bytearray(1080); trace = []
        def call():
            trace.append('call-return'); image[48:52] = b'1KTF'; return 0
        agent = OfflineDiagnosticDispatcher(call, lambda offset, length: bytes(image[offset:offset+length]))
        host = OfflineDiagnosticProtocol()
        host.accept(agent.dispatch(host.request(CALL)))
        captured = b''
        for offset in range(0, 1080, 256):
            captured += host.accept(agent.dispatch(host.request(READ, offset, min(256, 1080-offset))))
        self.assertEqual(captured, bytes(image)); self.assertEqual(trace, ['call-return'])

    def test_rejects_header_order_ranges_before_callbacks(self):
        requests = [HEADER.pack(b'FTDQ',1,READ,0,1,0,4), HEADER.pack(b'FTDQ',1,CALL,1,1,0,0),
                    HEADER.pack(b'FTDQ',1,3,0,1,0,0), HEADER.pack(b'FTDQ',1,CALL,0,2,0,0), b'bad']
        for request in requests:
            calls=[]; agent=OfflineDiagnosticDispatcher(lambda: calls.append(1), lambda o,n: calls.append(2))
            with self.assertRaises(ValueError): agent.dispatch(request)
            self.assertEqual(calls, []); self.assertTrue(agent.failed)

    def test_callback_failure_short_read_and_replay_poison(self):
        for result in [False, 1, None]:
            agent=OfflineDiagnosticDispatcher(lambda: result, lambda o,n: bytes(n))
            with self.assertRaises(ValueError): agent.dispatch(OfflineDiagnosticProtocol().request(CALL))
        host=OfflineDiagnosticProtocol(); agent=OfflineDiagnosticDispatcher(lambda:0, lambda o,n: b'')
        call=host.request(CALL); host.accept(agent.dispatch(call))
        with self.assertRaises(ValueError): agent.dispatch(host.request(READ,0,4))
        with self.assertRaises(ValueError): agent.dispatch(call)

    def test_transaction_budget_and_reentrant_callback(self):
        host=OfflineDiagnosticProtocol(); agent=OfflineDiagnosticDispatcher(lambda:0, lambda o,n:bytes(n))
        host.accept(agent.dispatch(host.request(CALL)))
        for _ in range(15): host.accept(agent.dispatch(host.request(READ,0,1)))
        with self.assertRaises(ValueError): host.request(READ,0,1)
        with self.assertRaises(ValueError): agent.dispatch(HEADER.pack(b'FTDQ',1,READ,0,17,0,1))
        q=OfflineDiagnosticProtocol().request(CALL)
        def callback():
            try: agent.dispatch(q)
            except ValueError: pass
            return 0
        agent=OfflineDiagnosticDispatcher(callback, lambda o,n:bytes(n))
        with self.assertRaises(ValueError): agent.dispatch(q)
