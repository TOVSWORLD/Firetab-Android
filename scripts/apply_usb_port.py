#!/usr/bin/env python3
"""Apply the locked MT8163 USB2 port0 variant to a disposable pinned ACK tree."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import shutil
import tempfile
ROOT=Path(__file__).resolve().parents[1]
PORT=ROOT/'projects/firetabs-android/kernel/usb-port'


def apply(source,actual_revision):
    lock=json.loads((PORT/'inputs.json').read_text())
    if actual_revision!=lock['ack_commit']:raise ValueError('Wrong ACK revision')
    parts=[lock]+lock.get('additional_patches',[])
    checks=[(PORT/p['patch'],p['patch_sha256']) for p in parts]
    checks += [(source/p['target'],p['original_sha256']) for p in parts]
    checks += [
            (source/'drivers/phy/mediatek/phy-mtk-io.h',lock['helper_sha256']),
            (PORT/'variant-definition.json',lock['definition_sha256'])]
    for path,expected in checks:
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('USB input drift: '+str(path))
    patches=[str(PORT/p['patch']) for p in parts]
    targets=[p['target'] for p in parts]
    numstat=subprocess.check_output(['git','-C',str(source),'apply','--numstat',*patches],text=True)
    if sorted(line.split('\t')[2] for line in numstat.splitlines())!=sorted(targets):
        raise ValueError('USB patch target set drift')
    # Verify every expected output in a disposable tree before any real source write.
    with tempfile.TemporaryDirectory(prefix='usb-preflight-') as temporary:
        shadow=Path(temporary)
        for p in parts:
            dest=shadow/p['target'];dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source/p['target'],dest)
        subprocess.run(['git','-C',str(shadow),'apply',*patches],check=True)
        for p in parts:
            if hashlib.sha256((shadow/p['target']).read_bytes()).hexdigest()!=p['patched_sha256']:
                raise ValueError('USB patched output drift before source writes: '+p['target'])
    subprocess.run(['git','-C',str(source),'apply','--check',*patches],check=True)
    subprocess.run(['git','-C',str(source),'apply',*patches],check=True)
    return {'scope':'MT8163 T-PHY and scoped MUSB source applied; build/runtime separate',
            'targets':targets,'all_outputs_preflighted':True,'runtime_qualified':False}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);a=p.parse_args();source=a.source.resolve()
    revision=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    print(json.dumps(apply(source,revision),indent=2))

if __name__=='__main__':main()
