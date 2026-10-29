#!/usr/bin/env python3
"""Verify the isolated disabled USB resource delta; never grant device readiness."""
import argparse
import copy
import json
from pathlib import Path
import struct
import subprocess
from compare_pmic_dtb import snapshot
ROOT=Path(__file__).resolve().parents[1]
PHY='/soc/t-phy@11210000'
USB0='/soc/usb@11200000';USB1='/soc/usb@11270000'
CHILDREN=['usb-phy@11210800','usb-phy@11210900']


def encode(data):return ' '.join(format(x,'x') for x in data)


def reservations(data):
    if len(data)<40 or struct.unpack_from('>I',data)[0]!=0xd00dfeed:raise ValueError('Invalid FDT header')
    offset=struct.unpack_from('>I',data,16)[0];rows=[]
    if offset<40 or offset%8:raise ValueError('Invalid reserve-table offset')
    while offset+16<=len(data):
        address,size=struct.unpack_from('>QQ',data,offset);offset+=16
        if address==0 and size==0:return rows
        rows.append((address,size))
    raise ValueError('Unterminated reserve table')


def compare(base,candidate,base_order,candidate_order,base_reserve,candidate_reserve):
    if base_order!=CHILDREN or candidate_order!=base_order:raise ValueError('PHY child order/index drift')
    if base_reserve!=candidate_reserve:raise ValueError('Reservation table drift')
    if base.get(PHY,{}).get('reg')!=encode(struct.pack('>4I',0,0x11210000,0,0x800)) or 'reg-names' in base[PHY]:raise ValueError('Unexpected baseline PHY resource')
    disabled=encode(b'disabled\0')
    for path in [PHY,USB0,USB1]:
        if base.get(path,{}).get('status')!=disabled:raise ValueError('Reviewed USB baseline is not disabled')
    expected=copy.deepcopy(base)
    expected[PHY]['reg']=encode(struct.pack('>8I',0,0x11210000,0,0x800,0,0x11210f00,0,0x100))
    expected[PHY]['reg-names']=encode(b'sif\0u2-frequency\0')
    if expected!=candidate:raise ValueError('Unexpected property/path/phandle or disabled-state change')
    return {'scope':'Complete source-DTB metadata delta only; not PHY/device qualification','nodes_compared':len(base),
            'base_property_count':sum(len(n) for n in base.values()),'candidate_property_count':sum(len(n) for n in candidate.values()),
            'only_changed_properties':[PHY+'/reg',PHY+'/reg-names'],
            'all_other_property_and_phandle_values_unchanged':True,'child_order_preserved':True,
            'reservation_table_preserved':True,'usb0_usb1_and_phy_remain_disabled':True,
            'usb1_port1_driver_supported':False,'runtime_qualified':False}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fdtget',type=Path,default=ROOT/'work/dtb-tool/build/fdtget');args=p.parse_args()
    base=ROOT/'work/dtb-compile/pwrap-pmic-node-name/douglas.dtb';candidate=ROOT/'work/dtb-compile/usb-frequency-resource/douglas.dtb'
    order=lambda dtb:subprocess.check_output([str(args.fdtget),'-l',str(dtb),PHY],text=True).splitlines()
    result=compare(snapshot(args.fdtget,base),snapshot(args.fdtget,candidate),order(base),order(candidate),reservations(base.read_bytes()),reservations(candidate.read_bytes()))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
