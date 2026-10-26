#!/usr/bin/env python3
"""Stage one digest-pinned public bottle privately; inspect bytes, never load USB."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import urllib.error
import urllib.request
from preflight_mac_usb_library import inspect_file
from verify_offline_escrow import regular_file

ROOT=Path(__file__).resolve().parents[1]
DIGEST='b462926c2314b5bb7d1a6721f9a3cf7336a4166ba67024b4bbd0226de457132a'
SIZE=191568
URL='https://ghcr.io/v2/homebrew/core/libusb/blobs/sha256:'+DIGEST
MEMBER='libusb/1.0.30/lib/libusb-1.0.0.dylib'
DYLIB_SHA='95c5d6ec5e955b5fb83253963805a0e25a6b1253e9c4e217eaad68e31bb04f4a'
SYMBOLS=('libusb_init','libusb_exit','libusb_get_device_list','libusb_free_device_list',
         'libusb_open','libusb_control_transfer','libusb_bulk_transfer')


def extract(raw):
    if len(raw)!=SIZE or hashlib.sha256(raw).hexdigest()!=DIGEST:
        raise ValueError('Bottle identity mismatch')
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        expanded=stream.read(16*1024*1024+1)
    if len(expanded)>16*1024*1024:
        raise ValueError('Expanded archive budget exceeded')
    with tarfile.open(fileobj=io.BytesIO(expanded),mode='r:') as archive:
        members=[]
        for member in archive:
            members.append(member)
            if len(members)>256:raise ValueError('Archive member cap exceeded')
        targets=[m for m in members if m.name==MEMBER and m.isfile()]
        if len(targets)!=1 or targets[0].size>4*1024*1024:
            raise ValueError('Expected single regular dylib')
        data=archive.extractfile(targets[0]).read(targets[0].size+1)
    if hashlib.sha256(data).hexdigest()!=DYLIB_SHA:
        raise ValueError('Extracted dylib identity mismatch')
    return data


def fetch():
    headers={'Accept-Encoding':'identity'}
    try:response=urllib.request.urlopen(urllib.request.Request(URL,headers=headers),timeout=25)
    except urllib.error.HTTPError as error:
        if error.code!=401:raise
        token_url='https://ghcr.io/token?service=ghcr.io&scope=repository:homebrew/core/libusb:pull'
        with urllib.request.urlopen(token_url,timeout=25) as answer:auth=answer.read(65537)
        if len(auth)>65536:raise ValueError('Public token response cap exceeded')
        headers['Authorization']='Bearer '+json.loads(auth)['token']
        response=urllib.request.urlopen(urllib.request.Request(URL,headers=headers),timeout=25)
    with response:raw=response.read(SIZE+1)
    extract(raw)  # Verify before persisting any downloaded artifact.
    return raw


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download',action='store_true')
    args=parser.parse_args()
    base=ROOT/'out/libusb-artifact';base.mkdir(parents=True,exist_ok=True)
    bottle=base/'bottle.tar.gz'
    if args.download:bottle.write_bytes(fetch())
    with regular_file(bottle) as stream:
        raw=stream.read(SIZE+1)
    data=extract(raw)
    library=base/'libusb-1.0.0.dylib';library.write_bytes(data)
    result=inspect_file(library)
    symbols=subprocess.check_output(['/usr/bin/nm','-gU',str(library)],text=True)
    names={line.split()[-1] for line in symbols.splitlines() if line.split()}
    observed={name:'_'+name in names for name in SYMBOLS}
    if not all(observed.values()):raise ValueError('Required static export names missing')
    print(json.dumps({'bottle_sha256':DIGEST,'bottle_bytes':SIZE,'selected_member':MEMBER,
        'artifact_staged_in_ignored_workspace':True,
        'static_library':result,'required_static_symbol_names_present':observed,
        'native_code_loaded':False,'system_install_performed':False,'usb_enumerated':False,
        'signature_or_runtime_abi_verified':False,'physical_test_ready':False},indent=2))


if __name__=='__main__':
    main()
