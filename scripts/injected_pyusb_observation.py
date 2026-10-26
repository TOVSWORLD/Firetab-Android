#!/usr/bin/env python3
"""Explicit injected PyUSB-shaped objects only; no USB imports/discovery or CLI.

Requires a fresh exclusive device object from a separately qualified owner.
Rejects alternate settings and globally ambiguous endpoint addresses.
"""
from array import array


class InjectedPyUSBObservation:
    def __init__(self, device, utilities, *, interface, endpoint_in, endpoint_out,
                 auto_detach_disabled=False, fresh_exclusive_device=False):
        # Caller attestations, not runtime getters or permission to access devices.
        if auto_detach_disabled is not True or fresh_exclusive_device is not True:
            raise ValueError('Reviewed fresh/exclusive handle and disabled auto-detach required')
        if type(interface) is not int or not 0<=interface<=255:
            raise ValueError('Explicit interface required')
        if (type(endpoint_in) is not int or type(endpoint_out) is not int
            or not 0x81<=endpoint_in<=0x8f or not 1<=endpoint_out<=15):
            raise ValueError('Explicit non-control endpoint pair required')
        self.device=device;self.util=utilities;self.interface=interface
        self.ep_in=endpoint_in;self.ep_out=endpoint_out
        self.valid=False;self.claimed=False;self.release_failed=False;self.closed=False
        self.claim_uncertain=False

    def validate_active(self, interface):
        if self.closed or interface!=self.interface:return False
        self.valid=False
        config=self.device.get_active_configuration()
        interfaces=list(config)
        selected=[i for i in interfaces if i.bInterfaceNumber==interface]
        if len(selected)!=1 or selected[0].bAlternateSetting!=0:return False
        # PyUSB endpoint lookup scans all interfaces. Ensure unique ownership.
        for address in (self.ep_in,self.ep_out):
            matches=[(i,e) for i in interfaces for e in i if e.bEndpointAddress==address]
            if len(matches)!=1:return False
            owner,ep=matches[0]
            if owner is not selected[0] or ep.bmAttributes & 3 != 2:return False
            if type(ep.wMaxPacketSize) is not int or not 0<ep.wMaxPacketSize<=1024:return False
        self.valid=True
        return True

    def claim(self,interface):
        if not self.valid or self.closed or self.claimed or self.claim_uncertain or interface!=self.interface:return False
        self.claim_uncertain=True
        self.util.claim_interface(self.device,interface)
        self.claimed=True;self.claim_uncertain=False
        return True

    def _io(self,timeout_ms):
        if not self.claimed or self.closed:raise RuntimeError('Interface not owned')
        if type(timeout_ms) is not int or not 0<timeout_ms<=500:
            raise ValueError('Positive bounded native timeout required')

    def write(self,data,*,timeout_ms):
        self._io(timeout_ms)
        if type(data) is not bytes or not 0<len(data)<=64:raise ValueError('Bounded bytes required')
        count=self.device.write(self.ep_out,data,timeout=timeout_ms)
        if type(count) is not int or count!=len(data):raise ValueError('Short write')
        return count

    def read(self,count,*,timeout_ms):
        self._io(timeout_ms)
        if type(count) is not int or not 0<count<=64:raise ValueError('Bounded read required')
        value=self.device.read(self.ep_in,count,timeout=timeout_ms)
        if not (type(value) is bytes or isinstance(value,array) and value.typecode=='B'):
            raise ValueError('Unexpected read representation')
        if len(value)!=count:raise ValueError('Short/oversized read')
        return bytes(value)

    def release(self,interface):
        if not self.claimed or interface!=self.interface:return False
        try:self.util.release_interface(self.device,interface)
        except Exception:
            self.release_failed=True
            raise
        self.claimed=False
        return True

    def dispose(self):
        if self.closed:return False
        self.closed=True;self.valid=False
        self.util.dispose_resources(self.device)
        return not self.release_failed and not self.claimed and not self.claim_uncertain
