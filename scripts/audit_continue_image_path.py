#!/usr/bin/env python3
"""Exact-stock selected continue-to-header path metadata; no firmware execution."""
import hashlib
import json
import struct
from audit_stock_fastboot_registration import ROOT,DIGEST
from trace_lk_handoff import thumb_pc_string,thumb_call


def main():
    raw=(ROOT/'out/ota-loader-inspection-659664620/lk.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=DIGEST:raise ValueError('Exact LK required')
    data=raw[512:]
    word=lambda offset:struct.unpack_from('<I',data,offset)[0]
    got=0x761f4
    cleared=word(got+word(0x3fde8));selector=word(got+word(0x3ef58))
    if cleared!=selector:raise ValueError('Selector identity differs')
    zero_case=0x3ebc6+2*struct.unpack_from('<H',data,0x3ebc6)[0]
    if zero_case!=0x3ef4e:raise ValueError('Selected table branch differs')
    labels=[thumb_pc_string(data,a,b) for a,b in [(0x3ee46,0x3ee50),(0x3ee68,0x3ee6a)]]
    if any(x['text']!='boot' for x in labels):raise ValueError('Selected image labels differ')
    calls=[]
    for offset,target in [(0x3ee52,0x24770),(0x3ee6c,0x24ce8)]:
        actual=thumb_call(*struct.unpack_from('<HH',data,offset),offset)
        if actual!=target:raise ValueError('Selected image call differs')
        calls.append({'offset':offset,'target':target})
    windows=[(0x3fd90,0x3fde4),(0x3eb98,0x3ebc6),(0x3ebc6,0x3ebc8),
             (0x3ef4e,0x3ef54),(0x3ee46,0x3ee8e)]
    print(json.dumps({'lk_sha256':DIGEST,'scope':'Selected static continue mode-zero path only',
        'shared_selector_linked_address':hex(selector),'mode_zero_table_target':zero_case,
        'image_label_references':labels,'checked_calls':calls,
        'reviewed_windows':[{'start':a,'end':b,'sha256':hashlib.sha256(data[a:b]).hexdigest()} for a,b in windows],
        'downloaded_image_handoff_verified':False,'signature_policy_resolved':False,
        'firmware_executed':False,'physical_test_ready':False},indent=2))


if __name__=='__main__':main()
