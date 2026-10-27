#!/usr/bin/env python3
"""Compile/link owned callable agent only. No execution or transport binding."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from prepare_stage1_host_image import prepare_host_image

ROOT = Path(__file__).resolve().parents[1]


def build_variant(entry_source):
    clang = shutil.which('clang-18') or shutil.which('clang')
    ld = shutil.which('ld.lld-18') or shutil.which('ld.lld')
    if not clang or not ld: raise RuntimeError('Preinstalled clang/LLD required')
    output = ROOT/('out/owned-agent-ci-'+entry_source)
    if output.exists() or shutil.disk_usage(ROOT).free < 1024**3:
        raise ValueError('Fresh output and 1GiB free disk required')
    output.mkdir(parents=True)
    sources = [ROOT/'diagnostic/protocol'/name for name in [entry_source+'.S','agent.c','dispatcher.c']]
    sources += [ROOT/'diagnostic/logging'/name for name in ['uart.c','marker.c','logged_agent.c']]
    objects = []
    for source in sources:
        obj=output/(source.name+'.o')
        command=[clang,'--target=arm-none-eabi','-mcpu=cortex-a9','-mthumb','-c',str(source),'-o',str(obj)]
        if source.suffix=='.c':
            command+=['-std=c11','-Os','-ffreestanding','-fno-builtin','-fPIE','-fno-unwind-tables',
                      '-fno-asynchronous-unwind-tables','-fstack-usage','-Wall','-Wextra','-Werror']
        subprocess.run(command,check=True,capture_output=True,timeout=30)
        objects.append(obj)
    frames = {}
    for source in sources:
        if source.suffix != '.c': continue
        for line in (output/(source.name+'.su')).read_text().splitlines():
            location, size, kind = line.split('\t')
            name = location.rsplit(':', 1)[-1]
            if kind != 'static' or name in frames: raise ValueError('Unbounded or duplicate stack frame')
            frames[name] = int(size)
    if not {'diagnostic_agent_run', 'diagnostic_dispatch'} <= frames.keys():
        raise ValueError('Missing owned stack frames')
    owned_stack = 16 + sum(frames.values())
    if owned_stack >= 2048: raise ValueError('Owned frames exhaust private stack')
    script=ROOT/'diagnostic/protocol/agent.ld';elf=output/'agent.elf'
    subprocess.run([ld,'-m','armelf','--build-id=none','-T',str(script),*[str(o) for o in objects],
                    '-o',str(elf)],check=True,capture_output=True,timeout=30)
    _,image=prepare_host_image(elf.read_bytes())
    report=dict(entry_variant=entry_source, embedded_callbacks_bound=False, source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sources+[script,ROOT/'diagnostic/protocol/agent.h',ROOT/'diagnostic/protocol/dispatcher.h',ROOT/'diagnostic/logging/uart.h',ROOT/'diagnostic/logging/marker.h',ROOT/'diagnostic/logging/logged_agent.h']},
                compiler=subprocess.check_output([clang,'--version'],text=True,timeout=10).splitlines()[0],
                linker=subprocess.check_output([ld,'--version'],text=True,timeout=10).splitlines()[0],
                elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),host_image=image,
                stack_bytes=2048, compiler_static_frames=frames,
                owned_frame_sum_with_wrapper_bytes=owned_stack,
                remaining_before_callbacks_interrupts_bytes=2048-owned_stack,
                maximum_callback_stack_usage_verified=False,
                caller_return_verified=False,transport_bound=False,firmware_executed=False,physical_test_ready=False)
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    print(json.dumps({'variants':[build_variant(n) for n in ['entry','bridge']]},indent=2))
