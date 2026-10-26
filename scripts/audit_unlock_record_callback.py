#!/usr/bin/env python3
"""Exact-stock callback registration metadata, no record extraction/execution."""
import hashlib,json,struct
from audit_stock_fastboot_registration import ROOT,DIGEST


def main():
    raw=(ROOT/'out/ota-loader-inspection-659664620/lk.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=DIGEST:raise ValueError('Exact LK required')
    data=raw[512:];word=lambda x:struct.unpack_from('<I',data,x)[0]
    get_global=(word(0x3c0)+0x3ac)&0xffffffff
    set_global=(word(0x59c)+0x4f2)&0xffffffff
    got=(word(0x54c)+0x3e0)&0xffffffff
    slot=got+word(0x598);pointer=word(slot)
    if get_global!=set_global or pointer!=0x4bd00ab5:raise ValueError('Reviewed callback identity differs')
    windows=[(0x3a4,0x3be),(0x4dc,0x4f6),(0xab4,0xb2e)]
    print(json.dumps({'lk_sha256':DIGEST,'callback_global_payload_relative':get_global,
        'registration_pointer_slot_payload_offset':slot,'callback_handler_payload_offset':0xab4,
        'registration_branch_conditional':True,'record_data_offset_bytes':28,
        'record_length_field_offset_bytes':16,'copy_extent_is_minimum_of_record_and_requested':True,
        'reviewed_windows':[{'start':a,'end':b,'sha256':hashlib.sha256(data[a:b]).hexdigest()} for a,b in windows],
        'scope':'Selected static registration and in-memory named-record reader only',
        'backing_store_origin_resolved':False,'installed_record_retrieved':False,
        'physical_test_ready':False},indent=2))


if __name__=='__main__':main()
