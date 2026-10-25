#!/usr/bin/env python3
"""Offline, fail-closed repository/evidence checks. Never builds or touches devices."""
import argparse
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
STAGES = {
    'firetabs-android': ['kernel_compile', 'android_compile', 'boot', 'hardware', 'general_purpose_soak'],
    'crestron-panel': ['client_runtime', 'cp4_integration', 'full_function_soak', 'native_runtime'],
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_path(value):
    path = PurePosixPath(value)
    require(value and not path.is_absolute() and '..' not in path.parts, f'Unsafe path: {value}')
    return value


def sha(value, length=64):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{%d}' % length, value) is not None


def load(path):
    return json.loads((ROOT / path).read_text())


def validate_progress(record, project, root=ROOT):
    require(record['project'] == project, 'Project identity mismatch')
    require(list(record['stages']) == STAGES[project], 'Stages missing, reordered or unknown')
    previous_passed = True
    for name, stage in record['stages'].items():
        status = stage['status']
        require(status in {'not_run', 'failed', 'passed'}, f'Invalid status: {name}')
        if status == 'passed':
            require(previous_passed, f'{name}: earlier validation has not passed')
            require(sha(stage['revision'], 40), f'{name}: exact tested revision required')
            require(stage['evidence'], f'{name}: evidence required')
        if status != 'not_run':
            require(sha(stage['revision'], 40) and stage['evidence'], f'{name}: execution needs revision and evidence')
        for item in stage['evidence']:
            path = root / safe_path(item['path'])
            require(path.is_file() and not path.is_symlink(), f'Missing/unsafe evidence: {path}')
            require(path.stat().st_size > 0, f'Empty evidence: {path}')
            require(sha(item['sha256']), f'Invalid evidence hash: {path}')
            require(hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], f'Evidence changed: {path}')
        previous_passed = previous_passed and status == 'passed'


def truncation(old, new):
    before = len(old.splitlines())
    after = len(new.splitlines())
    return before - after > 100 and after < before * 0.7


def check_python(source, path):
    tree = ast.parse(source, filename=path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Raise) and node.exc:
            expr = node.exc.func if isinstance(node.exc, ast.Call) else node.exc
            require(not isinstance(expr, ast.Name) or expr.id != 'NotImplementedError', f'{path}: unimplemented body')
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body[:]
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                body = body[1:]
            empty = not body or all(isinstance(x, ast.Pass) or (isinstance(x, ast.Expr) and isinstance(x.value, ast.Constant) and x.value.value is Ellipsis) for x in body)
            require(not empty, f'{path}:{node.lineno}: empty implementation')


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def repository(base):
    files = [x for x in git('ls-files', '-z').decode().split('\0') if x]
    require(files, 'No tracked files')
    for name in files:
        path = ROOT / name
        require(not name.startswith(('sources/', 'work/', 'out/')), f'Unreviewed generated content: {name}')
        require(path.suffix.lower() not in {'.apk', '.puf', '.img', '.so'}, f'Unexpected binary distribution: {name}')
        if path.suffix == '.json':
            load(name)
        elif path.suffix == '.xml':
            ET.parse(path)
        elif path.suffix == '.py':
            check_python(path.read_text(), name)
    if base:
        require(sha(base, 40), 'Comparison base must be an exact commit')
        git('cat-file', '-e', base + '^{commit}')
        exceptions = load('projects/change-exceptions.json')
        changes = git('diff', '--no-renames', '--name-only', '-z', base, 'HEAD').decode().split('\0')
        for name in filter(None, changes):
            exists = subprocess.run(['git', '-C', str(ROOT), 'cat-file', '-e', f'{base}:{name}'], capture_output=True).returncode == 0
            if not exists:
                continue
            old = git('show', f'{base}:{name}')
            path = ROOT / name
            new = path.read_bytes() if path.is_file() else b''
            if b'\0' in old or b'\0' in new:
                continue
            if truncation(old, new):
                approval = exceptions.get(name, {})
                require(approval.get('old_sha256') == hashlib.sha256(old).hexdigest() and len(approval.get('reason', '').strip()) >= 20,
                        f'{name}: large loss needs exact old-content hash and review reason')
    print('PASS: repository syntax, distribution boundaries and requested change guard')


def android():
    entries = load('evidence/sources.lock.json')
    directories = []
    for entry in entries:
        directories.append(safe_path(entry['directory']))
        require(entry['directory'].startswith('sources/'), 'Checkout outside sources')
        require(entry['url'].startswith('https://github.com/') and entry['url'].endswith('.git'), 'Unexpected source origin')
        require(sha(entry['commit'], 40), 'Source commit must be pinned')
    require(entries and len(directories) == len(set(directories)), 'Empty/duplicate source lock')
    manifests = list((ROOT / 'manifests').glob('*.xml'))
    require(len(manifests) >= 2, 'Historical manifests missing')
    for path in manifests:
        projects = ET.parse(path).getroot().findall('project')
        paths = [safe_path(x.attrib['path']) for x in projects]
        require(projects and len(paths) == len(set(paths)), 'Empty/duplicate manifest paths')
        require(all(sha(x.attrib['revision'], 40) for x in projects), 'Unpinned manifest')
    validate_progress(load('projects/firetabs-android/validation.json'), 'firetabs-android')
    print('PASS: Android source/manifest records; no kernel or Android compilation performed')


def panel():
    locked = load('evidence/crestron/downloads.lock.json')
    inspected = load('evidence/crestron/apk-inspection.json')
    require(len(locked) == 3 and len({x['name'] for x in locked}) == 3, 'Expected three unique archive records')
    require(len(inspected) == 3 and len({x['name'] for x in inspected}) == 3, 'Expected three unique inspection records')
    packages = {'h5display': 'com.crestron.blackbird', 'generalweb': 'com.crestron.generalweb', 'home-panel': 'com.crestron.phoenix.touchscreen'}
    for lock in locked:
        require(lock['name'] in packages, 'Unknown app evidence')
        require(lock['url'].startswith('https://devicefiles.crestron.io/apps/70-Series/Signed/'), 'Unexpected APK source')
        require(isinstance(lock['archive_bytes'], int) and 0 < lock['archive_bytes'] < 100_000_000, 'Invalid archive size')
        app = next(x for x in inspected if x['name'] == lock['name'])
        require(app['package'] == packages[lock['name']], 'Panel/mobile package confusion')
        for field in ['archive_sha256', 'apk_sha256']:
            require(sha(lock[field]) and app[field] == lock[field], 'Inspection/download hash mismatch')
        manifest = ET.parse(ROOT / f"evidence/crestron/{lock['name']}-manifest.xml").getroot()
        require(manifest.attrib['package'] == app['package'], 'Manifest package mismatch')
        sdk = manifest.find('uses-sdk')
        for field, attr in [('min_sdk', 'minSdkVersion'), ('target_sdk', 'targetSdkVersion')]:
            require(sdk.attrib['{http://schemas.android.com/apk/res/android}' + attr] == app[field], 'Manifest SDK mismatch')
    validate_progress(load('projects/crestron-panel/validation.json'), 'crestron-panel')
    print('PASS: panel static evidence consistency; no apps or native libraries executed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', choices=['repository', *STAGES])
    parser.add_argument('--base', help='Exact base SHA for committed change review')
    args = parser.parse_args()
    if args.project == 'repository':
        repository(args.base)
    elif args.project == 'firetabs-android':
        android()
    else:
        panel()


if __name__ == '__main__':
    main()
