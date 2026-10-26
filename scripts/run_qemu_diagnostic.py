#!/usr/bin/env python3
"""Bounded generic ARM64 VM test; never uses a tablet or douglas DT/loader."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import selectors
import struct
import subprocess
import time

from diagnostic_config import check, policy
from measure_arm64_image import measure, bounded_file, MAX_IMAGE

MARKERS = [b'FIRETABS_DIAGNOSTIC_INIT_V1', b'PROC_MOUNT_OK', b'SYSFS_MOUNT_OK',
           b'FILE /proc/version', b'FILE /proc/meminfo', b'FILE /proc/iomem',
           b'FILE /proc/uptime', b'MemTotal:', b'FIRETABS_DIAGNOSTIC_IDLE']
FATAL = [b'Kernel panic - not syncing', b'Internal error: Oops', b'\nUNAVAILABLE\n', b'\nREAD_ERROR\n']
LOG_LIMIT = 2*1024*1024



def cpu_contract_report(data, require_primary=False):
    checked = data.replace(b'\r\n', b'\n')
    begin, end = b'FIRETABS_CPU_CONTRACT_V1\n', b'FIRETABS_CPU_CONTRACT_END\n'
    if end not in checked:
        return None
    if checked.count(begin) != 1 or checked.count(end) != 1:
        raise ValueError('Duplicated/missing sanitized CPU contract block')
    block = checked.split(begin, 1)[1].split(end, 1)[0]
    allowed = {'LIMIT_NR_CPUS': {'missing', 'valid', 'conflict', 'duplicate', 'malformed', 'unavailable'},
               'LIMIT_MAXCPUS': {'missing', 'valid', 'conflict', 'duplicate', 'malformed', 'unavailable'},
               'ONLINE_BOOT_CPU_ONLY': {'yes', 'no'},
               'PSCI_DT_STATUS': {'disabled', 'enabled', 'unavailable', 'unrecognized'}}
    values = {}
    for raw in block.splitlines():
        try:
            key, value = raw.decode('ascii').split('=', 1)
        except (ValueError, UnicodeError):
            raise ValueError('Malformed sanitized CPU contract') from None
        if key in values or key not in {*allowed, 'ONLINE_CPUS'}:
            raise ValueError('Unexpected sanitized CPU contract field')
        if key == 'ONLINE_CPUS':
            if value != 'unavailable' and (not re.fullmatch(r'[1-9][0-9]{0,3}', value) or int(value) > 4096):
                raise ValueError('Invalid sanitized CPU count')
        elif value not in allowed[key]:
            raise ValueError('Invalid sanitized CPU verdict')
        values[key] = value
    if set(values) != {*allowed, 'ONLINE_CPUS'}:
        raise ValueError('Incomplete sanitized CPU contract')
    primary = (values['LIMIT_NR_CPUS'] == values['LIMIT_MAXCPUS'] == 'valid' and
               values['ONLINE_CPUS'] == '1' and values['ONLINE_BOOT_CPU_ONLY'] == 'yes' and
               values['PSCI_DT_STATUS'] == 'disabled')
    if require_primary and not primary:
        raise ValueError('Primary-only runtime observations do not meet contract')
    return {'verdicts': values, 'primary_only_contract_observed': primary,
            'scope': 'Separate sanitized observations; not loader/recovery or tablet hardware qualification',
            'douglas_boot_qualified': False}


def transcript_ready(data):
    # Serial consoles may translate LF to CRLF. Preserve raw log hashes, but
    # normalize line endings when interpreting exact diagnostic error lines.
    checked = data.replace(b'\r\n', b'\n')
    if any(marker in checked for marker in FATAL):
        raise ValueError('Guest kernel panic/Oops or diagnostic read failure')
    return all(marker in data for marker in MARKERS) and data.count(b'END_FILE') >= 4 and cpu_contract_report(data) is not None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kernel', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--initramfs', type=Path, required=True)
    parser.add_argument('--qemu', default='qemu-system-aarch64')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Fresh output required')
    resolved = check(args.config.read_text(), policy())
    if 'CONFIG_SERIAL_AMBA_PL011_CONSOLE=y' not in args.config.read_text().splitlines():
        parser.error('Generic virt PL011 console must be built in')
    kernel = bounded_file(args.kernel, MAX_IMAGE)
    sizing = measure(kernel, bounded_file(args.kernel.with_name('Image.gz'), MAX_IMAGE+65536))
    if len(kernel) < 64 or kernel[56:60] != b'ARMd':
        parser.error('Expected raw AArch64 Image')
    command = [args.qemu, '-machine', 'virt-8.2,gic-version=3', '-accel', 'tcg',
               '-cpu', 'cortex-a53', '-smp', '1', '-m', '512M', '-nodefaults',
               '-display', 'none', '-monitor', 'none', '-serial', 'stdio', '-nic', 'none',
               '-no-reboot', '-kernel', str(args.kernel), '-initrd', str(args.initramfs),
               '-append', 'console=ttyAMA0 earlycon rdinit=/init panic=-1']
    args.output.mkdir(parents=True)
    report = {'scope': 'Generic QEMU virt userspace execution only; douglas boot/hardware untested',
              'qemu_version': subprocess.check_output([args.qemu, '--version'], text=True).splitlines()[0],
              'command': command, 'machine': 'virt-8.2', 'cpu': 'cortex-a53', 'guest_memory_mib': 512,
              'timeout_seconds': 120, 'idle_observation_seconds': 5, 'console_limit': LOG_LIMIT,
              'config_sha256': hashlib.sha256(args.config.read_bytes()).hexdigest(),
              'kernel_sha256': hashlib.sha256(kernel).hexdigest(),
              'image_measurements': sizing,
              'initramfs_sha256': hashlib.sha256(args.initramfs.read_bytes()).hexdigest(),
              'tester_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'arm64_header': {'text_offset': struct.unpack_from('<Q', kernel, 8)[0],
                               'image_size': struct.unpack_from('<Q', kernel, 16)[0],
                               'flags': struct.unpack_from('<Q', kernel, 24)[0], 'first64_hex': kernel[:64].hex()},
              'resolved_policy_passed': resolved['passed'], 'passed': False,
              'douglas_boot_tested': False, 'hardware_tested': False, 'firmware_packed': False}
    data, began, ready = bytearray(), time.monotonic(), None
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            while time.monotonic()-began < 120:
                if process.poll() is not None:
                    raise ValueError('Guest exited before controlled stop')
                for key, _ in selector.select(timeout=0.2):
                    block = os.read(key.fd, min(65536, LOG_LIMIT-len(data)+1))
                    if not block:
                        raise ValueError('Guest console closed')
                    data.extend(block)
                    if len(data) > LOG_LIMIT:
                        raise ValueError('Console limit exceeded')
                if transcript_ready(data):
                    if ready is None:
                        ready = time.monotonic()
                    if time.monotonic()-ready >= 5:
                        report['passed'] = True
                        break
            if not report['passed']:
                raise ValueError('Required markers/idle observation timed out')
    except (ValueError, OSError) as error:
        report['failure'] = str(error)
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        raw = bytes(data[:LOG_LIMIT])
        (args.output/'console.log').write_bytes(raw)
        report['cpu_contract'] = cpu_contract_report(raw) if report['passed'] else None
        report.update(console_bytes=len(raw), console_sha256=hashlib.sha256(raw).hexdigest(),
                      host_stopped_qemu=True, required_markers=[x.decode() for x in MARKERS],
                      elapsed_seconds=round(time.monotonic()-began, 2))
        root = str(Path(__file__).resolve().parents[1])
        report['command'] = [x.replace(root, '<workspace>') for x in report['command']]
        (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(raw.decode('utf-8', errors='replace'))
        print(json.dumps(report, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
