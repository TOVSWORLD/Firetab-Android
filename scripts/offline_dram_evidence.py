#!/usr/bin/env python3
"""Decode explicit synthetic/captured response fields; no transport or stage sender.

Callers supply field boundaries, not an arbitrary concatenated wire capture.
Successful decoding never authorizes loading: integrity and provenance are unknown.
"""
import struct

FIELDS = {'version_reply': 1, 'requested_length': 4, 'checksum': 2,
          'status': 4, 'ram_type': 1, 'chip_select': 1, 'ram_bytes': 8}


def decode(fields, *, expected_ack, local_emi_bytes):
    if type(expected_ack) is not bytes or len(expected_ack) != 1:
        raise ValueError('Explicit single-byte ACK contract required')
    if type(local_emi_bytes) is not int or not 0 < local_emi_bytes <= 65536:
        raise ValueError('Bounded local EMI extent required')
    if type(fields) is not dict or set(fields) != set(FIELDS):
        raise ValueError('Complete exact response field set required')
    for name, size in FIELDS.items():
        if type(fields[name]) is not bytes or len(fields[name]) != size:
            raise ValueError('Malformed response field: ' + name)
    if fields['version_reply'] != expected_ack:
        raise ValueError('Version reply is not the explicit expected ACK')
    requested = struct.unpack('>I', fields['requested_length'])[0]
    if requested != local_emi_bytes:
        raise ValueError('Requested and local EMI extents disagree')
    status = struct.unpack('>I', fields['status'])[0]
    if status != 0:
        raise ValueError('Agent reports initialization failure')
    size = struct.unpack('>Q', fields['ram_bytes'])[0]
    if size == 0:
        raise ValueError('Zero agent-reported memory size')
    return {'complete_response_fields_decoded': True,
            'agent_reported_ram_bytes': size,
            'agent_reported_ram_type': fields['ram_type'][0],
            'agent_reported_chip_select': fields['chip_select'][0],
            'requested_emi_bytes': requested,
            'checksum_received': True, 'checksum_integrity_verified': False,
            'response_provenance_verified': False,
            'dram_capacity_or_layout_verified': False,
            'stage_transfer_authorized': False, 'physical_test_ready': False}
