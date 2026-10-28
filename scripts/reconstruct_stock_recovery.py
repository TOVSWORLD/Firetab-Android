#!/usr/bin/env python3
"""Reconstruct pinned stock recovery bytes locally; no vendor helper, mount or device access."""
import argparse
import bz2
import hashlib
import json
import os
from pathlib import Path
import struct
import tempfile
import zlib
from verify_offline_escrow import regular_file

CAP = 16 * 1024 * 1024
PINS = {
    'boot': '8982fa50193acc764be69ee51027ee92e83614cee4b8235b07439d1f9e2db363',
    'patch': '319e8ed946abfb9eab83b2f343212b8a93d0bd05c5489e77758747652cb75e40',
    'bonus': '7227fe97af0cf79c18bcf89048054a90bc0803bf3aa568dde88a1d879d7b0a05'}
TARGET_BYTES = 9299968
TARGET_SHA1 = '8e5e7f6f63fd77383c5721a13d818f880a1e70c9'


def signed_offset(raw):
    if len(raw) != 8:
        raise ValueError('Eight-byte BSDIFF signed offset required')
    value = int.from_bytes(raw, 'little') & ((1 << 63)-1)
    return -value if raw[7] & 128 else value


def bunzip(raw, cap=CAP):
    decoder = bz2.BZ2Decompressor()
    data = decoder.decompress(raw, max_length=cap+1)
    if len(data) > cap or not decoder.eof or decoder.unused_data:
        raise ValueError('Invalid or oversized single bzip2 stream')
    return data


def bsdiff(old, patch):
    if len(old) > CAP or not 32 <= len(patch) <= CAP or patch[:8] != b'BSDIFF40':
        raise ValueError('Unsupported BSDIFF input')
    control_bytes, diff_bytes, size = [signed_offset(patch[x:x+8]) for x in (8,16,24)]
    if min(control_bytes,diff_bytes,size) < 0 or size > CAP or 32+control_bytes+diff_bytes > len(patch):
        raise ValueError('BSDIFF bounds')
    control = bunzip(patch[32:32+control_bytes],1024*1024)
    diff = bunzip(patch[32+control_bytes:32+control_bytes+diff_bytes])
    extra = bunzip(patch[32+control_bytes+diff_bytes:])
    out = bytearray(); oldpos = cp = dp = ep = 0
    while len(out) < size:
        if cp+24 > len(control):
            raise ValueError('Missing BSDIFF control')
        x,y,seek = [signed_offset(control[a:a+8]) for a in (cp,cp+8,cp+16)];cp+=24
        if min(x,y)<0 or len(out)+x+y>size or dp+x>len(diff) or ep+y>len(extra):
            raise ValueError('BSDIFF control bounds')
        for i in range(x):
            original = old[oldpos+i] if 0 <= oldpos+i < len(old) else 0
            out.append((diff[dp+i]+original)&255)
        dp+=x;oldpos+=x
        out.extend(extra[ep:ep+y]);ep+=y;oldpos+=seek
        if abs(oldpos)>2*CAP:
            raise ValueError('BSDIFF seek budget')
    if cp != len(control) or dp != len(diff) or ep != len(extra):
        raise ValueError('Unused BSDIFF decoded data')
    return bytes(out)


