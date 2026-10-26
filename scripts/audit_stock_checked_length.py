#!/usr/bin/env python3
"""Model reviewed normal non-overflow size arithmetic; not a firmware emulator."""
import hashlib
import json
import struct
from pathlib import Path
from audit_stock_fastboot_registration import ROOT,DIGEST


def checked_length(kernel,ramdisk,page):
    if any(type(v) is not int or v<0 for v in (kernel,ramdisk,page)):
        raise ValueError('Nonnegative integer extents required')
    if not 512<=page<=65536 or page & (page-1):raise ValueError('Reviewed power-of-two page required')
    if kernel==0 or any(v+page-1>0xffffffff for v in (kernel,ramdisk)):
        raise ValueError('Zero kernel or overflowing rounding is outside model')
    total=page*((kernel+page-1)//page+(ramdisk+page-1)//page+2)
    if total>0xffffffff:raise ValueError('Overflowing product outside model')
    return total


def main():
    raw=(ROOT/'out/ota-loader-inspection-659664620/lk.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=DIGEST:raise ValueError('Exact LK required')
    data=raw[512:];word=lambda offset:struct.unpack_from('<I',data,offset)[0]
    producer=word(0x761f4+word(0x249b0));consumer=word(0x761f4+word(0x24ff0))
    if producer!=consumer:raise ValueError('Producer and consumer global differ')
    boot=ROOT/'out/stock-ota-douglas-659664620/boot.img'
    expected='8982fa50193acc764be69ee51027ee92e83614cee4b8235b07439d1f9e2db363'
    if hashlib.sha256(boot.read_bytes()).hexdigest()!=expected:raise ValueError('Exact cached stock boot required')
    with boot.open('rb') as stream:header=stream.read(608)
    if header[:8]!=b'ANDROID!':raise ValueError('Boot header required')
    kernel=struct.unpack_from('<I',header,8)[0]
    ramdisk=struct.unpack_from('<I',header,16)[0];page=struct.unpack_from('<I',header,36)[0]
    total=checked_length(kernel,ramdisk,page)
    print(json.dumps({'lk_sha256':DIGEST,'boot_sha256':expected,'shared_length_global_linked_address':hex(producer),
        'header_kernel_bytes':kernel,'header_ramdisk_bytes':ramdisk,'header_page_bytes':page,
        'modeled_checked_extent_bytes':total,'within_reviewed_16mib_length_check':total<=16777216,
        'model_scope':'Selected normal arithmetic only; not full placement/signature/acceptance model',
        'producer_window_sha256':hashlib.sha256(data[0x2487e:0x248f6]).hexdigest(),
        'physical_test_ready':False},indent=2))


if __name__=='__main__':main()
