#!/usr/bin/env python3
"""Built-in synthetic processes only; no native/device/command inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import time
from offline_observation_adapter import OfflineObservationAdapter
from offline_worker_supervisor import supervise_worker
ROOT=Path(__file__).resolve().parents[1]
COMPONENTS=('synthetic_supervised_observation.py','offline_observation_adapter.py',
            'offline_observation_session.py','offline_query_frame.py',
            'offline_security_observation.py','offline_worker_supervisor.py')


def hashes():
    return {name:hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest() for name in COMPONENTS}


class SyntheticBackend:
    def __init__(self, stall):self.stall=stall;self.command=None;self.echo=False
    def validate_active(self,interface):return True
    def claim(self,interface):return True
    def write(self,data,timeout_ms):
        if self.stall=='io':
            while True:time.sleep(0.02)
        self.command=data;self.echo=True;return len(data)
    def read(self,size,timeout_ms):
        if self.echo:self.echo=False;return self.command
        return bytes(size)
    def release(self,interface):
        if self.stall=='cleanup':
            while True:time.sleep(0.02)
        return True
    def dispose(self):return True


def _collect(directory, stall):
    result=OfflineObservationAdapter(SyntheticBackend(stall),interface=0,commands={
        'hardware_code':b'H','hardware_versions':b'V','target_config':b'S'}).collect()
    (directory/'result.json').write_text(json.dumps({'synthetic_only':True,
        'source_sha256':hashes(),'adapter':result},sort_keys=True))


def success(directory):_collect(directory,None)
def io_stall(directory):_collect(directory,'io')
def cleanup_stall(directory):_collect(directory,'cleanup')


def validate(directory):
    path=directory/'result.json'
    if path.is_symlink() or not path.is_file() or path.stat().st_size>8192:return False
    value=json.loads(path.read_text())
    result=value['adapter']
    return (value['synthetic_only'] is True and value['source_sha256']==hashes()
            and result['accepted_offline_observation'] is True
            and result['cleanup_confirmed'] is True and result['error_class'] is None
            and result['bootstrap_authorized'] is False and result['physical_test_ready'] is False)


def run_case(mode):
    workers={'success':success,'io-stall':io_stall,'cleanup-stall':cleanup_stall}
    if mode not in workers:raise ValueError('Built-in synthetic scenario required')
    with tempfile.TemporaryDirectory(prefix='synthetic-observation-') as root:
        outcome=supervise_worker(workers[mode],validate,root,timeout_seconds=1)
        accepted=outcome.summary['parent_validation_passed']
        passed=(accepted and not outcome.summary['timed_out']) if mode=='success' else (
            not accepted and outcome.summary['timed_out'] and outcome.summary['worker_reaped'])
        result={'synthetic_only':True,'scenario':mode,'scenario_passed':passed,
                'supervisor':outcome.summary,'source_sha256':hashes(),
                'device_access_performed':False,'physical_test_ready':False}
        if outcome.quarantine_directory is not None:shutil.rmtree(outcome.quarantine_directory)
        return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=('success','io-stall','cleanup-stall'),required=True)
    result=run_case(parser.parse_args().mode)
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['scenario_passed'] else 1)
