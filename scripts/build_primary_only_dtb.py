#!/usr/bin/env python3
"""Compile opt-in primary-only DT experiment from cached locked inputs; never boot."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
from compare_pmic_dtb import snapshot
from build_douglas_dtb import inspect_header

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT/'projects/firetabs-android/kernel/dtb/primary-only'


def compare(before, after):
    expected = copy.deepcopy(before)
    if 'status' in expected['/psci'] or 'bootargs' in expected['/chosen']:
        raise ValueError('Unexpected base firmware/command-line contract')
    encode = lambda text: ' '.join(f'{b:x}' for b in text.encode()+b'\0')
    expected['/psci']['status'] = encode('disabled')
    expected['/chosen']['bootargs'] = encode('nr_cpus=1 maxcpus=0')
    if after != expected:
        raise ValueError('Unexpected node/property change')
    return {'nodes_compared': len(before), 'original_property_count': sum(len(x) for x in before.values()), 'original_properties_preserved': True,
            'added_properties': ['/psci/status=disabled', '/chosen/bootargs=nr_cpus=1 maxcpus=0'],
            'secondary_cpu_nodes_deleted': False, 'runtime_command_line_verified': False,
            'firmware_calls_globally_proven_absent': False, 'boot_verified': False}



def source_audit():
    folder = ROOT/'evidence/primary-only'
    index = json.loads((folder/'sources.json').read_text())
    source = {}
    for record in index['records']:
        raw = (ROOT/record['path']).read_bytes()
        if len(raw) != record['bytes'] or hashlib.sha256(raw).hexdigest() != record['sha256']:
            raise ValueError('CPU initialization source hash mismatch')
        source[record['source_path']] = raw.decode()
    anchors = []
    for name, needle in [('drivers/firmware/psci/psci.c', 'if (!np || !of_device_is_available(np))'),
                         ('arch/arm64/kernel/setup.c', 'parse_early_param();'),
                         ('arch/arm64/kernel/setup.c', 'psci_dt_init();'),
                         ('arch/arm64/kernel/setup.c', 'init_bootcpu_ops();'),
                         ('arch/arm64/include/asm/cpu_ops.h', 'init_cpu_ops(0);'),
                         ('arch/arm64/kernel/smp.c', 'for (i = 1; i < nr_cpu_ids; i++)'),
                         ('arch/arm64/kernel/smp.c', 'if (max_cpus == 0)'),
                         ('kernel/smp.c', 'early_param("nr_cpus", nrcpus);'),
                         ('kernel/smp.c', 'bringup_nonboot_cpus(setup_max_cpus);')]:
        text = source[name]
        if text.count(needle) != 1:
            raise ValueError('CPU initialization anchor differs')
        anchors.append({'source_path': name, 'line': text[:text.index(needle)].count('\n')+1, 'anchor': needle})
    setup = source['arch/arm64/kernel/setup.c']
    if not setup.index('parse_early_param();') < setup.index('psci_dt_init();') < setup.index('init_bootcpu_ops();'):
        raise ValueError('Initialization order differs')
    config = (ROOT/'evidence/diagnostic-kernel/diagnostic.config').read_text()
    for symbol in ['ACPI', 'FORCE_NR_CPUS', 'CPU_IDLE', 'SUSPEND', 'HIBERNATION', 'CMDLINE_FORCE']:
        if 'CONFIG_'+symbol+'=y' in config.splitlines():
            raise ValueError('Diagnostic policy permits an unqualified CPU path: '+symbol)
    return {'anchors': anchors, 'diagnostic_config_sha256': hashlib.sha256(config.encode()).hexdigest(),
            'maxcpus_1_suppresses_psci_dt_init': False,
            'nr_cpus_1_limits_secondary_setup_loop': True,
            'maxcpus_0_skips_secondary_prepare_loop': True,
            'disabled_psci_node_guard': 'See pinned drivers/firmware/psci/psci.c psci_dt_init availability check',
            'assumptions': ['Effective command line retained by loader', 'Boot CPU matches donor MPIDR0',
                            'ACPI remains disabled by diagnostic policy'],
            'not_proven': ['Other firmware services/RSI/driver calls', 'Loader preservation of DT/bootargs',
                           'Primary entry, clocks, interrupts, RAM, logging and recovery']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Fresh output directory required')
    lock = json.loads((PROJECT/'experiment.json').read_text())
    base = ROOT/'work/dtb-compile/rdma-node-name'
    append = PROJECT/'append.dts'
    for path, expected in [(base/'douglas.dtb', lock['base_dtb_sha256']),
                           (base/'douglas.pp.dts', lock['base_preprocessed_sha256']),
                           (append, lock['append_sha256'])]:
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Input hash mismatch')
    tools = ROOT/'work/dtb-tool/build'
    if subprocess.check_output([str(tools/'dtc'), '--version'], text=True).strip() != 'Version: DTC 1.8.1':
        raise ValueError('Pinned dtc required')
    args.output.mkdir(parents=True)
    source = args.output/'primary-only.dts'
    source.write_bytes((base/'douglas.pp.dts').read_bytes()+b'\n'+append.read_bytes())
    target = args.output/'primary-only.dtb'
    command = [str(tools/'dtc'), '-I', 'dts', '-O', 'dtb', '-o', str(target), str(source)]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    if result.stderr:
        raise ValueError('DTC diagnostics require review: '+result.stderr)
    facts = compare(snapshot(tools/'fdtget', base/'douglas.dtb'), snapshot(tools/'fdtget', target))
    artifact = inspect_header(target.read_bytes())
    if artifact != lock['expected_artifact']:
        raise ValueError('Compiled artifact differs from reviewed experiment')
    report = {'scope': 'DT compilation/semantic comparison only; not an assembled firmware or hardware test',
              'base_dtb_sha256': lock['base_dtb_sha256'], 'artifact': artifact,
              'facts': facts, 'source_audit': source_audit(), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
