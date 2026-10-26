#!/usr/bin/env python3
"""Exact-stock selected verification call/status boundary metadata only."""
import hashlib,json,struct
from audit_stock_fastboot_registration import ROOT,DIGEST
from trace_lk_handoff import thumb_call,thumb_pc_string


def main():
    raw=(ROOT/'out/ota-loader-inspection-659664620/lk.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=DIGEST:raise ValueError('Exact LK required')
    data=raw[512:];calls=[]
    for offset,target in [(0x24df8,0x205ec),(0x24e1c,0x1cf0c),(0x1cf0e,0x1ce4c),
                          (0x1ce7e,0x1cf24),(0x1cea2,0x1cf24)]:
        if thumb_call(*struct.unpack_from('<HH',data,offset),offset)!=target:
            raise ValueError('Reviewed security call differs')
        calls.append({'offset':offset,'target':target})
    failure=thumb_pc_string(data,0x24fc0,0x24fc2)
    if failure['text'].strip()!='Failed to verify image':raise ValueError('Failure reference changed')
    windows=[(0x24df8,0x24e36),(0x24fc0,0x24fce),(0x1cf0c,0x1cf1e),(0x1ce4c,0x1ceec)]
    print(json.dumps({'lk_sha256':DIGEST,'checked_calls':calls,
        'verification_result_mask':9,'wrapper_accepts_any_mask_bit':True,
        'zero_wrapper_result_reaches_verification_failure':True,'failure_return_signed':-13,
        'selector_alternate_branch_offset':0x24f20,
        'reviewed_windows':[{'start':a,'end':b,'sha256':hashlib.sha256(data[a:b]).hexdigest()} for a,b in windows],
        'scope':'Selected static call/status mapping; not complete signature/key/rollback policy',
        'trusted_keys_resolved':False,'installed_selector_state_verified':False,
        'unsigned_image_acceptance_verified':False,'physical_test_ready':False},indent=2))


if __name__=='__main__':main()
