#!/usr/bin/env python3
"""Compile an isolated diagnostic initramfs; never pack a boot image or use devices."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'projects/firetabs-android/diagnostic/init.c'


def archive(entries):
    """Deterministic newc, uid/gid/time zero; entries are (name, mode, data, rdev)."""
    result = bytearray()
    for ino, (name, mode, data, device) in enumerate(entries + [('TRAILER!!!', 0, b'', (0, 0))], 1):
        encoded = name.encode('ascii') + b'\0'
        fields = [ino, mode, 0, 0, 1, 0, len(data), 0, 0, *device, len(encoded), 0]
        result.extend(b'070701' + b''.join(f'{x:08x}'.encode() for x in fields))
        result.extend(encoded)
        result.extend(b'\0' * (-len(result) % 4))
        result.extend(data)
        result.extend(b'\0' * (-len(result) % 4))
    result.extend(b'\0' * (-len(result) % 512))
    return bytes(result)


def inspect_elf(data):
    if len(data) < 64 or data[:7] != b'\x7fELF\x02\x01\x01':
        raise ValueError('Expected little-endian ELF64')
    kind, machine = struct.unpack_from('<HH', data, 16)
    if kind != 2 or machine != 183:
        raise ValueError('Expected AArch64 ET_EXEC')
    offset = struct.unpack_from('<Q', data, 32)[0]
    size, count = struct.unpack_from('<HH', data, 54)
    if size != 56 or count == 0 or offset + size * count > len(data):
        raise ValueError('Invalid ELF program headers')
    entry = struct.unpack_from('<Q', data, 24)[0]
    executable_entry = False
    for i in range(count):
        ptype, flags, fileoff, va, _, filesz, memsz, _ = struct.unpack_from('<IIQQQQQQ', data, offset + i * size)
        if ptype in (2, 3):
            raise ValueError('Dynamic segment or interpreter forbidden')
        if ptype == 1:
            if filesz > memsz or fileoff + filesz > len(data):
                raise ValueError('Invalid load segment')
            if flags & 1 and va <= entry < va + filesz:
                executable_entry = True
    if not executable_entry:
        raise ValueError('Entry is not in an executable file-backed load segment')
    return {'machine': 'AArch64', 'type': 'ET_EXEC', 'dynamic': False, 'entry': hex(entry)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--clang', default='clang-18')
    parser.add_argument('--output', type=Path, default=ROOT / 'out/diagnostic-initramfs')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    elf = args.output / 'init'
    command = [args.clang, '--target=aarch64-linux-gnu', '-fuse-ld=lld', '-nostdlib', '-static',
               '-Os', '-Wall', '-Wextra', '-Werror', '-ffreestanding', '-fno-builtin',
               '-fno-stack-protector', '-mgeneral-regs-only', '-Wl,--build-id=none,-e,_start',
               '-o', str(elf), str(SOURCE)]
    subprocess.run(command, check=True)
    data = elf.read_bytes()
    inspection = inspect_elf(data)
    entries = [(n, 0o040755, b'', (0, 0)) for n in ['dev', 'proc', 'sys']]
    entries += [('dev/console', 0o020600, b'', (5, 1)), ('init', 0o100755, data, (0, 0))]
    cpio = archive(entries)
    packed = bytearray(gzip.compress(cpio, mtime=0))
    packed[9] = 255  # Normalize Python 3.12 versus 3.13+ gzip OS metadata.
    packed = bytes(packed)
    (args.output / 'initramfs.cpio.gz').write_bytes(packed)
    artifacts = {'init': data, 'initramfs.cpio.gz': packed}
    report = {'scope': 'Isolated diagnostic userspace compilation, not a boot image or device test',
              'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              'cpu_contract_header_sha256': hashlib.sha256(SOURCE.with_name('cpu_contract.h').read_bytes()).hexdigest(),
              'compiler': subprocess.check_output([args.clang, '--version'], text=True).splitlines()[0],
              'command': [x.replace(str(ROOT), '<workspace>') for x in command],
              'elf': inspection, 'archive_entries': [x[0] for x in entries],
              'artifacts': {n: {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()} for n, b in artifacts.items()},
              'boot_tested': False, 'hardware_tested': False}
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
