#!/usr/bin/env python3
"""Exact-stock record container read-path metadata, never reads device state."""
import hashlib,json,struct
from audit_stock_fastboot_registration import ROOT,DIGEST
from trace_lk_handoff import thumb_call


def main():
    raw=(ROOT/'out/ota-loader-inspection-659664620/lk.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=DIGEST:raise ValueError('Exact LK required')
    data=raw[512:];calls=[]
    for offset,target in [(0x3f0,0x3c370),(0x3c380,0x3aefc),(0x3af08,0x3ae7c),
                          (0x3af14,0x3a0bc),(0x3aeda,0x39ae8),(0x3aee6,0x39b98)]:
        if thumb_call(*struct.unpack_from('<HH',data,offset),offset)!=target:
            raise ValueError('Reviewed container read call differs')
        calls.append({'offset':offset,'target':target})
    windows=[(0x3e0,0x402),(0x3c370,0x3c396),(0x3aefc,0x3af24),(0x3ae7c,0x3aefc),(0x3a0bc,0x3a124)]
    print(json.dumps({'lk_sha256':DIGEST,'checked_calls':calls,
        'reviewed_loader_arguments':{'controller':0,'start_block':0,'block_count':30,'selector':2},
        'selector_register_index':179,'selector_low_bits_mask':7,
        'wrapper_checks_selector_return_before_read':False,
        'reviewed_windows':[{'start':a,'end':b,'sha256':hashlib.sha256(data[a:b]).hexdigest()} for a,b in windows],
        'scope':'Static argument/call/selector path only; exact hardware region and contents unobserved',
        'actual_region_identity_verified':False,'record_contents_read':False,'physical_test_ready':False},indent=2))


if __name__=='__main__':main()
