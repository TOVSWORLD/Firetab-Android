#!/usr/bin/env python3
"""Apply the locked MT8163 PWM controller variant to a disposable pinned ACK tree."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import shutil
import tempfile
ROOT=Path(__file__).resolve().parents[1]
PORT=ROOT/'projects/firetabs-android/kernel/pwm-port'


def apply(source,actual_revision):
    lock=json.loads((PORT/'inputs.json').read_text())
    if actual_revision!=lock['ack_commit']:raise ValueError('Wrong ACK revision')
    parts=lock['files']
    checks=[(PORT/lock['patch'],lock['patch_sha256'])]
    checks += [(source/p['target'],p['original_sha256']) for p in parts if p['original_sha256'] is not None]
    for part in parts:
        if part['original_sha256'] is None and (source/part['target']).exists():raise ValueError('New PWM target already exists')
    checks += [(ROOT/p['source'],p['original_sha256'] or p['patched_sha256']) for p in parts]
    checks += [(path,p['sha256']) for p in lock['build_inputs'] for path in [source/p['target'],ROOT/p['source']]]
    checks += [(PORT/'variant-definition.json',lock['definition_sha256'])]
    for path,expected in checks:
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('PWM input drift: '+str(path))
    patches=[str(PORT/lock['patch'])]
    targets=[p['target'] for p in parts]
    numstat=subprocess.check_output(['git','-C',str(source),'apply','--numstat',*patches],text=True)
    if sorted(line.split('\t')[2] for line in numstat.splitlines())!=sorted(targets):
        raise ValueError('PWM patch target set drift')
    # Verify every expected output in a disposable tree before any real source write.
    with tempfile.TemporaryDirectory(prefix='pwm-preflight-') as temporary:
        shadow=Path(temporary)
        for p in parts:
            dest=shadow/p['target'];dest.parent.mkdir(parents=True,exist_ok=True)
            if p['original_sha256'] is not None:shutil.copyfile(source/p['target'],dest)
        subprocess.run(['git','-C',str(shadow),'apply',*patches],check=True)
        for p in parts:
            if hashlib.sha256((shadow/p['target']).read_bytes()).hexdigest()!=p['patched_sha256']:
                raise ValueError('PWM patched output drift before source writes: '+p['target'])
    subprocess.run(['git','-C',str(source),'apply','--check',*patches],check=True)
    subprocess.run(['git','-C',str(source),'apply',*patches],check=True)
    return {'scope':'MT8163 PWM controller source applied; build/runtime separate',
            'targets':targets,'all_outputs_preflighted':True,'runtime_qualified':False}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);a=p.parse_args();source=a.source.resolve()
    revision=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    print(json.dumps(apply(source,revision),indent=2))

if __name__=='__main__':main()
