#!/usr/bin/env python3
"""Inspect bounded ARM ELF load metadata without executing or disassembling it."""
import struct


def inspect_elf(data):
    if not 52 <= len(data) <= 1024 * 1024:
        raise ValueError('ELF size outside probe bounds')
    if data[:7] != b'\x7fELF\x01\x01\x01':
        raise ValueError('Expected ELF32 little-endian version 1')
    fields = struct.unpack_from('<HHIIIIIHHHHHH', data, 16)
    kind, machine, version, entry, phoff, _, _, ehsize, phsize, phnum, *_ = fields
    if (kind, machine, version, ehsize) != (2, 40, 1, 52):
        raise ValueError('Expected ARM executable header')
    if not 1 <= phnum <= 32 or phsize != 32 or phoff < 52 or phoff + phsize * phnum > len(data):
        raise ValueError('Invalid program header table')
    loads = []
    for index in range(phnum):
        tag, offset, virtual, physical, filesz, memsz, flags, align = struct.unpack_from('<8I', data, phoff + index * phsize)
        if tag != 1:
            continue
        if filesz > memsz or offset + filesz > len(data) or virtual + memsz > 2**32:
            raise ValueError('Invalid load segment extent')
        if align not in (0, 1) and (align & (align - 1) or virtual % align != offset % align):
            raise ValueError('Invalid load segment alignment')
        loads.append(dict(offset=offset, virtual_address=virtual, physical_address_field=physical,
                          file_bytes=filesz, memory_bytes=memsz, flags=flags, alignment=align))
    if not loads:
        raise ValueError('No load segments')
    address = entry & ~1  # ARM ELF may encode Thumb state in entry bit 0.
    covered = any(s['flags'] & 1 and s['virtual_address'] <= address < s['virtual_address'] + s['file_bytes'] for s in loads)
    if not covered:
        raise ValueError('Entry is not backed by executable file bytes')
    return dict(entry=entry, entry_executable_file_coverage=True, load_segments=loads,
                runtime_placement_verified=False, flat_transport_payload_verified=False)
