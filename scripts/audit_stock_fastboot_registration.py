#!/usr/bin/env python3
"""Exact cached LK metadata-only registration audit; never executes firmware."""
import hashlib
import json
from pathlib import Path
import struct
from trace_lk_handoff import thumb_pc_string, thumb_call
ROOT=Path(__file__).resolve().parents[1]
DIGEST='4ca0cca7ae9af6e959dc848b9ca002624c62e1bb93c83c0ecc89bae8d2186b08'


def main():
    raw=(ROOT/'out/ota-loader-inspection-659664620/lk.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=DIGEST:raise ValueError('Exact stock LK required')
    data=raw[512:];entries=[]
    for offset in range(0x3f800,0x3fb00,2):
        if struct.unpack_from('<H',data,offset)[0]&0xff00!=0x4800:continue
        for add in range(offset+2,offset+12,2):
            try:ref=thumb_pc_string(data,offset,add)
            except (ValueError,UnicodeDecodeError,struct.error):continue
            for call in range(add+2,add+12,2):
                try:target=thumb_call(*struct.unpack_from('<HH',data,call),call)
                except ValueError:continue
                if target==0x3f454:
                    entries.append({'command_label':ref['text'],'label_load_offset':offset,
                                    'registration_call_offset':call})
    if len(entries)!=13:raise ValueError('Reviewed registration inventory changed')
    windows=[(0x3f454,0x3f48a),(0x3f978,0x3fae8)]
    print(json.dumps({'lk_sha256':DIGEST,'build':'659664620','payload_offset':512,
        'scope':'Selected registration region only; no whole-image absence or runtime acceptance claim',
        'registration_function_offset':0x3f454,'entries':entries,
        'reviewed_windows':[{'start':a,'end':b,'sha256':hashlib.sha256(data[a:b]).hexdigest()} for a,b in windows],
        'ram_boot_verified':False,'firmware_executed':False,'physical_test_ready':False},indent=2))


if __name__=='__main__':main()
