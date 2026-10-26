#!/usr/bin/env python3
"""Read capped table ranges from pinned agent containers; never read stage code."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REV = '7cb40e727727dfe3faa065eefb29b16ed29bbdf1'
MAX_RANGE = 512 * 1024


def parse_records(data, count, width, file_size):
    if width not in (0xD8, 0xDC) or not 2 <= count <= 2048 or len(data) != count * width:
        raise ValueError('Unsupported record table geometry')
    records = []
    for index in range(count):
        row = data[index*width:(index+1)*width]
        old = width == 0xD8
        fields = struct.unpack_from('<' + 'H'*(8 if old else 10), row)
        magic, code, subcode, hwver = fields[:4]
        swver = 0 if old else fields[4]
        pagesize, region_index, region_count = (fields[4], fields[6], fields[7]) if old else (fields[6], fields[8], fields[9])
        start = 16 if old else 20
        if code != 0x8163:
            continue
        if magic != 0xDADA or not 2 <= region_count <= (width-start)//20:
            raise ValueError('Invalid target record')
        regions = []
        for region in range(region_count):
            offset, length, address, start_offset, signature = struct.unpack_from('<IIIII', row, start+20*region)
            if offset > file_size or length > file_size-offset or signature > length:
                raise ValueError('Agent region outside container')
            regions.append({'index':region,'file_offset':offset,'bytes':length,'signature_bytes':signature})
        records.append({'record_index':index,'hardware_subcode':subcode,'hardware_version':hwver,
                        'software_version':swver,'pagesize':pagesize,'entry_region_index':region_index,
                        'regions':regions})
    return records


class Ranges:
    def __init__(self):
        self.bytes = 0
        self.receipts = []

    def read(self, item, offset, length):
        if (not 0 < length <= MAX_RANGE or offset < 0 or offset+length > item['size']
                or self.bytes+length > 3*1024*1024):
            raise ValueError('Range outside cap/container')
        url=f"https://raw.githubusercontent.com/bkerler/mtkclient/{REV}/{item['path']}"
        request=urllib.request.Request(url,headers={'Range':f'bytes={offset}-{offset+length-1}',
                                                   'Accept-Encoding':'identity'})
        with urllib.request.urlopen(request,timeout=25) as response:
            expected=f"bytes {offset}-{offset+length-1}/{item['size']}"
            if response.status != 206 or response.headers.get('Content-Range') != expected:
                raise ValueError('Server did not honor exact bounded range; body not read')
            if response.headers.get('Content-Encoding') not in (None,'identity'):
                raise ValueError('Encoded response rejected')
            data=response.read(length+1)
            if len(data) != length:
                raise ValueError('Wrong range body length')
        self.bytes += len(data)
        if self.bytes > 3*1024*1024:
            raise ValueError('Aggregate metadata budget exceeded')
        self.receipts.append({'path':item['path'],'offset':offset,'bytes':length,
                              'sha256':hashlib.sha256(data).hexdigest()})
        return data


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download-metadata',action='store_true',required=True)
    parser.parse_args()
    inventory=json.loads((ROOT/'evidence/recovery-agent/report.json').read_text())
    if inventory['revision'] != REV:
        raise ValueError('Unexpected revision')
    reader=Ranges(); result=[]
    for item in inventory['default_filename_candidates']:
        if not re.fullmatch(r'mtkclient/Loader/MTK_[A-Za-z0-9_]+\.bin',item['path']):
            raise ValueError('Unexpected candidate path')
        header=reader.read(item,0,0x6C)
        count=struct.unpack_from('<I',header,0x68)[0]
        if not 2 <= count <= 2048:
            raise ValueError('Unsupported record count')
        marker=reader.read(item,0x6C+0xD8,2)
        width=0xD8 if marker == b'\xDA\xDA' else 0xDC
        table=reader.read(item,0x6C,count*width)
        result.append({'path':item['path'],'container_bytes':item['size'],'git_blob_sha1':item['sha'],
                       'v6_header':b'MTK_DA_v6' in header,'record_count':count,'record_width':width,
                       'mt8163_records':parse_records(table,count,width,item['size'])})
    print(json.dumps({'revision':REV,'scope':'Header/table metadata only; no agent stage code',
        'body_bytes':reader.bytes,'containers':result,'range_receipts':reader.receipts,
        'full_container_digest_verified':False,'vendor_signature_verified':False,
        'actual_device_record_selected':False,'physical_test_ready':False,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))


if __name__=='__main__':
    main()
