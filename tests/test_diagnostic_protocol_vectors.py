"""Compare native host C core against Python; no target execution or device I/O."""
import pathlib
import shutil
import struct
import subprocess
import tempfile
import unittest
from offline_diagnostic_dispatcher import OfflineDiagnosticDispatcher
from offline_diagnostic_protocol import HEADER, CALL, READ, OfflineDiagnosticProtocol


class ProtocolVectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cc = shutil.which('cc')
        if not cc: raise unittest.SkipTest('Host C compiler unavailable')
        cls.folder = tempfile.TemporaryDirectory(); cls.addClassCleanup(cls.folder.cleanup)
        root = pathlib.Path(__file__).resolve().parents[1]
        cls.runner = pathlib.Path(cls.folder.name)/'native-vectors'
        subprocess.run([cc,'-std=c11','-Wall','-Wextra','-Werror','-I',str(root/'diagnostic/protocol'),
                        str(root/'diagnostic/protocol/dispatcher.c'),
                        str(root/'tests/native/diagnostic_vector_runner.c'),'-o',str(cls.runner)],
                       check=True,capture_output=True,timeout=30)

    def compare(self, requests):
        image=bytearray(1080)
        def call(): image[48]=0x31; return 0
        model=OfflineDiagnosticDispatcher(call, lambda o,n:bytes(image[o:o+n]))
        expected=b''; responses=[]
        for request in requests:
            try:
                response=model.dispatch(request); status=0
            except ValueError:
                response=b''; status=1
            expected+=bytes([status])+struct.pack('<H',len(response))+response
            responses.append(response)
        input_bytes=b''.join(struct.pack('<H',len(q))+q for q in requests)
        actual=subprocess.run([str(self.runner)],input=input_bytes,capture_output=True,check=True,timeout=5).stdout
        self.assertEqual(actual,expected)
        return responses

    def test_full_image_vectors_accepted_by_host_contract(self):
        requests=[HEADER.pack(b'FTDQ',1,CALL,0,1,0,0)]
        for seq,offset in enumerate(range(0,1080,256),2):
            requests.append(HEADER.pack(b'FTDQ',1,READ,0,seq,offset,min(256,1080-offset)))
        responses=self.compare(requests); host=OfflineDiagnosticProtocol()
        host.request(CALL);host.accept(responses[0]);captured=b''
        for offset,response in zip(range(0,1080,256),responses[1:]):
            host.request(READ,offset,min(256,1080-offset));captured+=host.accept(response)
        self.assertEqual(len(captured),1080);self.assertEqual(captured[48],0x31)

    def test_sixty_four_header_mutations_and_sticky_followup(self):
        call=HEADER.pack(b'FTDQ',1,CALL,0,1,0,0)
        for offset in range(16):
            for mask in (1,2,64,128):
                changed=bytearray(call);changed[offset]^=mask
                self.compare([bytes(changed),call])

    def test_budget_read_boundaries_and_truncated_requests(self):
        call=HEADER.pack(b'FTDQ',1,CALL,0,1,0,0)
        self.compare([call]+[HEADER.pack(b'FTDQ',1,READ,0,s,0,1) for s in range(2,18)])
        for offset,length in [(1079,1),(1080,1),(0,256),(0,257),(0,0),(65535,1)]:
            self.compare([call,HEADER.pack(b'FTDQ',1,READ,0,2,offset,length)])
        for n in (0,1,15,17):self.compare([call[:n] if n<=16 else call+b'x',call])
