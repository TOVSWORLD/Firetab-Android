import unittest
from test_injected_pyusb_observation import make
from offline_diagnostic_dispatcher import OfflineDiagnosticDispatcher
from injected_diagnostic_capture import capture_injected


class FramedCaptureTests(unittest.TestCase):
    def fixture(self):
        device, utilities, backend = make(); image=bytearray(1080); buffer=bytearray(); writes=[]
        def call(): image[48]=0x31;return 0
        agent=OfflineDiagnosticDispatcher(call, lambda o,n:bytes(image[o:o+n]))
        def write(endpoint,data,timeout):
            writes.append(data);buffer.extend(agent.dispatch(data));return len(data)
        def read(endpoint,count,timeout):
            result=bytes(buffer[:count]);del buffer[:count];return result
        device.write=write;device.read=read
        return device,utilities,backend,writes

    def test_exact_framed_capture_through_injected_wrapper(self):
        _,util,backend,writes=self.fixture()
        result=capture_injected(backend,interface=0,clock=lambda:0.0)
        self.assertEqual(len(result['snapshot']),1080);self.assertEqual(result['snapshot'][48],0x31)
        self.assertEqual(len(writes),6);self.assertEqual(util.calls,['claim','release','dispose'])
        self.assertFalse(result['runtime_execution_verified'])

    def test_partial_send_and_cleanup_failure_discard_without_retry(self):
        device,util,backend,writes=self.fixture()
        original=device.write
        def partial(*args,**kwargs): original(*args,**kwargs);return 1
        device.write=partial
        with self.assertRaises(ValueError):capture_injected(backend,interface=0,clock=lambda:0.0)
        self.assertEqual(len(writes),1);self.assertEqual(util.calls,['claim','release','dispose'])
        _,util,backend,_=self.fixture();util.fail=True
        with self.assertRaises(ValueError):capture_injected(backend,interface=0,clock=lambda:0.0)

    def test_late_write_discards_and_cleans_up(self):
        device,util,backend,writes=self.fixture();time=[0.0];original=device.write
        def late(*args,**kwargs):result=original(*args,**kwargs);time[0]=6.0;return result
        device.write=late
        with self.assertRaises(ValueError):capture_injected(backend,interface=0,clock=lambda:time[0])
        self.assertEqual(len(writes),1);self.assertEqual(util.calls,['claim','release','dispose'])

    def test_late_claim_still_attempts_release(self):
        _,util,backend,writes=self.fixture();time=[0.0];original=backend.claim
        def late(interface):
            result=original(interface);time[0]=6.0;return result
        backend.claim=late
        with self.assertRaises(ValueError):capture_injected(backend,interface=0,clock=lambda:time[0])
        self.assertEqual(writes,[]);self.assertEqual(util.calls,['claim','release','dispose'])
