#!/usr/bin/env python3
"""Apply only the locked MT8163 IOMMU/SMI additions to a disposable ACK checkout."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
PORT=ROOT/'projects/firetabs-android/kernel/iommu-port'


def apply(source,actual_revision):
    lock=json.loads((PORT/'inputs.json').read_text())
    if actual_revision!=lock['ack_commit']:raise ValueError('Wrong ACK revision')
    patch=PORT/lock['patch']
    if hashlib.sha256(patch.read_bytes()).hexdigest()!=lock['patch_sha256']:raise ValueError('Patch hash changed')
    for row in lock['files']:
        for path,expected in [(source/row['target'],row['original_sha256']),
                              (ROOT/row['donor_source'],row['donor_sha256'])]:
            if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('Source input drift: '+str(path))
    subprocess.run(['git','-C',str(source),'apply','--check',str(patch)],check=True)
    subprocess.run(['git','-C',str(source),'apply',str(patch)],check=True)
    for row in lock['files']:
        if hashlib.sha256((source/row['target']).read_bytes()).hexdigest()!=row['patched_sha256']:raise ValueError('Patched output drift')
    return {'scope':'Minimal source additions applied; build/runtime qualification separate','files':len(lock['files']),'runtime_qualified':False}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);args=p.parse_args()
    source=args.source.resolve();revision=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    print(json.dumps(apply(source,revision),indent=2))


if __name__=='__main__':main()
