#!/usr/bin/env python3
"""Construct a bounded host-only PT_LOAD image; no execution or transport binding."""
import hashlib
from inspect_stage1_elf import inspect_elf


def prepare_host_image(data):
    layout = inspect_elf(data)
    segments = sorted(layout['load_segments'], key=lambda s: s['virtual_address'])
    end = max(s['virtual_address'] + s['memory_bytes'] for s in segments)
    if segments[0]['virtual_address'] != 0 or not 0 < end <= 65536:
        raise ValueError('Require zero-based image with at most 64KiB memory')
    previous_end = 0
    for segment in segments:
        start = segment['virtual_address']
        if start < previous_end:
            raise ValueError('Overlapping load memory extents')
        if segment['physical_address_field'] != start:
            raise ValueError('Physical and virtual fields differ')
        previous_end = start + segment['memory_bytes']
    image = bytearray(end)
    for segment in segments:
        start, offset, count = segment['virtual_address'], segment['offset'], segment['file_bytes']
        image[start:start + count] = data[offset:offset + count]
    result = bytes(image)
    receipt = dict(image_bytes=end, image_sha256=hashlib.sha256(result).hexdigest(),
                   entry_offset=layout['entry'],
                   segment_zero_fill_bytes=sum(s['memory_bytes'] - s['file_bytes'] for s in segments),
                   gap_zero_fill_bytes=end - sum(s['memory_bytes'] for s in segments),
                   source_elf_sha256=hashlib.sha256(data).hexdigest(),
                   purpose='host-only load-layout construction',
                   firmware_executed=False, runtime_relocation_verified=False,
                   physical_placement_verified=False, transport_binding_verified=False,
                   physical_test_ready=False)
    return result, receipt
