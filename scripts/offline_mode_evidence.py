#!/usr/bin/env python3
"""Classify supplied fresh reply fields without querying or proving device mode."""


def decode_mode_reply(*, query_byte, reply):
    if type(query_byte) is not bytes or len(query_byte) != 1:
        raise ValueError('Explicit single-byte mode query contract required')
    if type(reply) is not bytes or len(reply) != 1:
        raise ValueError('Missing/unsupported/ambiguous mode evidence')
    matches = reply == query_byte
    return {'reply_matches_mode_query': matches,
            'source_candidate': 'brom_echo' if matches else 'unknown',
            'protocol_mode_verified': False, 'response_provenance_verified': False,
            'bootstrap_authorized': False, 'physical_test_ready': False}
