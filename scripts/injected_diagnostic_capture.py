#!/usr/bin/env python3
"""Injected host objects only; no USB discovery/import, CLI, device binding or execution."""
import math
from offline_diagnostic_protocol import OfflineDiagnosticProtocol, HEADER, CALL, READ, IMAGE_BYTES


def capture_injected(backend, *, interface, clock):
    protocol = OfflineDiagnosticProtocol()
    start = clock()
    if not math.isfinite(start): raise ValueError('Finite monotonic clock required')
    deadline = start + 5.0
    last = start
    claimed = False
    snapshot = bytearray()
    call_may_have_run = False
    failure = None

    def remaining():
        nonlocal last
        now = clock()
        if not math.isfinite(now) or now < last or now >= deadline:
            raise ValueError('Session deadline/clock rejected')
        last = now
        return max(1, min(500, int((deadline-now)*1000)))

    def invoke(function, *args, **kwargs):
        remaining()
        result = function(*args, **kwargs)
        remaining()
        return result

    def transaction(operation, offset=0, length=0):
        nonlocal call_may_have_run
        frame = protocol.request(operation, offset, length)
        if operation == CALL: call_may_have_run = True
        if invoke(backend.write, frame, timeout_ms=remaining()) != len(frame):
            raise ValueError('Partial send; completion uncertain, never retry')
        header = invoke(backend.read, HEADER.size, timeout_ms=remaining())
        if type(header) is not bytes or len(header) != HEADER.size:
            raise ValueError('Exact response header required')
        # Reject corrupt range/identity before scheduling any payload reads.
        magic, version, op, status, sequence, echo_offset, echo_length = HEADER.unpack(header)
        if (magic,version,op,status,sequence,echo_offset,echo_length) != (
                b'FTDR',1,operation,0,protocol.sequence,offset,length):
            raise ValueError('Response header mismatch')
        payload = bytearray()
        while len(payload) < length:
            count = min(64, length-len(payload))
            chunk = invoke(backend.read, count, timeout_ms=remaining())
            if type(chunk) is not bytes or len(chunk) != count: raise ValueError('Short payload')
            payload.extend(chunk)
        return protocol.accept(header + bytes(payload))

    try:
        if invoke(backend.validate_active, interface) is not True: raise ValueError('Invalid active interface')
        claimed = True  # Attempt release even if claim returns late/uncertain.
        if invoke(backend.claim, interface) is not True: raise ValueError('Claim failed')
        transaction(CALL)
        for offset in range(0, IMAGE_BYTES, 256):
            snapshot.extend(transaction(READ, offset, min(256,IMAGE_BYTES-offset)))
    except Exception as error:
        protocol.abandon(); failure = error
    finally:
        # Cleanup still attempted after deadline; it is not preemptible by this clock.
        try:
            if claimed and backend.release(interface) is not True: raise ValueError('Release failed')
        except Exception as error:
            failure = error
        try:
            if backend.dispose() is not True: raise ValueError('Disposal uncertain')
        except Exception as error:
            failure = error
    try:
        remaining()
    except Exception as error:
        failure = error
    if failure is not None:
        raise ValueError('Capture discarded; call completion may be uncertain; never retry automatically') from failure
    return dict(snapshot=bytes(snapshot), call_may_have_run=call_may_have_run,
                acquisition_origin_verified=False, runtime_execution_verified=False,
                physical_test_ready=False)
