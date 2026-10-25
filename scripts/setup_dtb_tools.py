#!/usr/bin/env python3
"""Build pinned dtc/fdtget inside work/. Network access requires --download."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from urllib.parse import urlsplit

from ci import ROOT, require


def fetch(item, cache, download):
    require(Path(item['filename']).name == item['filename'], 'Unsafe tool filename')
    path = cache/item['filename']
    if not path.exists():
        require(download, f'Missing {path}; inspect lock and explicitly pass --download')
        parsed = urlsplit(item['url'])
        require(parsed.scheme == 'https' and parsed.netloc in {'www.kernel.org','files.pythonhosted.org'}, 'Unexpected tool source')
        with urllib.request.urlopen(item['url'], timeout=60) as response:
            data = response.read(item['bytes']+1)
        require(len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256'], 'Downloaded tool content mismatch')
        path.write_bytes(data)
    data = path.read_bytes()
    require(len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256'], f'Tool archive changed: {path}')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download', action='store_true')
    args = parser.parse_args()
    lock = json.loads((ROOT/'projects/firetabs-android/kernel/dtb/tools.lock.json').read_text())
    key = platform.system()+'-'+platform.machine()
    require(key in lock['platform_wheels'], f'No pinned compiler bootstrap for {key}')
    items = [lock['source'], *lock['common_wheels'], *lock['platform_wheels'][key]]
    size = sum(x['bytes'] for x in items)
    require(size <= lock['max_download_bytes'], 'Tool bootstrap exceeds recorded budget')
    print(f'Pinned dtc bootstrap: {key}, {size} archive bytes; download enabled={args.download}', flush=True)
    work = ROOT/'work/dtb-tool'
    cache = work/'downloads'
    cache.mkdir(parents=True, exist_ok=True)
    paths = [fetch(x, cache, args.download) for x in items]
    venv = work/'venv'
    if not (venv/'bin/python').exists():
        subprocess.run([sys.executable,'-m','venv',str(venv)],check=True)
    python = str(venv/'bin/python')
    subprocess.run([python,'-m','pip','--isolated','install','--disable-pip-version-check','--no-cache-dir','--no-index','--no-deps',*[str(x) for x in paths[1:]]],check=True)
    source = work/('dtc-'+lock['dtc_version'])
    if not source.exists():
        with tarfile.open(paths[0]) as archive:
            archive.extractall(work, filter='data')
    env = {**os.environ, 'PATH':str(venv/'bin')+os.pathsep+os.environ.get('PATH',''), 'GIT_CEILING_DIRECTORIES':str(work)}
    for tool in ['cc','bison','flex']:
        require(shutil.which(tool, path=env['PATH']) is not None, f'Required host tool not found: {tool}')
    build = work/'build'
    meson = str(venv/'bin/meson')
    cmd = [meson,'setup']
    if (build/'build.ninja').exists():
        cmd += ['--reconfigure']
    cmd += [str(build),str(source),'-Dpython=disabled','-Dyaml=disabled','-Dtests=false','-Dvalgrind=disabled','--backend=ninja']
    subprocess.run(cmd,env=env,check=True)
    subprocess.run([meson,'compile','-C',str(build),'dtc','fdtget'],env=env,check=True)
    version = subprocess.check_output([str(build/'dtc'),'--version'],text=True).strip()
    require(version == 'Version: DTC '+lock['dtc_version'], 'Unexpected dtc version')
    print(version)
    print('Host tools built under work/ only; no kernel, image or device operation.')


if __name__ == '__main__':
    main()
