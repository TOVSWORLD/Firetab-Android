#!/usr/bin/env python3
"""Exact packet-read contract with positive native deadlines; callbacks only, no USB."""
import math
import time
from offline_escrow_capture import MAX_CHUNK


class OfflineDeadlineReader:
    """A callback must honor timeout=milliseconds; this cannot preempt native code.

    No protocol checksum/reconnect behavior is inferred. Any failure poisons the
    stream until a separately qualified transport creates a new reader.
    """
    def __init__(self, read_packet, *, packet_bytes, deadline_seconds, max_native_ms=1000,
                 clock=time.monotonic):
        if type(packet_bytes) is not int or not 0<packet_bytes<=MAX_CHUNK:
            raise ValueError('Invalid packet budget')
        if (type(deadline_seconds) not in (int,float) or not math.isfinite(deadline_seconds)
            or not 0<deadline_seconds<=60):
            raise ValueError('Invalid logical-read deadline')
        if type(max_native_ms) is not int or not 0<max_native_ms<=60000:
            raise ValueError('Positive bounded native timeout required')
        self.packet=read_packet;self.packet_bytes=packet_bytes
        self.deadline=deadline_seconds;self.max_native_ms=max_native_ms;self.clock=clock
        self.leftover=bytearray();self.failed=False

    def read_exact(self, count):
        if self.failed:raise RuntimeError('Transport stream invalid after prior failure')
        try:
            if type(count) is not int or not 0<count<=MAX_CHUNK:
                raise ValueError('Invalid exact-read extent')
            end=self.clock()+self.deadline;result=bytearray()
            take=min(count,len(self.leftover));result.extend(self.leftover[:take]);del self.leftover[:take]
            while len(result)<count:
                remaining=end-self.clock()
                if remaining<=0:raise TimeoutError('Logical read deadline expired')
                timeout=max(1,min(self.max_native_ms,math.ceil(remaining*1000)))
                data=self.packet(self.packet_bytes,timeout=timeout)
                if self.clock()>=end:raise TimeoutError('Packet returned after logical deadline')
                if not isinstance(data,bytes) or not 0<len(data)<=self.packet_bytes:
                    raise ValueError('Empty/invalid/oversized packet; stream invalid')
                take=min(count-len(result),len(data));result.extend(data[:take]);self.leftover.extend(data[take:])
            return bytes(result)
        except BaseException:
            self.failed=True;self.leftover.clear()
            raise
