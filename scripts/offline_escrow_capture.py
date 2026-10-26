#!/usr/bin/env python3
"""Transport-neutral host capture contract; contains no device/helper binding or CLI."""
import hashlib
import os
from pathlib import Path
import shutil
import tempfile

REGIONS=frozenset(('user','boot1','boot2'))
MAX_CHUNK=1024*1024
HOST_MARGIN=64*1024*1024


def capture_region(destination, region, expected_bytes, select_region, read_chunk, chunk_bytes=MAX_CHUNK):
    """Callers must separately qualify geometry, callbacks and their timeouts.

    Tests supply synthetic callbacks only. This function cannot establish the
    storage origin, protocol checksum validity or side effects of a callback.
    """
    path=Path(destination)
    if region not in REGIONS or type(expected_bytes) is not int or not 0<expected_bytes<=64*1024**3:
        raise ValueError('Explicit ordinary eMMC region/positive bounded length required')
    if type(chunk_bytes) is not int or not 0<chunk_bytes<=MAX_CHUNK:
        raise ValueError('Invalid chunk budget')
    if not path.parent.is_dir() or path.exists() or path.is_symlink():
        raise ValueError('Fresh output in an existing trusted host directory required')
    if shutil.disk_usage(path.parent).free<expected_bytes+HOST_MARGIN:
        raise ValueError('Insufficient host disk budget')
    if select_region(region) is not True:
        raise ValueError('Region selection not acknowledged; no read permitted')
    temporary=None
    try:
        with tempfile.NamedTemporaryFile(prefix='.escrow-incomplete-',dir=path.parent,delete=False) as stream:
            temporary=Path(stream.name);digest=hashlib.sha256();offset=0
            while offset<expected_bytes:
                count=min(chunk_bytes,expected_bytes-offset)
                data=read_chunk(region,offset,count)
                if not isinstance(data,bytes) or len(data)!=count:
                    raise ValueError('Short, oversized or invalid chunk; capture incomplete')
                if stream.write(data)!=count:
                    raise OSError('Incomplete host write')
                digest.update(data);offset+=len(data)
            stream.flush();os.fsync(stream.fileno())
            if os.fstat(stream.fileno()).st_size!=expected_bytes:
                raise OSError('Host capture length mismatch')
        # Same-directory exclusive publish: never replace an existing output.
        os.link(temporary,path)
        return {'region':region,'bytes':expected_bytes,'sha256':digest.hexdigest(),
                'host_capture_complete':True,'collection_region_identity_verified':False,
                'protocol_checksum_verified':False,'callback_binding_qualified':False,
                'restore_qualified':False,'physical_test_ready':False}
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
