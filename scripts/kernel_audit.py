#!/usr/bin/env python3
"""Verify/restore bounded pinned kernel evidence and optionally reproduce a CPP gap probe."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import urllib.request
from urllib.parse import urlsplit

from ci import ROOT, require, safe_path, sha

INDEX = ROOT / 'evidence/kernel-audit/sources.json'


def verify_records(index, root=ROOT):
    seen = set()
    for record in index['records']:
        require(record['status'] in {200, 404}, 'Unknown source observation status')
        require(urlsplit(record['url']).scheme == 'https', 'Evidence URL must use HTTPS')
        require(urlsplit(record['url']).netloc in {'android.googlesource.com', 'raw.githubusercontent.com'}, 'Unexpected source origin')
        if record['status'] == 404:
            continue
        name = safe_path(record['path'])
        require(name not in seen, f'Duplicate evidence record: {name}')
        seen.add(name)
        path = root / name
        require(path.resolve().is_relative_to(root.resolve()), f'Evidence escapes root: {name}')
        require(path.is_file() and not path.is_symlink(), f'Missing source evidence: {name}')
        data = path.read_bytes()
        require(len(data) == record['bytes'] and sha(record['sha256']), f'Invalid source metadata: {name}')
        require(hashlib.sha256(data).hexdigest() == record['sha256'], f'Source evidence hash mismatch: {name}')
    return len(seen)


def restore(index):
    total = sum(x.get('bytes', 0) for x in index['records'])
    require(total < 10_000_000, 'Restore exceeds bounded 10 MB source budget')
    for record in index['records']:
        if record['status'] != 200:
            continue
        path = ROOT / safe_path(record['path'])
        require(path.resolve().is_relative_to(ROOT) and not path.is_symlink(), 'Restore escapes repository or targets a symlink')
        if path.exists():
            require(hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'], f'Refusing to replace modified evidence: {path}')
            continue
        require(urlsplit(record['url']).scheme == 'https' and urlsplit(record['url']).netloc in {'android.googlesource.com', 'raw.githubusercontent.com'}, 'Unexpected source origin')
        with urllib.request.urlopen(record['url'], timeout=45) as response:
            body = response.read(3_000_001)
        require(len(body) <= 3_000_000, 'Source response exceeds per-file limit')
        if record['format'] == 'gitiles-text':
            body = base64.b64decode(body.strip(), validate=True)
        elif record['format'] == 'gitiles-json':
            require(body.startswith(b")]}'\n"), 'Unexpected Gitiles JSON envelope')
            body = body[5:]
        else:
            require(record['format'] == 'raw', 'Unknown evidence encoding')
        require(len(body) == record['bytes'] and hashlib.sha256(body).hexdigest() == record['sha256'], 'Downloaded content differs from source lock')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)


def preprocess_probe():
    compiler = shutil.which('clang')
    require(compiler is not None, 'clang required for optional preprocessing probe')
    evidence = ROOT / 'evidence/kernel-audit'
    dest = ROOT / 'work/kernel-audit-cpp'
    dest.mkdir(parents=True, exist_ok=True)
    # Use unmodified community board/SoC files plus actual ACK headers. Do not invent headers.
    args = [compiler, '-E', '-P', '-nostdinc', '-undef', '-x', 'assembler-with-cpp',
            '-I', str(evidence/'ack/include'), '-I', str(evidence/'bengris7/arch/arm64/boot/dts/mediatek'),
            str(evidence/'bengris7/arch/arm64/boot/dts/mediatek/mt8163-amazon-douglas.dts')]
    result = subprocess.run(args, text=True, capture_output=True)
    (dest/'partial.dts').write_text(result.stdout)
    missing = 'dt-bindings/clock/mediatek,mt8163-audsys.h'
    require(result.returncode != 0 and missing in result.stderr, 'Probe no longer reproduces the recorded missing header; inspect new result')
    normalized = result.stderr.replace(str(ROOT)+'/', '')
    report = dict(kind='preprocessing-only',compiler=subprocess.check_output([compiler,'--version'],text=True).splitlines()[0],
                  argv=[x.replace(str(ROOT)+'/', '') for x in args],exit_code=result.returncode,
                  expected_missing_header=missing,stderr=normalized,kernel_compiled=False,device_tested=False)
    output = evidence/'cpp-probe.json'
    output.write_text(json.dumps(report,indent=2)+'\n')
    print('REPRODUCED: copying the community DTS files onto ACK headers stops at '+missing)
    print('This is a preprocessing failure, not a kernel compilation or hardware result.')


def check_claims():
    matrix = json.loads((ROOT/'projects/firetabs-android/kernel/support-matrix.json').read_text())
    for row in matrix['components']:
        require(row['status'] in {'integration-gap','reuse-candidate','unverified'}, 'Unsupported audit status')
        require(row['evidence'] and row['next_test'], 'Evidence and discriminating next test required')
        for ref in row['evidence']:
            path = ROOT / safe_path(ref['path'])
            require(ref['needle'] in path.read_text(), f'Claim anchor missing: {row["id"]}: {ref["path"]}')
    return len(matrix['components'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download', action='store_true', help='Explicitly restore missing locked evidence only (<10 MB decoded total)')
    parser.add_argument('--probe-cpp', action='store_true', help='Reproduce the recorded source dependency failure with local clang')
    args = parser.parse_args()
    index = json.loads(INDEX.read_text())
    if args.download:
        restore(index)
    count = verify_records(index)
    claims = check_claims()
    print(f'PASS: {count} pinned source/listing hashes and {claims} component evidence anchors')
    if args.probe_cpp:
        preprocess_probe()
    else:
        print('Offline source consistency only; no compilation, device actions or network requests.')


if __name__ == '__main__':
    main()
