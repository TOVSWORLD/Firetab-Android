#!/usr/bin/env python3
"""Verify/hash ignored cached original DA stages; never execute or patch them."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request
from probe_recovery_agent_records import Ranges, REV
from audit_recovery_entry_escrow import functions, calls

ROOT=Path(__file__).resolve().parents[1]


def stage_digest(raw, size, digest, signature_size):
    if len(raw)!=size or hashlib.sha256(raw).hexdigest()!=digest:
        raise ValueError('Original stage identity mismatch')
    if not 0 < signature_size < size:
        raise ValueError('Invalid declared signature length')
    return {'bytes':len(raw),'sha256':digest,'declared_signature_bytes':signature_size,
            'declared_signature_sha256':hashlib.sha256(raw[-signature_size:]).hexdigest(),
            'declared_code_sha256':hashlib.sha256(raw[:-signature_size]).hexdigest()}


def patch_scope(source):
    _,funcs=functions(source)
    nodes={name:calls(funcs[name]) for name in ('patch_da2','patch_da2_readmem')}
    observed=any(c['callee']=='self.patch_da2_readmem' for c in nodes['patch_da2'])
    if not observed:
        raise ValueError('Expected extension source changed; re-audit')
    return {'audited_call_sites':nodes,'patch_function_executed_by_this_audit':False,
            'patches_applied_to_cached_stages':False,'uploaded_stage_identity_verified':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download-original-stages',action='store_true')
    args=parser.parse_args()
    expected=json.loads((ROOT/'evidence/recovery-stage-identity/report.json').read_text())
    if expected['revision'] != REV:
        raise ValueError('Unexpected source revision')
    if args.download_original_stages:
        reader=Ranges()
        item={'path':'mtkclient/Loader/MTK_DA_V5.bin','size':22483280}
        for entry in expected['stages']:
            if (entry['stage'],entry['file_offset'],entry['bytes']) not in (
                    (1,17837176,65352),(2,17902536,254872)):
                raise ValueError('Unexpected original stage extent')
            raw=reader.read(item,entry['file_offset'],entry['bytes'])
            stage_digest(raw,entry['bytes'],entry['sha256'],entry['declared_signature_bytes'])
            target=ROOT/f"out/recovery-entry/v5-stage{entry['stage']}.bin"
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        meta=expected['extension_source']
        name='mtkclient/Library/DA/legacy/extension/legacy.py'
        url=f'https://raw.githubusercontent.com/bkerler/mtkclient/{REV}/{name}'
        if meta['url'] != url or meta['path'] != name or meta['bytes'] != 22383:
            raise ValueError('Unexpected extension source')
        with urllib.request.urlopen(url,timeout=25) as response:
            raw=response.read(22384)
        if len(raw)!=meta['bytes'] or hashlib.sha256(raw).hexdigest()!=meta['sha256']:
            raise ValueError('Extension download identity mismatch')
        target=ROOT/'out/recovery-entry/mtkclient'/name
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    stages=[]
    for item in expected['stages']:
        data=(ROOT/f"out/recovery-entry/v5-stage{item['stage']}.bin").read_bytes()
        stages.append({'stage':item['stage'],**stage_digest(data,item['bytes'],item['sha256'],
                                                         item['declared_signature_bytes'])})
    meta=expected['extension_source']
    source=(ROOT/'out/recovery-entry/mtkclient'/meta['path']).read_bytes()
    if len(source)!=meta['bytes'] or hashlib.sha256(source).hexdigest()!=meta['sha256']:
        raise ValueError('Extension source identity mismatch')
    print(json.dumps({'original_stage_hash_checks_pass':True,'stages':stages,
                     'extension':patch_scope(source.decode()),'vendor_signature_verified':False,
                     'physical_test_ready':False},indent=2))


if __name__=='__main__':
    main()
