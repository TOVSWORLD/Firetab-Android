#!/usr/bin/env python3
"""Runnable synthetic-only observation integration. No external callback or device inputs."""
import argparse
import hashlib
import json
from pathlib import Path
from offline_observation_session import OfflineObservationSession
from offline_query_frame import validate_frame
from offline_mode_evidence import decode_mode_reply
ROOT=Path(__file__).resolve().parents[1]
COMPONENTS=('synthetic_observation_package.py','offline_observation_session.py',
            'offline_query_frame.py','offline_mode_evidence.py','offline_security_observation.py')


def run_case(mode):
    if mode not in ('success','bad-echo','late'):
        raise ValueError('Built-in synthetic scenario required')
    now=[0.0];calls=[]
    # Invented symbolic commands and replies, not the MediaTek wire protocol.
    commands={'hardware_code':b'H','hardware_versions':b'V','target_config':b'S'}
    sizes={'hardware_code':4,'hardware_versions':8,'target_config':6}
    def query(name,timeout_ms):
        calls.append(name)
        now[0]+=2 if mode=='late' else 0.01
        command=commands[name]
        return validate_frame(command=command,echo=b'?' if mode=='bad-echo' else command,
                              payload=bytes(sizes[name]),expected_bytes=sizes[name])
    session=OfflineObservationSession(query,budget_seconds=1,clock=lambda:now[0])
    result=None;error=None;mode_result=None
    try:
        result=session.collect()
        mode_result=decode_mode_reply(query_byte=b'M',reply=b'M')
    except (ValueError,TimeoutError) as exc:
        error=type(exc).__name__
    accepted=result is not None
    expected=(mode=='success')
    return {'synthetic_only':True,'scenario':mode,'scenario_passed':accepted==expected,
            'observation_decoded':accepted,'session_state':session.state,'error_class':error,
            'symbolic_queries':calls,'simulated_seconds':now[0],
            'observation':result,'mode_evidence':mode_result,
            'source_sha256':{name:hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest() for name in COMPONENTS},
            'native_code_loaded':False,'device_access_performed':False,
            'bootstrap_authorized':False,'physical_test_ready':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=('success','bad-echo','late'),required=True)
    result=run_case(parser.parse_args().mode)
    print(json.dumps(result,indent=2))
    return 0 if result['scenario_passed'] else 1


if __name__=='__main__':
    raise SystemExit(main())
