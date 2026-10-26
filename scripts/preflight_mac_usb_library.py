#!/usr/bin/env python3
"""Static regular-file Mach-O preflight. Never load code, enumerate USB or install."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
from verify_offline_escrow import regular_file

ARM64=0x0100000C
MAX_FILE=64*1024*1024


def require(ok, message):
    if not ok:raise ValueError(message)


def thin(data, offset, size):
    require(size>=32 and offset+size<=len(data),'Truncated Mach-O slice')
    header=struct.unpack_from('<8I',data,offset)
    magic,cpu,subtype,kind,ncmds,command_bytes,flags,reserved=header
    require(magic==0xFEEDFACF and cpu==ARM64 and subtype==0,'Not generic arm64 Mach-O64')
    require(kind==6,'Not a dylib')
    require(0<ncmds<=4096 and 8*ncmds<=command_bytes<=size-32,'Invalid load-command bounds')
    position=offset+32;end=position+command_bytes;identity_count=0
    for _ in range(ncmds):
        require(position+8<=end,'Truncated load command')
        cmd,length=struct.unpack_from('<II',data,position)
        require(length>=8 and length%8==0 and position+length<=end,'Invalid load command')
        if cmd==0xD:  # LC_ID_DYLIB
            require(length>=24,'Truncated dylib identity')
            name=struct.unpack_from('<I',data,position+8)[0]
            require(24<=name<length and b'\0' in data[position+name:position+length],
                    'Invalid dylib identity string')
            identity_count+=1
        position+=length
    require(position==end and identity_count==1,'Incomplete commands or missing/duplicate dylib identity')
    return {'architecture':'arm64','filetype':'dylib','load_commands':ncmds,
            'slice_bytes':size,'header_structure_valid':True}


def inspect(data):
    require(32<=len(data)<=MAX_FILE,'Input outside size cap')
    magic=struct.unpack_from('>I',data)[0]
    if magic not in (0xCAFEBABE,0xBEBAFECA,0xCAFEBABF,0xBFBAFECA):
        return thin(data,0,len(data))
    endian='>' if magic in (0xCAFEBABE,0xCAFEBABF) else '<'
    wide=magic in (0xCAFEBABF,0xBFBAFECA)
    count=struct.unpack_from(endian+'I',data,4)[0]
    width=32 if wide else 20;table_end=8+count*width
    require(0<count<=32 and table_end<=len(data),'Invalid fat architecture table')
    spans=[];selected=[]
    for index in range(count):
        values=struct.unpack_from(endian+('IIQQII' if wide else 'IIIII'),data,8+index*width)
        cpu,subtype,offset,size,alignment=values[:5]
        require(alignment<=30 and offset>=table_end and offset%(1<<alignment)==0,
                'Invalid fat slice alignment/offset')
        require(size>=32 and offset+size<=len(data),'Fat slice outside file')
        if wide:require(values[5]==0,'Unexpected fat reserved field')
        spans.append((offset,offset+size))
        if cpu==ARM64 and subtype==0:selected.append((offset,size))
    spans.sort()
    require(all(a[1]<=b[0] for a,b in zip(spans,spans[1:])),'Overlapping fat slices')
    require(len(selected)==1,'Expected exactly one generic arm64 slice')
    return {'fat_architecture_count':count,**thin(data,*selected[0])}


def inspect_file(path):
    # Resolve an explicitly selected installation symlink; final target must be
    # regular before open. Trusted host directories, not hostile race protection.
    target=path.resolve(strict=True)
    with regular_file(target) as stream:
        data=stream.read(MAX_FILE+1)
    result=inspect(data)
    return {**result,'file_bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
            'native_code_loaded':False,'libusb_exports_verified':False,
            'dependency_loading_verified':False,'usb_enumerated':False,'physical_test_ready':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library',type=Path)
    args=parser.parse_args()
    locations=[('explicit',args.library)] if args.library else [
        ('homebrew-arm64',Path('/opt/homebrew/opt/libusb/lib/libusb-1.0.dylib')),
        ('homebrew-intel',Path('/usr/local/opt/libusb/lib/libusb-1.0.dylib'))]
    results=[];failed=False
    for label,path in locations:
        try:
            results.append({'candidate':label,'present':True,'static_result':inspect_file(path)})
        except FileNotFoundError:
            results.append({'candidate':label,'present':False});failed|=bool(args.library)
        except (ValueError,OSError):
            results.append({'candidate':label,'static_validation_failed':True});failed=True
    print(json.dumps({'scope':'Explicit/standard host regular files only; not a whole-host inventory',
        'candidates':results,'native_library_loaded':False,'usb_enumerated':False,
        'physical_test_ready':False},indent=2))
    return int(failed)


if __name__=='__main__':
    raise SystemExit(main())
