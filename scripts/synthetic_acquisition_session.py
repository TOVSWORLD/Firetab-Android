#!/usr/bin/env python3
"""Synthetic-only host integration. No device/native/bootstrap or external worker inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
from offline_deadline_reader import OfflineDeadlineReader
from offline_escrow_capture import capture_region
from offline_legacy_read_binding import OfflineLegacyReadBinding, REGION_IDS
from offline_worker_supervisor import supervise_worker
from synthetic_escrow_fixture import image
from verify_offline_escrow import verify_region

ROOT=Path(__file__).resolve().parents[1]
COMPONENTS=('synthetic_acquisition_session.py','synthetic_escrow_fixture.py','offline_deadline_reader.py',
            'offline_escrow_capture.py','offline_legacy_read_binding.py','offline_worker_supervisor.py',
            'verify_offline_escrow.py')


def fixtures():
    return {'user':bytes(image()),'boot1':b'A'*4096,'boot2':b'B'*4096}


def provenance():
    result={'components':{name:hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest() for name in COMPONENTS}}
    refs=('evidence/offline-readback-adapter/report.json','evidence/offline-read-binding/contract.json',
          'evidence/libusb-static-candidate/static-result.json')
    result['reference_metadata']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in refs}
    adapter=json.loads((ROOT/refs[0]).read_text());binding=json.loads((ROOT/refs[1]).read_text())
    native=json.loads((ROOT/refs[2]).read_text())
    if (adapter['physical_test_ready'] or adapter['upstream_helper_imported_or_executed'] or
        adapter['actual_readback_verified'] or native['native_code_loaded'] or binding['physical_test_ready']
        or not adapter['strict_read_region_ack_guard_prepared'] or binding['ordinary_region_ids']!=REGION_IDS
        or adapter['library_sha256']!=native['static_library']['sha256']):
        raise ValueError('Reference metadata changed; explicit review required')
    return result


def _capture_case(directory, mode):
    data=fixtures();sizes={name:len(raw) for name,raw in data.items()}
    def readflash(**options):
        if mode=='short':return b'x'
        source=data[options['parttype']][options['addr']:options['addr']+options['length']]
        position=0
        def packet(size,timeout):
            nonlocal position
            if mode=='stall':
                while True:time.sleep(0.02)
            take=min(size,777,len(source)-position)
            result=source[position:position+take];position+=take
            return result
        reader=OfflineDeadlineReader(packet,packet_bytes=1024,deadline_seconds=1)
        return reader.read_exact(options['length'])
    binding=OfflineLegacyReadBinding(sizes,lambda:dict(sizes),
        lambda parttype,length:(length,REGION_IDS[parttype]),lambda region:True,readflash,
        backend_kind='legacy',storage_kind='emmc',iot=False,sector_bytes=512)
    records={name:capture_region(directory/(name+'.bin'),name,len(raw),binding.select_region,
                binding.read_chunk,4096) for name,raw in data.items()}
    (directory/'session.json').write_text(json.dumps({'synthetic_only':True,
        'provenance':provenance(),'captures':records},indent=2)+'\n')


def synthetic_success(directory):
    _capture_case(directory,'success')


def synthetic_short(directory):
    _capture_case(directory,'short')


def synthetic_stall(directory):
    _capture_case(directory,'stall')


def validate_session(directory, results=None):
    manifest=directory/'session.json'
    if not manifest.is_file() or manifest.is_symlink() or manifest.stat().st_size>65536:return False
    record=json.loads(manifest.read_text())
    if record.get('synthetic_only') is not True or record.get('provenance')!=provenance():return False
    if set(record['captures'])!=set(REGION_IDS):return False
    for name,data in fixtures().items():
        digest=hashlib.sha256(data).hexdigest();capture=record['captures'][name]
        if capture['sha256']!=digest or capture['bytes']!=len(data) or capture['physical_test_ready']:return False
        checked=verify_region(directory/(name+'.bin'),len(data),digest,512 if name=='user' else None)
        if results is not None:results[name]={'bytes':len(data),'sha256':digest,'checks':checked}
    return True


def run_case(output, mode, timeout_seconds):
    if mode not in ('success','short','stall'):raise ValueError('Synthetic fixture mode only')
    output=Path(output).resolve()
    if output.exists() or not output.is_relative_to((ROOT/'out').resolve()):
        raise ValueError('Fresh ignored out/ directory required')
    source=provenance();output.mkdir(parents=True)
    workers={'success':synthetic_success,'short':synthetic_short,'stall':synthetic_stall}
    checked={}
    outcome=supervise_worker(workers[mode],lambda p:validate_session(p,checked),output,timeout_seconds=timeout_seconds)
    accepted=outcome.summary['worker_completed'] and outcome.summary['parent_validation_passed']
    if mode=='success':passed=accepted
    elif mode=='short':passed=(not accepted and not outcome.summary['timed_out'] and
        outcome.summary.get('failure')=='worker_failed_or_no_completion')
    else:passed=not accepted and outcome.summary['timed_out'] and outcome.summary['worker_reaped']
    report={'scope':'Synthetic-only end-to-end host integration; no native/helper/device transport',
        'mode':mode,'scenario_passed':passed,'host_session_accepted':accepted,
        'supervision':outcome.summary,'provenance':source,
        'validated_capture_metadata':checked if accepted else {},
        'project_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'working_tree_clean':not bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),
        'synthetic_fixture_bytes':sum(len(x) for x in fixtures().values()),
        'quarantine_retained':outcome.quarantine_directory is not None,
        'helper_code_executed':False,'native_code_loaded':False,'device_accessed':False,
        'bootstrap_executed':False,'protocol_checksum_verified':False,
        'live_binding_qualified':False,'restore_qualified':False,'physical_test_ready':False}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--mode',choices=('success','short','stall'),default='success')
    parser.add_argument('--timeout-seconds',type=float,default=5)
    args=parser.parse_args();report=run_case(args.output,args.mode,args.timeout_seconds)
    print(json.dumps(report,indent=2))
    return 0 if report['scenario_passed'] else 1


if __name__=='__main__':
    raise SystemExit(main())
