#!/usr/bin/env python3
"""Decode supplied EXT_CSD bytes only; no device acquisition, selectors or writes."""
from verify_offline_escrow import require


def decode_geometry(data):
    require(type(data) is bytes and len(data)==512,'Exact supplied EXT_CSD bytes required')
    revision=data[192]
    require(revision in (6,7,8),'Only reviewed EXT_CSD revisions 6..8 supported')
    require(data[61] in (0,1),'Unsupported data-sector encoding')
    sector=4096 if data[61]==1 else 512
    # SEC_COUNT units remain 512 bytes, independently of current data-sector size.
    user=int.from_bytes(data[212:216],'little')*512
    boot=data[226]*(128*1024)
    require(0<user<=64*1024**3 and user%sector==0,'User capacity outside reviewed bounds')
    require(0<boot<=32*1024**2 and boot%sector==0,'Boot-region capacity outside reviewed bounds')
    access=data[179]&7
    return dict(ext_csd_revision=revision,logical_sector_bytes=sector,
                region_bytes=dict(user=user,boot1=boot,boot2=boot),
                supplied_partition_access=access,
                supplied_access_is_ordinary_region=access in (0,1,2),
                linux_boot_suffix_mapping=dict(boot1='boot0',boot2='boot1'),
                device_origin_verified=False,region_selection_verified=False,
                independently_acquired_verified=False,restore_qualified=False,physical_test_ready=False)
