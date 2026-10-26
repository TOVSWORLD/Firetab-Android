#!/usr/bin/env python3
"""Bounded metadata/digest inspection of cached preloader EMI; never emit/execute firmware."""
import hashlib
import json
from pathlib import Path
import struct
from verify_offline_escrow import regular_file

ROOT=Path(__file__).resolve().parents[1]
MARKER=b'MTK_BLOADER_INFO_v'
GFH=b'MMM\x01\x38\x00\x00\x00'
MAX_INPUT=1024*1024
SOURCES={
 'current_659664620':('out/ota-loader-inspection-659664620/preloader.bin',
  'b30d8d1292c620ed372050549cff27f153fec6c2467484b9202265c0a364fea5'),
 'older_636558520':('out/official-loader-636558520/preloader.bin',
  'cefc66528a56626e65a553b7f97e0521e7939c195ce72794e7c4e14eab04619d')}


def inspect(data):
    if not 60<=len(data)<=MAX_INPUT or not data.startswith(GFH):
        raise ValueError('Expected bounded GFH-at-zero preloader')
    declared=struct.unpack_from('<I',data,0x20)[0]
    signature=struct.unpack_from('<I',data,0x2C)[0]
    if declared!=len(data) or not 0<signature<declared-60:
        raise ValueError('Invalid declared file/signature bounds')
    end=declared-signature
    length=struct.unpack_from('<I',data,end-4)[0]
    if not 0<length<=65536 or end-4-length<0x38:
        raise ValueError('Unsupported zero/oversized EMI footer')
    start=end-4-length;window=data[start:end-4]
    if not window.startswith(MARKER) or window.count(MARKER)!=1:
        raise ValueError('Missing/ambiguous loader-info tag')
    version=window[len(MARKER):len(MARKER)+2]
    if version!=b'16':raise ValueError('Only reviewed EMI version16 is supported')
    if window.count(b'MTK_BIN')!=1:raise ValueError('Missing/ambiguous EMI data tag')
    offset=window.index(b'MTK_BIN')+12
    if offset>=len(window):raise ValueError('Truncated EMI data tag')
    payload=window[offset:]
    return {'preloader_bytes':len(data),'declared_signature_bytes':signature,
        'loader_info_offset':start,'loader_info_bytes':length,'emi_format_version_decimal':16,
        'emi_format_version_hex':'0x10','emi_data_offset':start+offset,'emi_data_bytes':len(payload),
        'emi_data_sha256':hashlib.sha256(payload).hexdigest(),
        'helper_v16_branch_format_match':True,'agent_acceptance_verified':False,
        'dram_capacity_or_layout_verified':False,'installed_binary_equivalence_verified':False,
        'vendor_signature_verified':False,'firmware_executed':False,'physical_test_ready':False}


def main():
    results={}
    for name,(path,digest) in SOURCES.items():
        with regular_file(ROOT/path) as stream:data=stream.read(MAX_INPUT+1)
        if hashlib.sha256(data).hexdigest()!=digest:raise ValueError('Cached preloader identity mismatch')
        results[name]={'preloader_sha256':digest,**inspect(data)}
    source_index=json.loads((ROOT/'evidence/recovery-agent/source-index.json').read_text())
    config=next(x for x in source_index['files'] if x['source_path'].endswith('/daconfig.py'))
    raw=(ROOT/'out/recovery-entry/mtkclient'/config['source_path']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=config['sha256']:raise ValueError('Pinned extraction source mismatch')
    same=len({x['emi_data_sha256'] for x in results.values()})==1
    print(json.dumps({'scope':'Data-format/digest match only; no helper or firmware execution',
        'results':results,'current_and_older_emi_identical':same,'helper_extraction_source':config,
        'helper_revision':source_index['revision'],'physical_test_ready':False,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))


if __name__=='__main__':
    main()
