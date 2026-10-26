#!/usr/bin/env python3
"""Decode supplied host snapshots only; no acquisition, USB, or execution."""
import hashlib
import re

MARKER = (0x46544b31).to_bytes(4, 'little')
LAYOUTS = {'entry': (36, 40, 1064), 'callable': (48, 56, 1080)}


def decode_marker(image, before, after, *, variant, expected_image_sha256):
    if variant not in LAYOUTS:
        raise ValueError('Unknown diagnostic variant')
    if not isinstance(expected_image_sha256, str) or not re.fullmatch('[0-9a-f]{64}', expected_image_sha256):
        raise ValueError('Expected reviewed lowercase SHA256')
    marker, stack, total = LAYOUTS[variant]
    if any(type(value) is not bytes or len(value) != total for value in (image, before, after)):
        raise ValueError('Exact immutable snapshot sizes required')
    if hashlib.sha256(image).hexdigest() != expected_image_sha256:
        raise ValueError('Image identity mismatch')
    if image[marker:marker + 4] != bytes(4) or before != image:
        raise ValueError('Require pristine supplied before snapshot')
    if after[:marker] != image[:marker] or after[marker + 4:stack] != image[marker + 4:stack]:
        raise ValueError('Code or layout padding differs')
    value = after[marker:marker + 4]
    if value not in (bytes(4), MARKER):
        raise ValueError('Unknown marker value')
    return dict(variant=variant, supplied_marker_transition=(value == MARKER),
                image_sha256=expected_image_sha256,
                after_snapshot_sha256=hashlib.sha256(after).hexdigest(),
                stack_bytes_changed=sum(a != b for a, b in zip(before[stack:], after[stack:])),
                acquisition_origin_verified=False, freshness_verified=False,
                runtime_execution_verified=False, caller_return_verified=False,
                physical_test_ready=False)
