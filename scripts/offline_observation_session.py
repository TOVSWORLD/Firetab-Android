#!/usr/bin/env python3
"""Symbolic observation callbacks only; no command bytes, USB or helper binding.

Callbacks must honor the supplied positive timeout. This cooperative budget
cannot preempt blocked native code; a live binding also needs worker supervision.
"""
import math
import struct
import time
from offline_security_observation import decode_target_config


class OfflineObservationSession:
    def __init__(self, query, *, budget_seconds=5, clock=time.monotonic):
        if not callable(query):
            raise ValueError('Query callback required')
        if type(budget_seconds) not in (int,float) or not math.isfinite(budget_seconds) or not 0 < budget_seconds <= 30:
            raise ValueError('Positive bounded session budget required')
        self.query=query; self.budget=budget_seconds; self.clock=clock; self.state='new'

    def collect(self):
        if self.state != 'new':
            raise RuntimeError('Observation session cannot be reused')
        self.state='collecting'
        try:
            end=self.clock()+self.budget
            replies={}
            for name,size in [('hardware_code',4),('hardware_versions',8),('target_config',6)]:
                remaining=end-self.clock()
                if remaining <= 0:raise TimeoutError('Observation deadline expired')
                reply=self.query(name,timeout_ms=max(1,min(1000,math.ceil(remaining*1000))))
                if self.clock() >= end:raise TimeoutError('Callback exceeded observation deadline')
                if type(reply) is not bytes or len(reply) != size:
                    raise ValueError('Missing or malformed observation reply')
                if name == 'hardware_versions' and int.from_bytes(reply[6:], 'big') != 0:
                    raise ValueError('Hardware-version status is not zero')
                replies[name]=reply
            hwcode,initial_hwver=struct.unpack('>HH',replies['hardware_code'])
            subcode,hwver,swver,status=struct.unpack('>HHHH',replies['hardware_versions'])
            if status != 0:raise ValueError('Hardware-version status is not zero')
            security=decode_target_config(replies['target_config'])
            self.state='complete'
            return {'reported_hardware_code':hwcode,'reported_initial_hw_version':initial_hwver,
                    'reported_subcode':subcode,'reported_hw_version':hwver,'reported_sw_version':swver,
                    'security':security,'protocol_mode_verified':False,'physical_test_ready':False,
                    'bootstrap_authorized':False,'response_provenance_verified':False}
        except BaseException:
            self.state='invalid'
            raise
