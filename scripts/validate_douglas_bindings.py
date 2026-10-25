#!/usr/bin/env python3
"""Full pinned ACK binding-context diagnostic; exits nonzero on any diagnostics."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / 'projects/firetabs-android/kernel/dtb/bindings.lock.json'
WORK = ROOT / 'work/binding-validation'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment', choices=['baseline', 'pmic-node-names', 'sysirq-node-name'], default='baseline')
    parser.add_argument('--download', action='store_true', help='Allow one hash-locked archive download, at most 20 MiB')
    args = parser.parse_args()
    lock = json.loads(LOCK.read_text())
    WORK.mkdir(parents=True, exist_ok=True)
    archive = WORK / 'bindings.tar.gz'
    if not archive.exists():
        if not args.download:
            parser.error('Archive absent; use --download for the bounded source fetch')
        with urllib.request.urlopen(lock['url'], timeout=60) as response:
            data = response.read(20 * 1024 * 1024 + 1)
        if len(data) != lock['bytes'] or hashlib.sha256(data).hexdigest() != lock['sha256']:
            parser.error('Archive size/hash mismatch; not extracting')
        archive.write_bytes(data)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != lock['sha256']:
        parser.error('Existing archive hash mismatch')
    variant_dir = 'repro' if args.experiment == 'baseline' else args.experiment
    variant_file = 'experiment.json' if args.experiment == 'baseline' else args.experiment + '.json'
    dtb = ROOT / 'work/dtb-compile' / variant_dir / 'douglas.dtb'
    experiment = json.loads((LOCK.parent / variant_file).read_text())
    if hashlib.sha256(dtb.read_bytes()).hexdigest() != experiment['expected_artifact']['sha256']:
        parser.error('DTB differs from pinned DT-only experiment')
    tools = ROOT / 'work/dtb-tool/venv/bin'
    version = subprocess.check_output([str(tools / 'dt-validate'), '-V'], text=True).strip()
    if version != lock['dtschema_version']:
        parser.error('Unexpected dtschema version')
    output = WORK / ('result' if args.experiment == 'baseline' else 'result-' + args.experiment)
    output.mkdir(exist_ok=True)
    (output / 'diagnostics.json').unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix='source-', dir=WORK) as temporary:
        source = Path(temporary)
        with tarfile.open(archive) as handle:
            handle.extractall(source, filter='data')
        count = len(list(source.rglob('*.yaml')))
        if count != lock['yaml_files']:
            parser.error('Binding corpus file count mismatch')
        commands = [
            [str(tools / 'dt-mk-schema'), '-j', '-o', str(output / 'processed.json'), str(source)],
            [str(tools / 'dt-validate'), '-s', str(output / 'processed.json'), '-m', '--json-output', str(output / 'diagnostics.json'), str(dtb)]]
        results = []
        for name, command in zip(['mk-schema', 'validate'], commands):
            process = subprocess.run(command, capture_output=True, text=True, timeout=180)
            for stream in ['stdout', 'stderr']:
                value = getattr(process, stream).replace(str(source), '<ack-bindings>').replace(str(ROOT), '<workspace>')
                (output / f'{name}.{stream}').write_text(value)
            results.append({'command': [x.replace(str(source), '<ack-bindings>').replace(str(ROOT), '<workspace>') for x in command],
                            'exit_code': process.returncode, 'stderr_lines': len(process.stderr.splitlines())})
            if process.returncode != 0:
                break
        diagnostics = json.loads((output / 'diagnostics.json').read_text()) if len(results) == 2 and (output / 'diagnostics.json').exists() else []
        passed = len(results) == 2 and all(x['exit_code'] == 0 and x['stderr_lines'] == 0 for x in results) and not diagnostics
        report = {'scope': 'Pinned ACK corpus only; donor-specific schemas still incomplete; no hardware validation',
                  'experiment': args.experiment, 'ack_commit': lock['ack_commit'], 'archive_sha256': lock['sha256'], 'yaml_files': count,
                  'dtschema_version': version, 'dtb_sha256': experiment['expected_artifact']['sha256'],
                  'commands': results, 'diagnostic_count': len(diagnostics),
                  'diagnostic_types': dict(Counter(x['type'] for x in diagnostics)),
                  'diagnostic_levels': dict(Counter(x['level'] for x in diagnostics)), 'passed': passed}
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
