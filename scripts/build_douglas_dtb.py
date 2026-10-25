#!/usr/bin/env python3
"""Compile/inspect the isolated douglas DT experiment; never pack or boot an image."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

from ci import ROOT, require, safe_path

BASE = ROOT/'evidence/dtb-compile'
PROJECT = ROOT/'projects/firetabs-android/kernel/dtb'


def verify_inputs(experiment_name="baseline"):
    index = json.loads((BASE/'sources.lock.json').read_text())
    paths = set()
    for item in index['records']:
        name = safe_path(item['path'])
        require(name not in paths, 'Duplicate DT dependency: '+name)
        paths.add(name)
        path = BASE/'inputs'/name
        data = path.read_bytes()
        require(len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256'], 'DT source changed: '+name)
    for edge in index['dependencies']:
        require(edge['parent'] in paths and edge['path'] in paths, 'Unresolved DT dependency')
    experiment_file = 'experiment.json' if experiment_name == 'baseline' else safe_path(experiment_name) + '.json'
    experiment = json.loads((PROJECT/experiment_file).read_text())
    for item in experiment['patches']:
        path = PROJECT/safe_path(item['path'])
        require(hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], 'DT patch changed: '+str(path))
    return index, experiment


def inspect_header(data):
    require(len(data) >= 40, 'Truncated DTB header')
    header = struct.unpack('>10I',data[:40])
    require(header[0] == 0xd00dfeed and header[1] == len(data), 'Invalid DTB magic/total size')
    require(header[5] == 17 and header[6] <= 17, 'Unexpected DTB format version')
    require(header[2]+header[9] <= len(data) and header[3]+header[8] <= len(data), 'Invalid DTB block bounds')
    return dict(format_version=header[5],bytes=len(data),sha256=hashlib.sha256(data).hexdigest())


def compile_tree(index, experiment, output, dtc, fdtget):
    report = dict(scope='DT compilation only; no kernel build or hardware test',status='failed',commands=[])
    def run(argv, stage):
        result = subprocess.run([str(x) for x in argv],text=True,capture_output=True)
        normalize = lambda value: value.replace(str(stage),'<STAGE>').replace(str(ROOT)+'/', '')
        report['commands'].append(dict(argv=[normalize(str(x)) for x in argv],exit_code=result.returncode,stdout=normalize(result.stdout),stderr=normalize(result.stderr)))
        require(result.returncode == 0, 'Command failed; see report.json: '+str(argv[0]))
        return result
    try:
        with tempfile.TemporaryDirectory(prefix='stage-',dir=output) as temporary:
            stage = Path(temporary)
            for item in index['records']:
                dest = stage/item['path']; dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(BASE/'inputs'/item['path'],dest)
            env = {**os.environ,'GIT_CEILING_DIRECTORIES':str(stage.parent)}
            for item in experiment['patches']:
                patch = PROJECT/item['path']
                result = subprocess.run(['git','apply','--no-index',str(patch)],cwd=stage,env=env,text=True,capture_output=True)
                require(result.returncode == 0, 'Patch application failed: '+result.stderr)
            cpp = run(['clang','-E','-P','-nostdinc','-undef','-x','assembler-with-cpp','-I',stage/'include','-I',stage/'arch/arm64/boot/dts/mediatek',stage/index['entry']],stage)
            require(not cpp.stderr.strip(), 'Preprocessor diagnostics must be reviewed')
            source = output/'douglas.pp.dts'; source.write_text(cpp.stdout)
            result = run([dtc,'-I','dts','-O','dtb','-o',output/'douglas.dtb',source],stage)
            require(not result.stderr.strip(), 'DTC diagnostics must be fixed; no warning suppression')
            artifact = inspect_header((output/'douglas.dtb').read_bytes())
            require(artifact['sha256'] == experiment['expected_artifact']['sha256'] and artifact['bytes'] == experiment['expected_artifact']['bytes'], 'DTB differs from reviewed experiment; inspect before changing the reference')
            def get(node,prop,kind='s'):
                return run([fdtget,'-t',kind,output/'douglas.dtb',node,prop],stage).stdout.strip()
            actual = dict(model=get('/','model'),compatible=get('/','compatible').split(),memory_reg=get('/memory@40000000','reg','x'),cpu_enable_methods=[get(f'/cpus/cpu@{n}','enable-method') for n in range(4)],cooling_cells=[get(f'/cpus/cpu@{n}','#cooling-cells','u') for n in range(4)])
            require(actual['model'] == 'Amazon Fire HD 8 (2017)' and actual['compatible'] == ['amazon,douglas','mediatek,mt8163'], 'Wrong compiled board identity')
            require(actual['memory_reg'] == '0 40000000 0 20000000', 'Donor memory declaration changed without review')
            require(actual['cpu_enable_methods'] == ['psci']*4 and actual['cooling_cells'] == ['2']*4, 'Unexpected compiled CPU declarations')
            if experiment.get('variant') in ('pmic-node-names', 'sysirq-node-name', 'rdma-node-name'):
                actual['pmic_children'] = {name: get('/soc/pwrap@1000d000/mt6323/'+name, 'compatible') for name in ['regulators', 'keys', 'audio-codec']}
                require(actual['pmic_children'] == {'regulators': 'mediatek,mt6323-regulator', 'keys': 'mediatek,mt6323-keys', 'audio-codec': 'mediatek,mt6397-codec'}, 'PMIC compatible changed')
            report.update(status='compiled',artifact=artifact,inspection=actual,dtc_version=subprocess.check_output([str(dtc),'--version'],text=True).strip(),kernel_compiled=False,device_tested=False,binding_validation='not passed; full ACK/donor binding context remains outstanding')
    finally:
        (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: DTB compiled without diagnostics and inspected:',report['artifact'])
    print('Preserved donor memory/PSCI declarations are UNVALIDATED for the physical tablet.')
    print('No kernel compilation, full binding validation, boot-image packing or device test.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment', choices=['baseline', 'pmic-node-names', 'sysirq-node-name', 'rdma-node-name'], default='baseline')
    parser.add_argument('--verify-only',action='store_true')
    parser.add_argument('--dtc',type=Path,default=ROOT/'work/dtb-tool/build/dtc')
    parser.add_argument('--fdtget',type=Path,default=ROOT/'work/dtb-tool/build/fdtget')
    args = parser.parse_args()
    index,experiment = verify_inputs(args.experiment)
    print(f'PASS: {len(index["records"])} locked DT input files and {len(experiment["patches"])} reviewed patches')
    if args.verify_only:
        return
    require(shutil.which('clang') is not None,'clang required')
    require(subprocess.check_output([str(args.dtc),'--version'],text=True).strip() == 'Version: DTC 1.8.1','Use pinned dtc 1.8.1')
    output = ROOT/'work/dtb-compile'/('repro' if args.experiment == 'baseline' else args.experiment)
    output.mkdir(parents=True,exist_ok=True)
    compile_tree(index,experiment,output,args.dtc,args.fdtget)


if __name__ == '__main__':
    main()
