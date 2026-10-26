#!/usr/bin/env python3
"""Inventory only known static argument sources; never infer runtime completeness."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from inspect_loader_layout import checked_file, lk_layout
from inspect_boot_image import inspect, MAX_INPUT_BYTES
from verify_offline_escrow import regular_file

ROOT=Path(__file__).resolve().parents[1]
BOOT_SHA='8982fa50193acc764be69ee51027ee92e83614cee4b8235b07439d1f9e2db363'


def keys(text):
    if len(text)>16384 or any(ord(c)<32 or ord(c)>126 for c in text):
        raise ValueError('Unexpected bounded static command line')
    result=[]
    for token in text.split():
        key=token.split('=',1)[0]
        if not re.fullmatch('[A-Za-z0-9_.-]+',key):
            raise ValueError('Malformed argument key')
        result.append(key)
    return result


def header_arguments(raw):
    inspect(raw)
    parts=[]
    for start,end in [(64,576),(608,1632)]:
        field=raw[start:end]
        if b'\0' not in field:
            raise ValueError('Unterminated header argument field')
        parts.append(field.split(b'\0',1)[0].decode('ascii'))
    return ' '.join(parts).strip()


def main():
    with regular_file(ROOT/'out/stock-ota-douglas-659664620/boot.img') as stream:
        boot=stream.read(MAX_INPUT_BYTES+1)
    if len(boot)>MAX_INPUT_BYTES or hashlib.sha256(boot).hexdigest()!=BOOT_SHA:
        raise ValueError('Stock boot image identity mismatch')
    lk_report=json.loads((ROOT/'evidence/lk-bootargs/report.json').read_text())
    lk=checked_file(ROOT/'out/ota-loader-inspection-659664620/lk.bin',lk_report['lk_sha256'])
    payload=lk[lk_layout(lk)['payload_offset']:]
    ref=lk_report['facts']['initial_file_backed_command_buffer']
    start=int(ref['linked_address'],16)-0x4bd00000
    initial=payload[start:start+ref['bytes_before_nul']+1]
    if not initial.endswith(b'\0') or hashlib.sha256(initial[:-1]).hexdigest()!=ref['sha256_before_nul']:
        raise ValueError('Static LK argument buffer changed')
    sources=[{'source':'stock boot header','keys':keys(header_arguments(boot)),
              'source_sha256':BOOT_SHA},
             {'source':'initial LK buffer','keys':keys(initial[:-1].decode('ascii')),
              'source_sha256':ref['sha256_before_nul']}]
    stock=json.loads((ROOT/'evidence/stock-dtb/candidate-report.json').read_text())
    # DT identities are independently pinned by the previously published stock inspection.
    for index in (0,1):
        dtb=ROOT/f'out/stock-dtb-659664620/dtb-{index}.dtb'
        digest=hashlib.sha256(dtb.read_bytes()).hexdigest()
        if digest != next(x['sha256'] for x in stock['dtbs'] if x['index']==index):
            raise ValueError('Stock DT identity absent from inspection report')
        text=subprocess.check_output([str(ROOT/'work/dtb-tool/build/fdtget'),'-ts',str(dtb),
                                      '/chosen','bootargs'],text=True).rstrip('\n')
        sources.append({'source':f'stock appended DT {index}','keys':keys(text),'source_sha256':digest})
    runtime=json.loads((ROOT/'evidence/stock-facts/runtime-contract.json').read_text())
    print(json.dumps({'scope':'Known static sources only; no argument values published',
        'sources':sources,'union_keys':sorted({key for source in sources for key in source['keys']}),
        'stock_runtime_cmdline_available':'/proc/cmdline' not in runtime['unavailable'],
        'all_loader_mutations_audited':False,'discarded_arguments_fully_qualified':False,
        'device_profile_build_recommended':False,'physical_test_ready':False,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))


if __name__=='__main__':
    main()
