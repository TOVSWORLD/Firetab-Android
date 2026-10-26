#!/usr/bin/env python3
"""Exact-stock metadata-only limited-unlock validation boundary."""
import hashlib,json,struct
from audit_stock_fastboot_registration import ROOT,DIGEST
from trace_lk_handoff import thumb_call,thumb_pc_string


def main():
    raw=(ROOT/'out/ota-loader-inspection-659664620/lk.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=DIGEST:raise ValueError('Exact LK required')
    data=raw[512:];calls=[]
    for offset,target in [(0x20644,0x20f80),(0x2067a,0x7b10),(0x20698,0x11438),
                          (0x206dc,0x135ac),(0x206f8,0x20f34)]:
        if thumb_call(*struct.unpack_from('<HH',data,offset),offset)!=target:
            raise ValueError('Reviewed validator call differs')
        calls.append({'offset':offset,'target':target})
    name=thumb_pc_string(data,0x2074e,0x20752)['text']
    if name!='amzn_verify_limited_unlock':raise ValueError('Validator label differs')
    windows=[(0x2062c,0x206a8),(0x206b4,0x20708),(0x2074c,0x20778)]
    print(json.dumps({'lk_sha256':DIGEST,'diagnostic_function_label':name,'checked_calls':calls,
        'reviewed_signature_extent_bytes':256,'reviewed_transform_result_required_bytes':256,
        'diagnostic_identifies_rsa_decryption':True,'verification_success_result_checked_equals_one':True,
        'reviewed_windows':[{'start':a,'end':b,'sha256':hashlib.sha256(data[a:b]).hexdigest()} for a,b in windows],
        'scope':'Selected static limited-unlock validation only; no input/key export or execution',
        'key_provenance_resolved':False,'credential_available':False,'physical_test_ready':False},indent=2))


if __name__=='__main__':main()
