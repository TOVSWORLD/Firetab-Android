#!/usr/bin/env python3
"""Bounded section-table inspection; absence of relocations is not runtime PIC proof."""
import struct
from inspect_stage1_elf import inspect_elf


def inspect_relocations(data):
    inspect_elf(data)
    offset = struct.unpack_from('<I', data, 32)[0]
    size, count = struct.unpack_from('<HH', data, 46)
    if not count or count > 256 or size != 40 or offset < 52 or offset + count * size > len(data):
        raise ValueError('Require bounded ordinary section table')
    relocation_sections = 0
    dynamic_sections = 0
    for index in range(count):
        fields = struct.unpack_from('<10I', data, offset + index * size)
        _, kind, _, _, start, length, _, _, _, entry_size = fields
        if kind != 8 and start + length > len(data):  # NOBITS has no file extent.
            raise ValueError('Section outside file')
        if kind in (4, 9):
            expected = 12 if kind == 4 else 8
            if entry_size != expected or length % expected:
                raise ValueError('Invalid relocation record layout')
            if length:
                relocation_sections += 1
        if kind == 6 and length:
            dynamic_sections += 1
    if relocation_sections or dynamic_sections:
        raise ValueError('Unresolved relocation or dynamic section requires separate loader')
    return dict(section_count=count, nonempty_relocation_sections=0,
                nonempty_dynamic_sections=0, runtime_position_independence_verified=False)
