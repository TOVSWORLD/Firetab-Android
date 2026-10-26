#!/usr/bin/env python3
"""Owned wire specification for supplied bytes; no transport, agent or firmware execution."""
import struct

HEADER = struct.Struct('<4sBBHIHH')
CALL = 1
READ = 2
IMAGE_BYTES = 1080
MAX_READ = 256


class OfflineDiagnosticProtocol:
    def __init__(self):
        self.sequence = 0
        self.pending = None
        self.failed = False
        self.call_completed = False

    def request(self, operation, offset=0, length=0):
        if self.failed or self.pending is not None:
            raise ValueError('Failed or pending transaction')
        if type(operation) is not int or type(offset) is not int or type(length) is not int:
            raise ValueError('Integer fields required')
        if operation == CALL:
            if self.call_completed or offset or length:
                raise ValueError('Single fixed-slot call has no address or payload')
        elif operation == READ:
            if not self.call_completed or not 1 <= length <= MAX_READ or not 0 <= offset <= IMAGE_BYTES - length:
                raise ValueError('Read requires completed call and bounded image-relative range')
        else:
            raise ValueError('Unknown operation')
        if self.sequence == 0xffffffff:
            raise ValueError('Sequence exhausted')
        self.sequence += 1
        self.pending = (operation, self.sequence, offset, length)
        return HEADER.pack(b'FTDQ', 1, operation, 0, self.sequence, offset, length)

    def accept(self, response):
        try:
            if self.failed or self.pending is None or type(response) is not bytes or len(response) < HEADER.size:
                raise ValueError('No transaction or invalid response')
            magic, version, operation, status, sequence, offset, length = HEADER.unpack_from(response)
            if (magic, version, status) != (b'FTDR', 1, 0):
                raise ValueError('Invalid completion status/version/magic')
            if (operation, sequence, offset, length) != self.pending or len(response) != HEADER.size + length:
                raise ValueError('Completion identity or exact length mismatch')
            if operation == CALL:
                self.call_completed = True
            self.pending = None
            return response[HEADER.size:]
        except (ValueError, struct.error):
            self.failed = True
            self.pending = None
            raise ValueError('Transaction rejected; session unusable') from None

    def abandon(self):
        """Caller records timeout/partial I/O; this model provides no deadline or cancellation."""
        self.failed = True
        self.pending = None
