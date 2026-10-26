#!/usr/bin/env python3
"""Host-only exact candidate load/version probe. No libusb context or device APIs."""
import ctypes
import hashlib
import json
from pathlib import Path
import platform
ROOT=Path(__file__).resolve().parents[1]
DIGEST='95c5d6ec5e955b5fb83253963805a0e25a6b1253e9c4e217eaad68e31bb04f4a'


def main():
    if platform.system()!='Darwin' or platform.machine()!='arm64':
        raise ValueError('Reviewed Darwin arm64 host required')
    path=ROOT/'out/libusb-artifact/libusb-1.0.0.dylib'
    if path.is_symlink() or not path.is_file() or path.stat().st_size!=162720:
        raise ValueError('Expected regular exact candidate')
    if hashlib.sha256(path.read_bytes()).hexdigest()!=DIGEST:
        raise ValueError('Candidate identity mismatch')
    library=ctypes.CDLL(str(path))
    version=library.libusb_get_version
    version.argtypes=[]
    # Read only the fixed four uint16 fields; do not dereference optional strings.
    version.restype=ctypes.POINTER(ctypes.c_uint16*4)
    result=version()
    if not result:raise ValueError('Null version result')
    numeric=list(result.contents)
    if numeric[:3]!=[1,0,30]:raise ValueError('Unexpected candidate version')
    print(json.dumps({'candidate_sha256':DIGEST,'numeric_version':numeric,
        'native_library_loaded':True,'version_call_completed':True,
        'context_initialized':False,'device_enumeration_called':False,
        'device_open_called':False,'physical_test_ready':False},indent=2))


if __name__=='__main__':main()
