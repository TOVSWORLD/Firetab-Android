#!/usr/bin/env python3
"""User-run, read-only douglas metadata collection. Never run automatically in CI."""
import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import threading

PROPERTIES = ('ro.product.manufacturer', 'ro.product.model', 'ro.product.device',
              'ro.build.version.release', 'ro.build.version.sdk', 'ro.build.display.id',
              'ro.build.version.incremental', 'ro.build.fingerprint', 'ro.bootloader',
              'ro.hardware', 'ro.board.platform', 'ro.bootmode')
PROC_FILES = ('meminfo', 'iomem', 'partitions')
CMDLINE_KEYS = {'console', 'earlycon', 'bootopt', 'mem', 'maxcpus', 'nr_cpus',
                'androidboot.hardware', 'androidboot.bootloader',
                'androidboot.verifiedbootstate', 'androidboot.unlocked_kernel'}


@dataclass
class Result:
    code: int
    stdout: bytes = b''
    stderr: bytes = b''
    truncated: bool = False
    timed_out: bool = False


def bounded_run(command, timeout=15, limit=1024 * 1024):
    """Bound both pipe buffers and runtime without relying on device cooperation."""
    process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    buffers = [bytearray(), bytearray()]
    truncated = threading.Event()
    def read(pipe, buffer):
        with pipe:
            while True:
                chunk = pipe.read(4096)
                if not chunk:
                    return
                remaining = limit - len(buffer)
                buffer.extend(chunk[:remaining])
                if len(chunk) > remaining:
                    truncated.set()
                    try:
                        process.kill()
                    except ProcessLookupError:
                        pass
                    return
    threads = [threading.Thread(target=read, args=(pipe, buffer), daemon=True)
               for pipe, buffer in zip([process.stdout, process.stderr], buffers)]
    for thread in threads:
        thread.start()
    timed_out = False
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        process.wait()
    for thread in threads:
        thread.join(timeout=2)
    return Result(process.returncode, bytes(buffers[0]), bytes(buffers[1]), truncated.is_set(), timed_out)


class ADBReader:
    def __init__(self, adb, serial):
        if not re.fullmatch(r'[A-Za-z0-9_.:-]+', serial):
            raise ValueError('Supply one explicit device serial, not a placeholder or shell expression')
        self.adb, self.serial = str(adb), serial

    def __call__(self, arguments):
        return bounded_run([self.adb, '-s', self.serial, *arguments])


def collect(reader):
    """Transport injection permits complete tests with no real ADB/device calls."""
    records = []
    def read(name, arguments, binary=False):
        result = reader(arguments)
        ok = result.code == 0 and not result.truncated and not result.timed_out
        record = {'name': name, 'available': ok, 'exit_code': result.code,
                  'truncated': result.truncated, 'timed_out': result.timed_out}
        if ok:
            record['hex' if binary else 'text'] = result.stdout.hex() if binary else result.stdout.decode('utf-8', errors='replace').strip()
        # Do not retain arbitrary stderr (which can include a hardware serial).
        records.append(record)
        return result.stdout if ok else None
    identity = {}
    for key in PROPERTIES[:3]:
        value = read(key, ['shell', 'getprop', key])
        identity[key] = value.decode('utf-8', errors='replace').strip() if value else ''
    if identity['ro.product.manufacturer'].lower() != 'amazon' or not (
            identity['ro.product.model'].upper() == 'KFDOWI' or identity['ro.product.device'].lower() == 'douglas'):
        raise ValueError('Device identity is unavailable or not Amazon douglas/KFDOWI; stopping before further reads')
    for key in PROPERTIES[3:]:
        read(key, ['shell', 'getprop', key])
    for flag in ['-r', '-m']:
        read('uname ' + flag, ['shell', 'uname', flag])
    for name in PROC_FILES:
        read('/proc/' + name, ['shell', 'cat', '/proc/' + name])
    result = reader(['shell', 'cat', '/proc/cmdline'])
    if result.code == 0 and not result.truncated and not result.timed_out:
        filtered = {}
        for token in result.stdout.decode('utf-8', errors='replace').split():
            key, separator, value = token.partition('=')
            if separator and key in CMDLINE_KEYS:
                filtered.setdefault(key, []).append(value)
        records.append({'name': '/proc/cmdline', 'available': True, 'allowed_fields_only': filtered})
    else:
        records.append({'name': '/proc/cmdline', 'available': False})
    # Read individual DT properties, never a full bootargs/serial-containing blob.
    for name in ['model', 'compatible', 'version', '#address-cells', '#size-cells']:
        read('/proc/device-tree/' + name, ['exec-out', 'cat', '/proc/device-tree/' + name], binary=True)
    listing = read('DT root node names', ['shell', 'ls', '/proc/device-tree'])
    if listing:
        nodes = sorted({node for node in listing.decode('utf-8', errors='replace').split() if re.fullmatch(r'memory(?:@[0-9a-fA-F]+)?', node)})
        records.append({'name': 'DT memory node selection', 'observed_nodes': len(nodes), 'collected_nodes': nodes[:8], 'limited': len(nodes) > 8})
        for node in nodes[:8]:
            for prop in ['reg', 'orig_dram_info', 'mblock_info']:
                path = '/proc/device-tree/' + node + '/' + prop
                read(path, ['exec-out', 'cat', path], binary=True)
    return {'scope': 'Read-only stock metadata; no raw partitions, root, reboot, mounts or setting writes',
            'generated_utc': datetime.now(timezone.utc).isoformat(), 'identity': identity,
            'hardware_serial_recorded': False, 'records': records,
            'limitations': ['Missing/permission-denied properties remain unavailable; no privilege escalation.',
                           'Driver/firmware/boot compatibility is not validated by this collection.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adb', type=Path, required=True, help='Path to the installed official adb executable')
    parser.add_argument('--serial', required=True, help='Explicit serial from your local adb devices display; not saved in report')
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 'out/stock-facts')
    args = parser.parse_args()
    try:
        report = collect(ADBReader(args.adb, args.serial))
    except (OSError, ValueError) as error:
        parser.exit(2, f'Collection stopped: {error}\n')
    target = args.output / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    target.mkdir(parents=True, exist_ok=False)
    path = target / 'report.json'
    path.write_text(json.dumps(report, indent=2) + '\n')
    print(f'Collected read-only metadata in {path}; review before sharing. No hardware serial saved.')


if __name__ == '__main__':
    main()
