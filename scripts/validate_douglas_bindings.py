#!/usr/bin/env python3
"""Full pinned ACK binding-context diagnostic; exits nonzero on any diagnostics."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / 'projects/firetabs-android/kernel/dtb/bindings.lock.json'
WORK = ROOT / 'work/binding-validation'


def apply_locked_proposal(source, ack_commit, filename):
    """Apply only the hash-locked UART proposal to an isolated corpus extraction."""
    profile = json.loads((LOCK.parent / ('bindings/' + filename)).read_text())
    patch = LOCK.parent / profile['patch']
    schema = source / profile['schema']
    if (profile['ack_commit'] != ack_commit or
            hashlib.sha256(patch.read_bytes()).hexdigest() != profile['patch_sha256'] or
            hashlib.sha256(schema.read_bytes()).hexdigest() != profile['original_sha256']):
        raise ValueError('Proposed binding input hash/revision mismatch')
    subprocess.run(['git', 'apply', '--no-index', str(patch)], cwd=source,
                   env={**os.environ, 'GIT_CEILING_DIRECTORIES': str(source.parent)}, check=True)
    if hashlib.sha256(schema.read_bytes()).hexdigest() != profile['proposed_sha256']:
        raise ValueError('Proposed binding output hash mismatch')
    return profile, schema


def apply_uart_proposal(source, ack_commit):
    return apply_locked_proposal(source, ack_commit, 'mt8163-uart.json')


def apply_gunyah_yaml_repair(source, ack_commit):
    profile = json.loads((LOCK.parent / 'bindings/gunyah-yaml-repair.json').read_text())
    schema = source / profile['schema']
    original = schema.read_bytes()
    if profile['ack_commit'] != ack_commit or hashlib.sha256(original).hexdigest() != profile['original_sha256']:
        raise ValueError('Gunyah repair input hash/revision mismatch')
    repaired = original.replace(b'\t', b' ' * profile['tab_replacement_spaces'])
    if hashlib.sha256(repaired).hexdigest() != profile['repaired_sha256']:
        raise ValueError('Gunyah repair output hash mismatch')
    schema.write_bytes(repaired)
    return profile


def bounded_result_name(name):
    """Keep existing profile paths unless a component exceeds filesystem limits."""
    if len(name.encode('utf-8')) <= 255:
        return name
    return 'result-' + hashlib.sha256(name.encode('utf-8')).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment', choices=['baseline', 'pmic-node-names', 'sysirq-node-name', 'rdma-node-name', 'pwrap-pmic-node-name', 'usb-frequency-resource'], default='baseline')
    parser.add_argument('--binding-profile', choices=['ack', 'mt8163-uart-proposed'], default='ack')
    parser.add_argument('--extra-binding', choices=['mt8163-sysirq', 'mt8163-timer', 'mt8163-mmc', 'mt8163-uart-dma', 'mt8163-i2c', 'mt8163-spi', 'mt8163-auxadc', 'mt8163-rng', 'mt8163-keypad', 'mt8163-efuse', 'mt8163-gce', 'mt8163-topckgen', 'mt8163-infracfg', 'mt8163-apmixedsys', 'mt8163-gate-clocks', 'mt8163-mmsys', 'mt8163-pinctrl', 'mt8163-pwrap', 'mt8163-scpsys', 'mt8163-power-controller', 'mt8163-watchdog', 'mt8163-pctl-syscfg', 'mt8163-iommu', 'mt8163-smi-common', 'mt8163-smi-larb', 'mt8163-musb', 'mt8163-tphy', 'mt8163-audsys', 'mt8163-sym827'], action='append', default=[], help='Additional opt-in locked binding proposals')
    parser.add_argument('--repair-pmic-selector', action='store_true', help='Opt-in exact MT6323 sys-off selector proposal')
    parser.add_argument('--repair-gunyah-yaml', action='store_true', help='Opt-in hash-locked indentation repair; not schema qualification')
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
    result_name = 'result' if args.experiment == 'baseline' else 'result-' + args.experiment
    if args.binding_profile != 'ack':
        result_name += '-' + args.binding_profile
    if args.repair_gunyah_yaml:
        result_name += '-gunyah-yaml-repaired'
    if args.repair_pmic_selector:
        result_name += '-pmic-selector'
    if args.extra_binding:
        result_name += '-' + '-'.join(sorted(set(args.extra_binding)))
    output = WORK / bounded_result_name(result_name)
    output.mkdir(exist_ok=True)
    (output / 'diagnostics.json').unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix='source-', dir=WORK) as temporary:
        source = Path(temporary)
        with tarfile.open(archive) as handle:
            handle.extractall(source, filter='data')
        count = len(list(source.rglob('*.yaml')))
        if count != lock['yaml_files']:
            parser.error('Binding corpus file count mismatch')
        yaml_repair = apply_gunyah_yaml_repair(source, lock['ack_commit']) if args.repair_gunyah_yaml else None
        profile = None
        commands = []
        if args.binding_profile != 'ack':
            profile, schema = apply_uart_proposal(source, lock['ack_commit'])
            commands.append(('doc-validate', [str(tools / 'dt-doc-validate'), '-u', str(source), str(schema)]))
        pmic_proposal = None
        if args.repair_pmic_selector:
            pmic_proposal, schema = apply_locked_proposal(source, lock['ack_commit'], 'pmic-domain-selector.json')
            commands.append(('pmic-doc-validate', [str(tools / 'dt-doc-validate'), '-u', str(source), str(schema)]))
        extra_proposals = []
        for name in sorted(set(args.extra_binding)):
            extra, schema = apply_locked_proposal(source, lock['ack_commit'], name + '.json')
            extra_proposals.append(extra)
            commands.append((name + '-doc-validate', [str(tools / 'dt-doc-validate'), '-u', str(source), str(schema)]))
        commands += [
            ('mk-schema', [str(tools / 'dt-mk-schema'), '-j', '-o', str(output / 'processed.json'), str(source)]),
            ('validate', [str(tools / 'dt-validate'), '-s', str(output / 'processed.json'), '-m', '--json-output', str(output / 'diagnostics.json'), str(dtb)])]
        results = []
        for name, command in commands:
            process = subprocess.run(command, capture_output=True, text=True, timeout=180)
            for stream in ['stdout', 'stderr']:
                value = getattr(process, stream).replace(str(source), '<ack-bindings>').replace(str(ROOT), '<workspace>')
                (output / f'{name}.{stream}').write_text(value)
            results.append({'stage': name, 'command': [x.replace(str(source), '<ack-bindings>').replace(str(ROOT), '<workspace>') for x in command],
                            'exit_code': process.returncode, 'stderr_lines': len(process.stderr.splitlines())})
            if process.returncode != 0:
                break
        diagnostics = json.loads((output / 'diagnostics.json').read_text()) if results and results[-1]['stage'] == 'validate' and (output / 'diagnostics.json').exists() else []
        passed = len(results) == len(commands) and all(x['exit_code'] == 0 and x['stderr_lines'] == 0 for x in results) and not diagnostics
        report = {'scope': 'Pinned ACK corpus with explicitly reported local proposal, if selected; donor-specific schemas still incomplete; no hardware validation',
                  'extra_proposals': extra_proposals, 'pmic_selector_proposal': pmic_proposal, 'yaml_repair': yaml_repair, 'experiment': args.experiment, 'binding_profile': args.binding_profile, 'binding_proposal': profile, 'ack_commit': lock['ack_commit'], 'archive_sha256': lock['sha256'], 'yaml_files': count,
                  'dtschema_version': version, 'wrapper_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'dtb_sha256': experiment['expected_artifact']['sha256'],
                  'commands': results, 'diagnostic_count': len(diagnostics),
                  'diagnostic_types': dict(Counter(x['type'] for x in diagnostics)),
                  'diagnostic_levels': dict(Counter(x['level'] for x in diagnostics)), 'passed': passed}
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
