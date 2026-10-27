#!/usr/bin/env python3
"""Compare supplied owned ELF load images at two synthetic link bases; no execution."""
import hashlib
from inspect_stage1_elf import inspect_elf
from inspect_stage1_relocations import inspect_relocations


def normalized_image(data, base):
    if type(base) is not int or not 0<=base<=0xffffffff:
        raise ValueError('Explicit synthetic link base required')
    layout=inspect_elf(data);inspect_relocations(data)
    segments=sorted(layout['load_segments'],key=lambda s:s['virtual_address'])
    if segments[0]['virtual_address']!=base:raise ValueError('Unexpected load base')
    end=max(s['virtual_address']+s['memory_bytes'] for s in segments)
    if not 0<end-base<=65536:raise ValueError('Bounded owned image required')
    image=bytearray(end-base);previous=base
    for s in segments:
        start=s['virtual_address']
        if start<previous or s['physical_address_field']!=start:raise ValueError('Ambiguous load extent')
        offset=s['offset'];count=s['file_bytes']
        image[start-base:start-base+count]=data[offset:offset+count]
        previous=start+s['memory_bytes']
    return bytes(image),((layout['entry']&~1)-base,layout['entry']&1)


def compare_link_bases(first,second,*,second_base):
    if not second_base:raise ValueError('Distinct nonzero synthetic base required')
    a,entry_a=normalized_image(first,0);b,entry_b=normalized_image(second,second_base)
    if a!=b or entry_a!=entry_b:raise ValueError('Owned load bytes or relative entry depend on link base')
    return dict(synthetic_second_link_base=second_base,normalized_load_bytes_equal=True,
                normalized_image_bytes=len(a),normalized_image_sha256=hashlib.sha256(a).hexdigest(),
                relative_entry_offset=entry_a[0],thumb_entry=bool(entry_a[1]),
                arbitrary_runtime_relocation_verified=False,physical_placement_verified=False,
                firmware_executed=False,physical_test_ready=False)
