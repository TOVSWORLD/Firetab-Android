#!/usr/bin/env python3
"""Compile/link owned entry experiment; never execute or upload the result."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from prepare_stage1_host_image import prepare_host_image
from decode_diagnostic_marker import decode_marker, LAYOUTS, MARKER

ROOT = Path(__file__).resolve().parents[1]


def build_variant(name):
    clang = shutil.which('clang-18') or shutil.which('clang')
    linker = shutil.which('ld.lld-18') or shutil.which('ld.lld')
    if not clang or not linker:
        raise RuntimeError('Preinstalled clang and LLD required; no automatic installs')
    output = ROOT / ('out/owned-entry-ci-' + name)
    if output.exists() or shutil.disk_usage(ROOT).free < 1024**3:
        raise ValueError('Fresh output and 1GiB free disk required')
    output.mkdir(parents=True)
    source = ROOT / ('diagnostic/entry/' + name + '.S')
    script = ROOT / 'diagnostic/entry/entry.ld'
    obj = output / 'entry.o'
    elf = output / 'entry.elf'
    commands = [[clang, '--target=arm-none-eabi', '-mcpu=cortex-a9', '-c', str(source), '-o', str(obj)],
                [linker, '-m', 'armelf', '--build-id=none', '-T', str(script), str(obj), '-o', str(elf)]]
    for command in commands:
        subprocess.run(command, check=True, capture_output=True, timeout=30)
    image_bytes, image = prepare_host_image(elf.read_bytes())
    marker_offset, _, _ = LAYOUTS[name]
    synthetic_after = bytearray(image_bytes)
    synthetic_after[marker_offset:marker_offset + 4] = MARKER
    synthetic_decode = decode_marker(image_bytes, image_bytes, bytes(synthetic_after),
        variant=name, expected_image_sha256=image['image_sha256'])
    report = dict(variant=name, synthetic_marker_decode=synthetic_decode, sources={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [source, script]},
                  compiler=subprocess.check_output([clang, '--version'], text=True, timeout=10).splitlines()[0],
                  linker=subprocess.check_output([linker, '--version'], text=True, timeout=10).splitlines()[0],
                  elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(), host_image=image,
                  stack_bytes=1024, marker_value='0x46544b31',
                  marker_observed_at_runtime=False, firmware_executed=False,
                  caller_return_sequence_implemented=(name == 'callable'),
                  caller_return_verified_at_runtime=False, stock_return_implemented=False,
                  log_transport_implemented=False, physical_test_ready=False)
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    print(json.dumps({'variants': [build_variant(name) for name in ['entry', 'callable']]}, indent=2))
