#!/usr/bin/env python3
"""Metadata-only selected image source audit; no firmware execution."""
import hashlib
import json
import struct
from audit_stock_fastboot_registration import ROOT,DIGEST
from trace_lk_handoff import thumb_call,thumb_pc_string


def main():
    raw=(ROOT/'out/ota-loader-inspection-659664620/lk.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=DIGEST:raise ValueError('Exact stock LK required')
    data=raw[512:];calls=[]
    for offset,target in [(0x2477a,0x35da8),(0x2478a,0x35c40),(0x247ac,0x35c40),
                          (0x24cf4,0x35da8),(0x24d04,0x35c40),(0x24d1e,0x244c0)]:
        if thumb_call(*struct.unpack_from('<HH',data,offset),offset)!=target:
            raise ValueError('Reviewed image source call differs')
        calls.append({'offset':offset,'target':target})
    exclusions=[thumb_pc_string(data,a,b)['text'] for a,b in [(0x35c40,0x35c48),(0x35c52,0x35c56)]]
    if exclusions!=['PRELOADER','preloader']:raise ValueError('Named lookup branches differ')
    windows=[(0x24770,0x247ee),(0x24ce8,0x24d70),(0x35bc4,0x35c24),(0x35c40,0x35c7a),(0x35da8,0x35dc6)]
    print(json.dumps({'lk_sha256':DIGEST,'scope':'Selected named-table/device-callback paths only',
        'checked_calls':calls,'name_lookup_special_cases':exclusions,
        'header_callback_call_offset':0x247de,'image_callback_call_offset':0x24d6e,
        'callback_slot_bytes':16,'named_record_extent_bytes':20,
        'reviewed_windows':[{'start':a,'end':b,'sha256':hashlib.sha256(data[a:b]).hexdigest()} for a,b in windows],
        'callback_implementation_resolved':False,'signature_policy_resolved':False,
        'downloaded_image_handoff_verified':False,'physical_test_ready':False},indent=2))


if __name__=='__main__':main()
