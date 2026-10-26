#!/usr/bin/env python3
"""Metadata-only exact-stock handler pointer resolution, no firmware execution."""
import hashlib
import json
from pathlib import Path
import struct
from audit_stock_fastboot_registration import DIGEST, ROOT


def main():
    raw=(ROOT/'out/ota-loader-inspection-659664620/lk.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=DIGEST:raise ValueError('Exact stock LK required')
    data=raw[512:]
    def word(offset):return struct.unpack_from('<I',data,offset)[0]
    got=(word(0x3fbbc)+0x3f94c)&0xffffffff
    entries=[]
    for name,pool,expected in [('continue',0x3fc18,0x3fd90),('reboot',0x3fc20,0x40010),
                               ('reboot-bootloader',0x3fc28,0x40028)]:
        slot=got+word(pool);pointer=word(slot)
        offset=(pointer & ~1)-0x4bd00000
        if offset!=expected or not pointer&1:raise ValueError('Reviewed Thumb handler differs')
        entries.append({'label':name,'pointer_slot_payload_offset':slot,'handler_payload_offset':offset})
    windows=[(0x3f77c,0x3f82a),(0x20858,0x20934),(0x3fd90,0x3fde4),(0x40010,0x40042)]
    print(json.dumps({'lk_sha256':DIGEST,'scope':'Static selected handler/dispatcher paths only',
        'linked_address_base_assumption':'0x4bd00000; not runtime placement proof',
        'handlers':entries,'reviewed_windows':[{'start':a,'end':b,'sha256':hashlib.sha256(data[a:b]).hexdigest()} for a,b in windows],
        'pre_dispatch_filter_call_offset':0x3f780,'pre_dispatch_filter_target_offset':0x20858,
        'indirect_handler_call_offset':0x3f7f6,
        'registration_flag_semantics_resolved':False,'runtime_permission_verified':False,
        'ram_boot_verified':False,'physical_test_ready':False},indent=2))


if __name__=='__main__':main()