def imgdiff(old, patch, bonus=b''):
    if any(type(x) is not bytes or len(x)>CAP for x in (old,patch,bonus)) or len(patch)<12 or patch[:8]!=b'IMGDIFF2':
        raise ValueError('Unsupported IMGDIFF input')
    count=struct.unpack_from('<I',patch,8)[0]
    if not 1<=count<=32:
        raise ValueError('Chunk count')
    pos=12;chunks=[]
    for index in range(count):
        if pos+4>len(patch):raise ValueError('Truncated chunk type')
        kind=struct.unpack_from('<I',patch,pos)[0];pos+=4
        if kind in (0,2):
            length=24 if kind==0 else 60
            if pos+length>len(patch):raise ValueError('Truncated chunk header')
            values=struct.unpack_from('<3Q' if kind==0 else '<5Q5i',patch,pos);pos+=length
            start,size,offset=values[:3]
            if start+size>len(old):raise ValueError('Source chunk bounds')
            chunks.append((kind,index,values))
        elif kind==3:
            if pos+4>len(patch):raise ValueError('Truncated raw length')
            length=struct.unpack_from('<I',patch,pos)[0];pos+=4
            if pos+length>len(patch) or length>CAP:raise ValueError('Raw chunk bounds')
            chunks.append((kind,index,patch[pos:pos+length]));pos+=length
        else:raise ValueError('Unsupported chunk type')
    offsets=[x[2][2] for x in chunks if x[0]!=3]
    if offsets!=sorted(set(offsets)) or any(not pos<=x<len(patch) for x in offsets):
        raise ValueError('Patch offsets not unique/ordered/outside headers')
    ends=dict(zip(offsets,offsets[1:]+[len(patch)]));out=bytearray()
    for kind,index,values in chunks:
        if kind==3:piece=values
        else:
            start,size,offset=values[:3];source=old[start:start+size]
            if kind==2:
                expanded,target,level,method,window,memory,strategy=values[3:]
                if not 0<=expanded<=CAP or not 0<=target<=CAP or (level,method,window,memory,strategy)!=(6,8,-15,8,0):
                    raise ValueError('Unreviewed deflate parameters or length')
                decoder=zlib.decompressobj(-15);source=decoder.decompress(source,expanded+1)
                if len(source)>expanded or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
                    raise ValueError('Invalid source deflate stream')
                if index==1:source+=bonus
                if len(source)!=expanded:raise ValueError('Expanded source/bonus length mismatch')
            piece=bsdiff(source,patch[offset:ends[offset]])
            if kind==2:
                if len(piece)!=target:raise ValueError('Patched expanded target length mismatch')
                compressor=zlib.compressobj(level,method,window,memory,strategy)
                piece=compressor.compress(piece)+compressor.flush()
        if len(out)+len(piece)>CAP:raise ValueError('Aggregate output cap')
        out.extend(piece)
    return bytes(out)


def pinned_recovery(boot,patch,bonus):
    for name,data in [('boot',boot),('patch',patch),('bonus',bonus)]:
        if hashlib.sha256(data).hexdigest()!=PINS[name]:raise ValueError('Pinned input differs: '+name)
    result=imgdiff(boot,patch,bonus)
    if len(result)!=TARGET_BYTES or hashlib.sha1(result).hexdigest()!=TARGET_SHA1:
        raise ValueError('Reconstructed output differs from signed target; never publish')
    return result


def publish(path,data):
    temporary=None
    try:
        with tempfile.NamedTemporaryFile(prefix='.recovery-incomplete-',dir=path.parent,delete=False) as stream:
            temporary=Path(stream.name)
            if stream.write(data)!=len(data):raise OSError('Incomplete host write')
            stream.flush();os.fsync(stream.fileno())
            if os.fstat(stream.fileno()).st_size!=len(data):raise OSError('Host length differs')
        os.link(temporary,path)  # Exclusive same-directory publication; never overwrite.
    finally:
        if temporary is not None:temporary.unlink(missing_ok=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['boot','patch','bonus','output']:parser.add_argument('--'+name,required=True,type=Path)
    args=parser.parse_args();inputs=[]
    for name in ['boot','patch','bonus']:
        with regular_file(getattr(args,name)) as stream:data=stream.read(CAP+1)
        if len(data)>CAP:raise ValueError('Input cap')
        inputs.append(data)
    result=pinned_recovery(*inputs)
    publish(args.output,result)
    print(json.dumps({'bytes':len(result),'sha1':hashlib.sha1(result).hexdigest(),
        'sha256':hashlib.sha256(result).hexdigest(),'matches_signed_target':True,
        'zlib_runtime':zlib.ZLIB_RUNTIME_VERSION,'firmware_or_helpers_executed':False,
        'device_accessed':False,'recovery_boot_verified':False,'stock_return_verified':False},indent=2))


if __name__=='__main__':main()
