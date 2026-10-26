from array import array
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from injected_pyusb_observation import InjectedPyUSBObservation
from offline_observation_adapter import OfflineObservationAdapter
from test_injected_pyusb_observation import Device, Utilities


class ProtocolDevice(Device):
    def __init__(self,fault=None):
        super().__init__();self.fault=fault;self.pending=None;self.echo=False
    def write(self,endpoint,data,timeout):
        super().write(endpoint,data,timeout);self.pending=data;self.echo=True
        return 0 if self.fault=='write' else len(data)
    def read(self,endpoint,count,timeout):
        super().read(endpoint,count,timeout)
        if self.echo:
            self.echo=False
            return array('B',b'?' if self.fault=='echo' else self.pending)
        return array('B',bytes(count-1 if self.fault=='short' else count))


def integrate(fault=None):
    device=ProtocolDevice(fault);util=Utilities()
    if fault=='claim':
        def uncertain_claim(*args):
            util.calls.append('claim-attempt')
            raise RuntimeError('synthetic uncertain claim')
        util.claim_interface=uncertain_claim
    if fault=='release':util.fail=True
    backend=InjectedPyUSBObservation(device,util,interface=0,endpoint_in=0x81,endpoint_out=1,
        auto_detach_disabled=True,fresh_exclusive_device=True)
    adapter=OfflineObservationAdapter(backend,interface=0,commands={
        'hardware_code':b'H','hardware_versions':b'V','target_config':b'S'})
    return adapter.collect(),device,util,backend


class WrapperAdapterIntegrationTests(unittest.TestCase):
    def test_complete_adapter_uses_wrapper_endpoints_and_array_conversion(self):
        result,device,util,backend=integrate()
        self.assertTrue(result['accepted_offline_observation'])
        self.assertTrue(result['cleanup_confirmed'])
        self.assertEqual(util.calls,['claim','release','dispose'])
        self.assertEqual([x[1] for x in device.calls if isinstance(x,tuple) and x[0]=='write'],[1]*3)
        self.assertEqual([x[1] for x in device.calls if isinstance(x,tuple) and x[0]=='read'],[0x81]*6)
        self.assertFalse(result['physical_test_ready'])

    def test_transfer_faults_reject_and_release_claim(self):
        for fault in ['write','echo','short']:
            result,device,util,backend=integrate(fault)
            self.assertFalse(result['accepted_offline_observation'])
            self.assertEqual(util.calls,['claim','release','dispose'])
            self.assertEqual(len([x for x in device.calls if isinstance(x,tuple) and x[0]=='write']),1)
            if fault=='echo':
                self.assertEqual(len([x for x in device.calls if isinstance(x,tuple) and x[0]=='read']),1)

    def test_uncertain_claim_and_release_cannot_report_confirmed_cleanup(self):
        for fault in ['claim','release']:
            result,device,util,backend=integrate(fault)
            self.assertFalse(result['accepted_offline_observation'])
            self.assertFalse(result['cleanup_confirmed'])
            self.assertEqual(util.calls[-1],'dispose')
            if fault=='claim':
                self.assertTrue(backend.claim_uncertain)
                self.assertNotIn('release',util.calls)
