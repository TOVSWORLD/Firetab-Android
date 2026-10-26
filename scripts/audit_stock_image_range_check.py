#!/usr/bin/env python3
"""Metadata-only receipt for exact-stock early image range check."""
import hashlib
import json
import struct
from audit_stock_fastboot_registration import ROOT,DIGEST
from trace_lk_handoff import thumb_pc_string,thumb_call


def main():
    raw=(ROOT/'out/ota-loader-inspection-659664620/lk.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=DIGEST:raise ValueError('Exact stock LK required')
    data=raw[512:]
    if thumb_call(*struct.unpack_from('<HH',data,0x24d1e),0x24d1e)!=0x244c0:
        raise ValueError('Early check caller differs')
    message=thumb_pc_string(data,0x2450a,0x24510)
    if not message['text'].startswith('Kernel size '):raise ValueError('Reviewed diagnostic differs')
    windows=[(0x244c0,0x2451c),(0x24d10,0x24d28)]
    print(json.dumps({'lk_sha256':DIGEST,'check_offset':0x244c0,
        'caller_offset':0x24d1e,'diagnostic_reference_offset':int(message['target_offset'],16),
        'reviewed_length_limit_bytes':16777216,'length_limit_unsigned_strictly_greater_rejected':True,
        'unsigned_address_addition_carry_rejected':True,'check_is_cryptographic_verifier':False,
        'caller_rejects_nonzero_check_result':True,
        'complete_range_policy_modeled':False,'length_global_producer_resolved':False,
        'reviewed_windows':[{'start':a,'end':b,'sha256':hashlib.sha256(data[a:b]).hexdigest()} for a,b in windows],
        'scope':'Manual static instruction review plus hash/call/reference checks; no firmware execution',
        'physical_test_ready':False},indent=2))


if __name__=='__main__':main()
