#!/usr/bin/env python3
"""Ordered response-event collector only: no USB, native helper, sender or CLI.

Event order models received fields, not the full bidirectional wire protocol.
A timeout is reported through abort(); this class cannot enforce native deadlines.
"""
from offline_dram_evidence import FIELDS, decode


class OfflineDramSession:
    def __init__(self, *, expected_ack, local_emi_bytes):
        if type(expected_ack) is not bytes or len(expected_ack) != 1:
            raise ValueError('Explicit ACK required')
        if type(local_emi_bytes) is not int or not 0 < local_emi_bytes <= 65536:
            raise ValueError('Bounded local EMI extent required')
        self.ack = expected_ack
        self.extent = local_emi_bytes
        self.fields = {}
        self.state = 'collecting'
        self.order = tuple(FIELDS)

    def abort(self):
        self.fields.clear()
        self.state = 'invalid'

    def accept(self, name, data):
        if self.state != 'collecting':
            self.abort()
            raise RuntimeError('Session is not collecting; create a new session')
        try:
            expected = self.order[len(self.fields)]
            if name != expected or type(data) is not bytes or len(data) != FIELDS[expected]:
                raise ValueError('Out-of-order or malformed response event')
            if name == 'version_reply' and data != self.ack:
                raise ValueError('Unexpected version reply')
            if name == 'requested_length' and int.from_bytes(data, 'big') != self.extent:
                raise ValueError('EMI extent disagreement')
            if name == 'status' and int.from_bytes(data, 'big') != 0:
                raise ValueError('Initialization failure')
            self.fields[name] = data
            if len(self.fields) == len(self.order):
                result = decode(self.fields, expected_ack=self.ack, local_emi_bytes=self.extent)
                self.fields.clear()
                self.state = 'decoded'
                return result
            return None
        except BaseException:
            self.abort()
            raise
