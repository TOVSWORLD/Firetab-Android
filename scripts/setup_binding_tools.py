#!/usr/bin/env python3
"""Install hash-locked schema controls in existing work/ venv; explicit bounded downloads only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from setup_dtb_tools import fetch
ROOT=Path(__file__).resolve().parents[1]
LOCK=ROOT/'projects/firetabs-android/kernel/dtb/schema-tools.lock.json'


def select_items(lock,key,version):
    if key!=lock['platform'] or version!=lock['python']:raise ValueError('No locked schema bootstrap for this platform/Python')
    items=lock['items']
    if sum(x['bytes'] for x in items)>lock['max_download_bytes']:raise ValueError('Schema tool budget exceeded')
    for item in items:
        if Path(item['filename']).name!=item['filename'] or type(item['bytes']) is not int or item['bytes']<=0:
            raise ValueError('Unsafe schema artifact metadata')
    versions={x['name']:x['version'] for x in items}
    if versions.get('dtschema')!=lock['dtschema_version'] or versions.get('swig')!='4.4.1' or versions.get('pylibfdt')!='1.7.2.post2':
        raise ValueError('Schema/build requirement version mismatch')
    return items


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--download',action='store_true');args=p.parse_args()
    lock=json.loads(LOCK.read_text());version=f'{sys.version_info.major}.{sys.version_info.minor}'
    items=select_items(lock,platform.system()+'-'+platform.machine(),version)
    binding=json.loads((ROOT/'projects/firetabs-android/kernel/dtb/bindings.lock.json').read_text())
    if lock['dtschema_version']!=binding['dtschema_version']:raise ValueError('Binding schema version differs from locked tools')
    work=ROOT/'work/dtb-tool';python=work/'venv/bin/python3'
    if not python.exists():raise ValueError('Run pinned DTC setup first')
    actual=subprocess.check_output([str(python),'-c','import sys;print(f"{sys.version_info.major}.{sys.version_info.minor}")'],text=True).strip()
    if actual!=version:raise ValueError('Existing venv Python mismatch')
    cache=work/'downloads';cache.mkdir(parents=True,exist_ok=True)
    paths=[fetch(item,cache,args.download) for item in items]
    print('Pinned schema tool bootstrap:',len(items),'artifacts,',sum(x['bytes'] for x in items),'bytes',flush=True)
    env={**os.environ,'PATH':str(work/'venv/bin')+os.pathsep+os.environ.get('PATH',''),
         'PIP_NO_INDEX':'1','SETUPTOOLS_SCM_PRETEND_VERSION_FOR_PYLIBFDT':'1.7.2.post2'}
    common=[str(python),'-m','pip','--isolated','install','--disable-pip-version-check','--no-cache-dir',
            '--no-index','--no-deps','--force-reinstall']
    subprocess.run(common+[str(path) for path in paths if path.suffix=='.whl'],env=env,check=True)
    swig_version=subprocess.check_output([str(work/'venv/bin/swig'),'-version'],text=True,env=env)
    if 'SWIG Version 4.4.1' not in swig_version:raise ValueError('Pinned SWIG executable version mismatch')
    # Build the actual extension with installed pinned build tools; never resolve build dependencies online.
    subprocess.run(common+['--no-build-isolation']+[str(path) for path in paths if path.suffix!='.whl'],env=env,check=True)
    subprocess.run([str(python),'-m','pip','--isolated','check'],env=env,check=True)
    probe='import dtschema,libfdt;from dtschema import DTValidator;import importlib.metadata as m,json;print(json.dumps({n:m.version(n) for n in '+repr([x['name'] for x in items])+'}))'
    versions=json.loads(subprocess.check_output([str(python),'-c',probe],text=True,env=env))
    for item in items:
        if versions[item['name']]!=item['version']:raise ValueError('Installed schema tool version drift')
    report={'scope':'Actual pinned schema-control dependencies only; no kernel/device operation',
            'platform':lock['platform'],'python':version,'versions':versions,'swig_version':'4.4.1',
            'lock_sha256':hashlib.sha256(LOCK.read_bytes()).hexdigest(),'download_bytes':sum(x['bytes'] for x in items)}
    (work/'schema-tools-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
