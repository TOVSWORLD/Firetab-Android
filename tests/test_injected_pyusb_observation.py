from array import array
from pathlib import Path
from types import SimpleNamespace as NS
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from injected_pyusb_observation import InjectedPyUSBObservation


class Interface(list):
    bInterfaceNumber=0
    bAlternateSetting=0


class Device:
    def __init__(self):
        self.config=[Interface([NS(bEndpointAddress=a,bmAttributes=2,wMaxPacketSize=64) for a in [0x81,1]])]
        self.calls=[]
    def get_active_configuration(self):self.calls.append('config');return self.config
    def write(self,endpoint,data,timeout):self.calls.append(('write',endpoint,timeout));return len(data)
    def read(self,endpoint,count,timeout):self.calls.append(('read',endpoint,timeout));return array('B',bytes(count))


class Utilities:
    def __init__(self):self.calls=[];self.fail=False
    def claim_interface(self,device,interface):self.calls.append('claim')
    def release_interface(self,device,interface):
        self.calls.append('release')
        if self.fail:raise RuntimeError('synthetic release fault')
    def dispose_resources(self,device):self.calls.append('dispose')


def make():
    device=Device();util=Utilities()
    return device,util,InjectedPyUSBObservation(device,util,interface=0,endpoint_in=0x81,endpoint_out=1,
        auto_detach_disabled=True,fresh_exclusive_device=True)


class InjectedWrapperTests(unittest.TestCase):
    def test_validated_explicit_io_bytes_and_cleanup(self):
        device,util,subject=make()
        self.assertTrue(subject.validate_active(0));self.assertTrue(subject.claim(0))
        self.assertEqual(subject.write(b'Q',timeout_ms=50),1)
        self.assertEqual(subject.read(4,timeout_ms=50),bytes(4))
        self.assertTrue(subject.release(0));self.assertTrue(subject.dispose())
        self.assertEqual(util.calls,['claim','release','dispose'])

    def test_ambiguous_endpoints_or_alternates_reject_before_claim(self):
        for fault in ['duplicate','alternate','type']:
            device,util,subject=make()
            if fault=='duplicate':device.config.append(Interface(list(device.config[0])))
            if fault=='alternate':device.config[0].bAlternateSetting=1
            if fault=='type':device.config[0][0].bmAttributes=3
            self.assertFalse(subject.validate_active(0));self.assertFalse(subject.claim(0))
            self.assertEqual(util.calls,[])

    def test_release_failure_cannot_be_hidden_by_dispose(self):
        device,util,subject=make();subject.validate_active(0);subject.claim(0);util.fail=True
        with self.assertRaises(RuntimeError):subject.release(0)
        self.assertFalse(subject.dispose())

    def test_missing_ownership_zero_timeout_and_short_read_reject(self):
        device,util,subject=make()
        with self.assertRaises(RuntimeError):subject.read(1,timeout_ms=1)
        subject.validate_active(0);subject.claim(0)
        with self.assertRaises(ValueError):subject.read(1,timeout_ms=0)
        device.read=lambda *args,**kwargs:array('B')
        with self.assertRaises(ValueError):subject.read(1,timeout_ms=1)


class HandlePolicyTests(unittest.TestCase):
    def test_missing_or_truthy_nonboolean_attestations_reject_without_calls(self):
        for detach,fresh in [(False,True),(True,False),(1,True),(True,1),(None,None)]:
            device=Device();util=Utilities()
            with self.assertRaises(ValueError):
                InjectedPyUSBObservation(device,util,interface=0,endpoint_in=0x81,endpoint_out=1,
                    auto_detach_disabled=detach,fresh_exclusive_device=fresh)
            self.assertEqual(device.calls,[])
            self.assertEqual(util.calls,[])
