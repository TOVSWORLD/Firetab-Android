#!/usr/bin/env python3
"""Download only patch-touched files at pinned commits; never sync or build Android."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = {
    'bionic': ('android_bionic', 'b67b03356ceb6171bd0cfdb88c3ee9413c476935'),
    'frameworks/base': ('android_frameworks_base', '2f5cf1e4fc1e8b1480d3c27a855f95d6d45429f4'),
    'hardware/interfaces': ('android_hardware_interfaces', '203e87a39c04f30bc1f09f6c2306b701d6b97fe0'),
    'system/core': ('android_system_core', '92420679ffbd50b79d76525085b21278f8497037'),
    'system/bt': ('android_system_bt', 'bcca9a572f1cc539ba21ebe940c3642ce8707d1a'),
}
results = []
base = ROOT / 'sources/android_device_amazon_mt8163-common/patches'
for project, (repo, commit) in PROJECTS.items():
    dest = ROOT / 'work/patch-probe' / project
    dest.mkdir(parents=True, exist_ok=True)
    for patch in sorted((base / project).glob('*.patch')):
        files = re.findall(r'^--- a/(.+)$', patch.read_text(), re.M)
        missing = []
        hashes = {}
        for name in files:
            url = f'https://raw.githubusercontent.com/LineageOS/{repo}/{commit}/{name}'
            try:
                data = urllib.request.urlopen(url, timeout=45).read()
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    raise
                missing.append(name)
                continue
            target = dest / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            hashes[name] = hashlib.sha256(data).hexdigest()
        # --no-index supports this intentionally incomplete, non-repository fixture.
        env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(dest.parent))
        run = subprocess.run(['git', 'apply', '--check', '--no-index', '--verbose', str(patch)],
                             cwd=dest, env=env, text=True, capture_output=True)
        if 'Skipped patch' in run.stderr:
            raise RuntimeError('Git skipped a fixture; this is not a valid applicability test')
        results.append(dict(project=project, commit=commit, patch=str(patch.relative_to(ROOT)),
                            missing=missing, sha256=hashes, exit_code=run.returncode,
                            diagnostics=run.stderr.strip()))
output = ROOT / 'evidence/android11-patch-probe.json'
output.write_text(json.dumps(results, indent=2) + '\n')
for r in results:
    print(('APPLIES' if r['exit_code'] == 0 else 'NEEDS REWORK'), r['patch'])
print('Patch applicability only; not a compilation or runtime test.')

# Check the initial graphics rebase against the same pinned Android 11 revision.
dest = ROOT / 'work/patch-probe/frameworks/base'
repo, commit = PROJECTS['frameworks/base']
for name in ['Bitmap.cpp', 'BitmapFactory.cpp']:
    target = dest / 'libs/hwui/jni' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    url = f'https://raw.githubusercontent.com/LineageOS/{repo}/{commit}/libs/hwui/jni/{name}'
    target.write_bytes(urllib.request.urlopen(url, timeout=45).read())
patch = ROOT / 'patches/android11/frameworks/base/0001-Rebase-MTK-bitmap-workaround-to-Android-11.patch'
run = subprocess.run(['git', 'apply', '--check', '--no-index', '--verbose', str(patch)],
                     cwd=dest, env=dict(os.environ, GIT_CEILING_DIRECTORIES=str(dest.parent)),
                     text=True, capture_output=True)
if 'Skipped patch' in run.stderr:
    raise RuntimeError('Invalid rebase check: Git skipped a fixture')
(ROOT / 'evidence/android11-bitmap-rebase-check.txt').write_text(
    run.stdout + run.stderr + f'Exit code: {run.returncode}\n')
print('Bitmap rebase:', 'APPLIES' if run.returncode == 0 else 'NEEDS REWORK')
raise SystemExit(run.returncode)
