#!/usr/bin/env python3
"""Compare two supplied host-file capture sets; no collection or restoration."""
import argparse
import json
from pathlib import Path
from verify_offline_escrow import regular_file, require, verify_region
from decode_offline_emmc_geometry import decode_geometry


def verify_set(manifest_path, identities, geometry=None):
    with regular_file(manifest_path) as stream:raw=stream.read(65537)
    require(len(raw)<=65536,'Manifest exceeds cap')
    manifest=json.loads(raw)
    require(set(manifest)=={'logical_sector_bytes','regions'},'Unexpected manifest fields')
    require(set(manifest['regions'])=={'user','boot1','boot2'},'All regions required')
    if geometry is not None:
        require(manifest['logical_sector_bytes']==geometry['logical_sector_bytes'],
                'Manifest sector size differs from supplied EXT_CSD')
    fingerprint={}
    for name in ('user','boot1','boot2'):
        record=manifest['regions'][name]
        require(set(record)=={'file','expected_bytes','sha256'},'Unexpected region fields')
        if geometry is not None:
            require(record['expected_bytes']==geometry['region_bytes'][name],
                    'Region extent differs from supplied EXT_CSD')
        path=Path(manifest_path).resolve().parent/record['file']
        before=path.lstat();identity=(before.st_dev,before.st_ino)
        require(identity not in identities,'Capture files alias an already supplied inode')
        verify_region(path,record['expected_bytes'],record['sha256'],
                      manifest['logical_sector_bytes'] if name=='user' else None)
        after=path.lstat()
        require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==
                (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),
                'Capture changed during verification')
        identities.add(identity)
        fingerprint[name]=(record['expected_bytes'],record['sha256'])
    return manifest['logical_sector_bytes'],fingerprint


def compare_sets(first, second, *, ext_csd=None):
    geometry=decode_geometry(ext_csd) if ext_csd is not None else None
    identities=set()
    a=verify_set(first,identities,geometry);b=verify_set(second,identities,geometry)
    require(a==b,'Capture geometry or bytes disagree')
    return dict(offline_capture_sets_agree=True,
                geometry_matches_supplied_ext_csd=(geometry is not None),
                supplied_metadata_origin_verified=False,distinct_host_inodes_checked=True,
                independently_acquired_verified=False,collection_region_identity_verified=False,
                RTC_or_RPMB_covered=False,restore_qualified=False,physical_test_ready=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('first');parser.add_argument('second')
    parser.add_argument('--ext-csd',help='Optional supplied regular 512-byte host metadata file')
    args=parser.parse_args()
    try:
        ext_csd=None
        if args.ext_csd:
            with regular_file(args.ext_csd) as stream:ext_csd=stream.read(513)
        result=compare_sets(args.first,args.second,ext_csd=ext_csd)
    except (ValueError,OSError,KeyError,TypeError) as error:
        print(json.dumps(dict(offline_capture_sets_agree=False,error_type=type(error).__name__,
                             restore_qualified=False,physical_test_ready=False)))
        raise SystemExit(1)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
