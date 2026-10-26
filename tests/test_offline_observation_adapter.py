from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from offline_observation_adapter import OfflineObservationAdapter


class FakeBackend:
    def __init__(self, fault=None):self.calls=[];self.fault=fault;self.pending=None;self.echo=False
    def validate_active(self,interface):self.calls.append('validate');return self.fault!='config'
    def claim(self,interface):self.calls.append('claim');return self.fault!='claim'
    def write(self,data,timeout_ms):
        self.calls.append('write');self.pending=data;self.echo=True
        assert 0<timeout_ms<=500
        return 0 if self.fault=='write' else 1
    def read(self,size,timeout_ms):
        self.calls.append('read');assert 0<timeout_ms<=500
        if self.echo:
            self.echo=False;return b'?' if self.fault=='echo' else self.pending
        return bytes(size-1 if self.fault=='short' else size)
    def release(self,interface):self.calls.append('release');return self.fault!='release'
    def dispose(self):self.calls.append('dispose');return self.fault!='dispose'


def adapter(backend):
    return OfflineObservationAdapter(backend,interface=0,commands={
        'hardware_code':b'H','hardware_versions':b'V','target_config':b'S'})


class AdapterSequenceTests(unittest.TestCase):
    def test_success_only_uses_reviewed_operations_and_cleans_up(self):
        backend=FakeBackend();subject=adapter(backend);result=subject.collect()
        self.assertTrue(result['accepted_offline_observation'])
        self.assertEqual(backend.calls,['validate','claim']+['write','read','read']*3+['release','dispose'])
        self.assertFalse(result['bootstrap_authorized'])
        with self.assertRaises(RuntimeError):subject.collect()

    def test_configuration_or_claim_failure_has_no_protocol_traffic(self):
        for fault in ['config','claim']:
            backend=FakeBackend(fault);result=adapter(backend).collect()
            self.assertFalse(result['accepted_offline_observation'])
            self.assertNotIn('write',backend.calls)
            self.assertNotIn('release',backend.calls)
            self.assertEqual(backend.calls[-1],'dispose')

    def test_io_faults_abort_and_cleanup_faults_discard_success(self):
        for fault in ['write','echo','short','release','dispose']:
            backend=FakeBackend(fault);result=adapter(backend).collect()
            self.assertFalse(result['accepted_offline_observation'])
            self.assertEqual(backend.calls[-2:],['release','dispose'])
