#!/usr/bin/env python3
"""Validate retained generic runtime proof; never promote physical qualification."""
import hashlib
import json
from pathlib import Path
import re
from check_diagnostic_commandline import check

ROOT=Path(__file__).resolve().parents[1]


def verify(record, config):
    check(config,'generic-force')
    run=record['runtime']
    if (record['ci_run_id']!=40279916842 or
        record['source_revision']!='710edcfdfa7c3f003ededf8e40643fde4707bbb1' or
        record['ack_revision']!='d9318bdb4c34e8b2d997b4f67ced56b120b22b87'):
        raise ValueError('Unexpected executed source/run provenance')
    if not run['passed'] or not run['forced_argument_test']['forced_limits_observed']:
        raise ValueError('Executed argument-selection proof did not pass')
    if hashlib.sha256(config.encode()).hexdigest()!=run['config_sha256']:
        raise ValueError('Retained resolved config identity mismatch')
    incoming=run['command'][run['command'].index('-append')+1].split()
    if [x for x in incoming if x.startswith(('nr_cpus=','maxcpus='))]!=['nr_cpus=4','maxcpus=3']:
        raise ValueError('Contradictory incoming arguments missing')
    verdicts=run['cpu_contract']['verdicts']
    if any(verdicts[key]!='valid' for key in ('LIMIT_NR_CPUS','LIMIT_MAXCPUS')):
        raise ValueError('Actual verdicts do not establish forced limits')
    for field in ('config_sha256','kernel_sha256','initramfs_sha256','console_sha256'):
        if not re.fullmatch('[0-9a-f]{64}',run[field]):
            raise ValueError('Missing exact artifact/log digest')
    if (record['physical_test_ready'] or run['douglas_boot_tested'] or run['hardware_tested']
        or run['firmware_packed'] or run['cpu_contract']['douglas_boot_qualified']):
        raise ValueError('Generic result must not qualify tablet boot/hardware')
    return {'executed_generic_argument_selection_verified':True,
            'primary_only_contract_observed':run['cpu_contract']['primary_only_contract_observed'],
            'ci_run_id':record['ci_run_id'],'physical_test_ready':False}


def main():
    folder=ROOT/'evidence/generic-forced-arguments'
    print(json.dumps(verify(json.loads((folder/'runtime-result.json').read_text()),
                            (folder/'resolved.config').read_text()),indent=2))


if __name__=='__main__':
    main()
