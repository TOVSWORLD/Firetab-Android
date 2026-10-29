#!/usr/bin/env python3
"""Apply the locked MT8163 USB2 port0 variant to a disposable pinned ACK tree."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
PORT=ROOT/'projects/firetabs-android/kernel/usb-port'


def apply(source,actual_revision):
    lock=json.loads((PORT/'inputs.json').read_text())
    if actual_revision!=lock['ack_commit']:raise ValueError('Wrong ACK revision')
    checks=[(PORT/lock['patch'],lock['patch_sha256']),
            (source/lock['target'],lock['original_sha256']),
            (source/'drivers/phy/mediatek/phy-mtk-io.h',lock['helper_sha256']),
            (PORT/'variant-definition.json',lock['definition_sha256'])]
    for path,expected in checks:
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('USB input drift: '+str(path))
    patch=PORT/lock['patch']
    subprocess.run(['git','-C',str(source),'apply','--check',str(patch)],check=True)
    subprocess.run(['git','-C',str(source),'apply',str(patch)],check=True)
    if hashlib.sha256((source/lock['target']).read_bytes()).hexdigest()!=lock['patched_sha256']:raise ValueError('USB patched output drift')
    return {'scope':'MT8163 USB2 port0 source applied; build/runtime separate','runtime_qualified':False}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);a=p.parse_args();source=a.source.resolve()
    revision=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    print(json.dumps(apply(source,revision),indent=2))

if __name__=='__main__':main()
