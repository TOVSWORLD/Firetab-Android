#!/usr/bin/env python3
"""Decode supplied target-config reply only. No device access or default flags."""
import struct


def decode_target_config(reply):
    if type(reply) is not bytes or len(reply) != 6:
        raise ValueError('Missing/unsupported/truncated target-config evidence')
    flags, status = struct.unpack('>IH', reply)
    if status != 0:
        raise ValueError('Nonzero target-config status is not accepted evidence')
    return {'sbc_reported': bool(flags & 1), 'sla_reported': bool(flags & 2),
            'daa_reported': bool(flags & 4), 'status_zero': True,
            'unknown_flag_bits_present': bool(flags & ~0xff),
            'protocol_mode_verified': False, 'response_provenance_verified': False,
            'bootstrap_authorized': False, 'physical_test_ready': False}
