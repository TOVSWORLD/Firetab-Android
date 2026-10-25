#!/usr/bin/env python3
"""Validate a release candidate offline; never tag, upload, publish or touch a device."""
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re

from ci import ROOT, require, safe_path, sha, validate_progress

VERSION = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-(alpha|beta|rc)\.([1-9][0-9]*))?')


def record_path(root, name):
    path = root / safe_path(name)
    require(path.resolve().is_relative_to(root.resolve()), f'Path escapes root: {name}')
    require(path.is_file() and not path.is_symlink() and path.stat().st_size > 0, f'Missing/empty record: {name}')
    return path


def read_json(root, name):
    return json.loads(record_path(root, name).read_text())


def validate_manifest(manifest, root=ROOT, artifact_root=None):
    policy = read_json(root, 'releases/policy.json')
    project = manifest['project']
    require(project in policy['streams'], 'Unknown release project')
    stream = policy['streams'][project]
    version = VERSION.fullmatch(manifest['version'])
    require(version is not None, 'Invalid release version/channel')
    require(manifest['tag'] == stream['tag_prefix'] + manifest['version'], 'Tag/version prefix mismatch')
    require(manifest['kind'] == stream['kind'], 'Release kind/project mismatch')
    require(sha(manifest['tested_revision'], 40), 'Exact tested revision required')
    notes = record_path(root, manifest['notes'])
    require(notes.suffix == '.md', 'Release notes must be Markdown')
    require(type(manifest['native_runtime']) is bool, 'Explicit native-runtime claim required')
    require(not manifest['native_runtime'] or project == 'crestron-panel', 'Native-runtime claim only applies to panel load')
    artifacts = manifest['artifacts']
    require(isinstance(artifacts, list), 'Artifact list required')
    if project == 'workspace':
        require(not artifacts and not manifest['native_runtime'], 'Source snapshots cannot distribute runtime artifacts')
        return
    require(artifacts, 'Runtime release needs artifact records')
    prerelease = version.group(4)
    stable_gates = prerelease in {None, 'rc'}
    progress = read_json(root, f'projects/{project}/validation.json')
    validate_progress(progress, project, root)
    if project == 'firetabs-android':
        stages = ['kernel_compile', 'android_compile', 'boot']
        if stable_gates:
            stages += ['hardware', 'general_purpose_soak']
    else:
        stages = ['client_runtime', 'cp4_integration']
        if stable_gates:
            stages += ['full_function_soak']
        if manifest['native_runtime']:
            stages += ['native_runtime']
    for name in stages:
        stage = progress['stages'][name]
        require(stage['status'] == 'passed', f'Unpassed release gate: {name}')
        require(stage['revision'] == manifest['tested_revision'], f'Stale evidence revision: {name}')
    provenance = manifest['provenance']
    for field in ['source_manifest', 'toolchain', 'device_matrix']:
        record_path(root, provenance[field])
    if stable_gates:
        support = read_json(root, manifest['support_record'])
        require(support['project'] == project and support['version'] == manifest['version'], 'Support record identity mismatch')
        require(bool(support['maintainer'].strip()), 'Named support maintainer required')
        start, end = date.fromisoformat(support['starts']), date.fromisoformat(support['ends'])
        require(start <= date.today() <= end, 'Support record must be currently active')
        require((end-start).days >= (730 if support.get('lts') else 365), 'Support period shorter than declared policy')
        for field in ['install', 'upgrade', 'recovery']:
            record_path(root, support[field])
    paths = []
    for artifact in artifacts:
        path = safe_path(artifact['path'])
        paths.append(path)
        require(type(artifact['bytes']) is int and artifact['bytes'] > 0, 'Artifact size must be positive')
        require(sha(artifact['sha256']), 'Invalid artifact hash')
        if artifact_root is not None:
            actual = record_path(artifact_root, path)
            require(actual.stat().st_size == artifact['bytes'], f'Artifact size mismatch: {path}')
            digest = hashlib.sha256()
            with actual.open('rb') as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b''):
                    digest.update(chunk)
            require(digest.hexdigest() == artifact['sha256'], f'Artifact content mismatch: {path}')
    require(len(paths) == len(set(paths)), 'Duplicate artifact paths')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--artifact-root', type=Path, help='Verify actual local artifact bytes before publication')
    args = parser.parse_args()
    validate_manifest(json.loads(args.manifest.read_text()), artifact_root=args.artifact_root)
    print('PASS: release metadata and declared evidence gates; no publication performed')
    if args.artifact_root is None:
        print('Artifact bytes were not checked; use --artifact-root before publishing runtime assets.')


if __name__ == '__main__':
    main()
