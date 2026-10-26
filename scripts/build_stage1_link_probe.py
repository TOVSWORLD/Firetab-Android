#!/usr/bin/env python3
"""Small pinned-source compile/link only; no firmware execution or dependency installs."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import urllib.request
from inspect_stage1_elf import inspect_elf
from prepare_stage1_host_image import prepare_host_image
ROOT=Path(__file__).resolve().parents[1]


def main():
    inputs=[]
    for record in ['evidence/payload-source-provenance/source-index.json','evidence/stage1-link-feasibility/report.json']:
        for item in json.loads((ROOT/record).read_text())['files']:
            if item['path'] in ['src/stage1/generic/generic_stage1.c','src/stage1/common/start.S','src/stage1/common/generic.ld']:
                inputs.append(item)
    if len(inputs)!=3 or sum(x['bytes'] for x in inputs)>16384:raise ValueError('Pinned source budget differs')
    clang=shutil.which('clang-18') or shutil.which('clang')
    linker=shutil.which('ld.lld-18') or shutil.which('ld.lld')
    report={'source_revision':'7cb40e727727dfe3faa065eefb29b16ed29bbdf1',
            'source_bytes':sum(x['bytes'] for x in inputs),'compiled':False,'linked':False,
            'firmware_executed':False,'physical_test_ready':False}
    if not clang or not linker:
        report['failure']='preinstalled_clang_or_elf_linker_missing';print(json.dumps(report,indent=2));return 1
    output=ROOT/'out/stage1-ci-link-probe'
    if output.exists():raise ValueError('Fresh output directory required')
    if shutil.disk_usage(ROOT).free<1024**3:raise ValueError('1GiB free disk required')
    output.mkdir(parents=True)
    sources={}
    for item in inputs:
        if not item['url'].startswith('https://raw.githubusercontent.com/bkerler/mtkclient/'+report['source_revision']+'/'):
            raise ValueError('Unreviewed source origin')
        with urllib.request.urlopen(item['url'],timeout=15) as stream:data=stream.read(16385)
        if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:
            raise ValueError('Source identity mismatch')
        path=output/Path(item['path']).name;path.write_bytes(data);sources[path.name]=path
    report['compiler_version']=subprocess.check_output([clang,'--version'],text=True,timeout=10).splitlines()[0]
    report['linker_version']=subprocess.check_output([linker,'--version'],text=True,timeout=10).splitlines()[0]
    objects=[];warnings=0
    for source in ['generic_stage1.c','start.S']:
        obj=output/(source+'.o');command=[clang,'--target=arm-none-eabi','-c',str(sources[source]),'-o',str(obj)]
        if source.endswith('.c'):
            command+=['-std=gnu99','-Os','-mthumb','-mcpu=cortex-a9','-ffreestanding',
                      '-fno-builtin-printf','-fno-strict-aliasing','-fno-builtin-memcpy','-fPIE','-mno-unaligned-access','-DNDEBUG']
        run=subprocess.run(command,capture_output=True,text=True,timeout=60)
        warnings+=run.stderr.count('warning:')
        if run.returncode:
            report.update(failure='object_compile',exit_code=run.returncode,diagnostic_sha256=hashlib.sha256(run.stderr.encode()).hexdigest())
            print(json.dumps(report,indent=2));return 1
        objects.append(obj)
    report['compiled']=True;report['warning_count']=warnings
    elf=output/'stage1-probe.elf'
    command=[linker,'-m','armelf','--build-id=none','-T',str(sources['generic.ld']),*[str(x) for x in objects],'-o',str(elf)]
    run=subprocess.run(command,capture_output=True,text=True,timeout=60)
    if run.returncode:
        report.update(failure='elf_link',exit_code=run.returncode,diagnostic_sha256=hashlib.sha256(run.stderr.encode()).hexdigest())
        print(json.dumps(report,indent=2));return 1
    data=elf.read_bytes()
    if len(data)>1024*1024 or data[:6]!=b'\x7fELF\x01\x01' or struct.unpack_from('<HH',data,16)!=(2,40):
        raise ValueError('Expected bounded ARM executable ELF')
    report['elf_layout'] = inspect_elf(data)
    _, report['host_image'] = prepare_host_image(data)
    report.update(linked=True,elf_bytes=len(data),elf_sha256=hashlib.sha256(data).hexdigest(),
        entry=struct.unpack_from('<I',data,24)[0],source_sha256={x['path']:x['sha256'] for x in inputs},
        shipped_binary_equivalence_verified=False,linux_handoff_verified=False)
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
