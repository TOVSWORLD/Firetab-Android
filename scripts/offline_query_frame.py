#!/usr/bin/env python3
"""Validate explicit supplied query echo/payload fields; no wire IO or command constants."""


def validate_frame(*, command, echo, payload, expected_bytes):
    if type(command) is not bytes or len(command) != 1:
        raise ValueError('Explicit single-byte command contract required')
    if type(expected_bytes) is not int or not 0 < expected_bytes <= 64:
        raise ValueError('Bounded query response extent required')
    if type(echo) is not bytes or echo != command:
        raise ValueError('Missing/mismatched command echo')
    if type(payload) is not bytes or len(payload) != expected_bytes:
        raise ValueError('Missing/truncated/oversized query response')
    return payload
