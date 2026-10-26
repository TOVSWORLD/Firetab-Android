#!/usr/bin/env python3
"""Compile/link owned entry experiment; never execute or upload the result."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from prepare_stage1_host_image import prepare_host_image

ROOT = Path(__file__).resolve().parents[1]


def main():
    clang = shutil.which('clang-18') or shutil.which('clang')
    linker = shutil.which('ld.lld-18') or shutil.which('ld.lld')
    if not clang or not linker:
        raise RuntimeError('Preinstalled clang and LLD required; no automatic installs')
    output = ROOT / 'out/owned-entry-ci'
    if output.exists() or shutil.disk_usage(ROOT).free < 1024**3:
        raise ValueError('Fresh output and 1GiB free disk required')
    output.mkdir(parents=True)
    source = ROOT / 'diagnostic/entry/entry.S'
    script = ROOT / 'diagnostic/entry/entry.ld'
    obj = output / 'entry.o'
    elf = output / 'entry.elf'
    commands = [[clang, '--target=arm-none-eabi', '-mcpu=cortex-a9', '-c', str(source), '-o', str(obj)],
                [linker, '-m', 'armelf', '--build-id=none', '-T', str(script), str(obj), '-o', str(elf)]]
    for command in commands:
        subprocess.run(command, check=True, capture_output=True, timeout=30)
    _, image = prepare_host_image(elf.read_bytes())
    report = dict(sources={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [source, script]},
                  compiler=subprocess.check_output([clang, '--version'], text=True, timeout=10).splitlines()[0],
                  linker=subprocess.check_output([linker, '--version'], text=True, timeout=10).splitlines()[0],
                  elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(), host_image=image,
                  stack_bytes=1024, marker_value='0x46544b31',
                  marker_observed_at_runtime=False, firmware_executed=False,
                  stock_return_implemented=False, log_transport_implemented=False, physical_test_ready=False)
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
