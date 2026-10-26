#!/usr/bin/env python3
"""Exact-stock selector input metadata; no credential retrieval or execution."""
import hashlib,json,struct
from audit_stock_fastboot_registration import ROOT,DIGEST
from trace_lk_handoff import thumb_call,thumb_pc_string


def main():
    raw=(ROOT/'out/ota-loader-inspection-659664620/lk.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=DIGEST:raise ValueError('Exact LK required')
    data=raw[512:];reference=thumb_pc_string(data,0x205fc,0x20604)
    if reference['text']!='unlock_code':raise ValueError('Input name differs')
    calls=[]
    for offset,target in [(0x20606,0x3a4),(0x20618,0x2080c),(0x1cebc,0x205ec),(0x1cede,0x205ec)]:
        if thumb_call(*struct.unpack_from('<HH',data,offset),offset)!=target:
            raise ValueError('Reviewed selector call differs')
        calls.append({'offset':offset,'target':target})
    windows=[(0x205ec,0x20628),(0x2080c,0x20814),(0x3a4,0x3be),(0x1ceaa,0x1ceec)]
    print(json.dumps({'lk_sha256':DIGEST,'selector_input_field_name':reference['text'],
        'requested_input_buffer_bytes':256,'checked_calls':calls,
        'retrieval_uses_runtime_callback':True,'retrieval_storage_origin_resolved':False,
        'installed_input_value_retrieved':False,'validation_algorithm_resolved':False,
        'reviewed_windows':[{'start':a,'end':b,'sha256':hashlib.sha256(data[a:b]).hexdigest()} for a,b in windows],
        'scope':'Static field-name/call boundary only; no credential bytes or execution',
        'physical_test_ready':False},indent=2))


if __name__=='__main__':main()
