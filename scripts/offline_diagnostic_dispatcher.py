#!/usr/bin/env python3
"""Host-only protocol model with injected synthetic callbacks, no I/O or agent binding."""
from offline_diagnostic_protocol import HEADER, CALL, READ, IMAGE_BYTES, MAX_READ


class OfflineDiagnosticDispatcher:
    def __init__(self, call_fixed_slot, read_image):
        self.call_fixed_slot = call_fixed_slot
        self.read_image = read_image
        self.sequence = 0
        self.called = False
        self.failed = False
        self.busy = False

    def dispatch(self, request):
        try:
            if self.failed or self.busy or type(request) is not bytes or len(request) != HEADER.size:
                raise ValueError('Invalid session or request frame')
            magic, version, operation, reserved, sequence, offset, length = HEADER.unpack(request)
            if (magic, version, reserved) != (b'FTDQ', 1, 0) or sequence != self.sequence + 1 or sequence > 16:
                raise ValueError('Header or bounded sequence mismatch')
            if operation == CALL:
                if self.called or offset or length:
                    raise ValueError('Invalid single fixed-slot call')
            elif operation == READ:
                if not self.called or not 1 <= length <= MAX_READ or not 0 <= offset <= IMAGE_BYTES - length:
                    raise ValueError('Invalid image read range or order')
            else:
                raise ValueError('Unknown operation')
            self.busy = True
            if operation == CALL:
                result = self.call_fixed_slot()
                if type(result) is not int or result != 0:
                    raise ValueError('Synthetic call callback failed')
                self.called = True
                payload = b''
            else:
                payload = self.read_image(offset, length)
                if type(payload) is not bytes or len(payload) != length:
                    raise ValueError('Synthetic read callback returned wrong extent')
            if self.failed:
                raise ValueError('Callback reentered and invalidated session')
            self.sequence = sequence
            return HEADER.pack(b'FTDR', 1, operation, 0, sequence, offset, length) + payload
        except Exception:
            self.failed = True
            raise ValueError('Request rejected; dispatcher unusable') from None
        finally:
            self.busy = False
