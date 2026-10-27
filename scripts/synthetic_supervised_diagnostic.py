#!/usr/bin/env python3
"""Built-in host synthetic framed sessions only; no device or firmware inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import time
from injected_diagnostic_capture import capture_injected
from offline_diagnostic_dispatcher import OfflineDiagnosticDispatcher
from offline_worker_supervisor import supervise_worker
ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ('synthetic_supervised_diagnostic.py','injected_diagnostic_capture.py',
              'offline_diagnostic_dispatcher.py','offline_diagnostic_protocol.py','offline_worker_supervisor.py')


def hashes():
    return {n:hashlib.sha256((ROOT/'scripts'/n).read_bytes()).hexdigest() for n in COMPONENTS}


class SyntheticBackend:
    def __init__(self, stall):
        self.stall=stall;self.image=bytearray(1080);self.buffer=bytearray()
        self.agent=OfflineDiagnosticDispatcher(self.call,lambda o,n:bytes(self.image[o:o+n]))
    def call(self): self.image[48:52]=b'1KTF';return 0
    def validate_active(self, interface):return True
    def claim(self, interface):return True
    def block(self, where):
        if self.stall==where:
            while True: time.sleep(0.02)
    def write(self, data, *, timeout_ms):
        self.block('write');self.buffer.extend(self.agent.dispatch(data));return len(data)
    def read(self, count, *, timeout_ms):
        self.block('read');result=bytes(self.buffer[:count]);del self.buffer[:count];return result
    def release(self, interface):self.block('cleanup');return True
    def dispose(self):return True


def collect(directory, mode):
    result=capture_injected(SyntheticBackend(mode),interface=0,clock=time.monotonic)
    snapshot=result.pop('snapshot');(directory/'snapshot.bin').write_bytes(snapshot)
    (directory/'result.json').write_text(json.dumps(dict(synthetic_only=True,source_sha256=hashes(),
        snapshot_sha256=hashlib.sha256(snapshot).hexdigest(),capture=result),sort_keys=True))


def success(directory):collect(directory,None)
def write_stall(directory):collect(directory,'write')
def read_stall(directory):collect(directory,'read')
def cleanup_stall(directory):collect(directory,'cleanup')


def validate(directory):
    manifest=directory/'result.json';snapshot=directory/'snapshot.bin'
    if any(p.is_symlink() or not p.is_file() for p in (manifest,snapshot)):return False
    if manifest.stat().st_size>8192 or snapshot.stat().st_size!=1080:return False
    value=json.loads(manifest.read_text());data=snapshot.read_bytes()
    expected=bytearray(1080);expected[48:52]=b'1KTF'
    return (value['synthetic_only'] is True and value['source_sha256']==hashes()
        and value['snapshot_sha256']==hashlib.sha256(data).hexdigest() and data==bytes(expected)
        and value['capture']['runtime_execution_verified'] is False
        and value['capture']['acquisition_origin_verified'] is False
        and value['capture']['physical_test_ready'] is False)


def run_case(mode):
    workers={'success':success,'write-stall':write_stall,'read-stall':read_stall,'cleanup-stall':cleanup_stall}
    if mode not in workers:raise ValueError('Built-in synthetic scenario required')
    with tempfile.TemporaryDirectory(prefix='synthetic-diagnostic-') as root:
        outcome=supervise_worker(workers[mode],validate,root,timeout_seconds=1)
        accepted=outcome.summary['parent_validation_passed']
        passed=(accepted and not outcome.summary['timed_out']) if mode=='success' else (
            not accepted and outcome.summary['timed_out'] and outcome.summary['worker_reaped'])
        result=dict(synthetic_only=True,scenario=mode,scenario_passed=passed,supervisor=outcome.summary,
                    source_sha256=hashes(),forced_stop_confirms_device_cleanup=False,
                    firmware_executed=False,device_accessed=False,physical_test_ready=False)
        if outcome.quarantine_directory is not None:shutil.rmtree(outcome.quarantine_directory)
        return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=('success','write-stall','read-stall','cleanup-stall'),required=True)
    result=run_case(parser.parse_args().mode);print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['scenario_passed'] else 1)
