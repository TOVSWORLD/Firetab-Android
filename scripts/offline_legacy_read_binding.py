#!/usr/bin/env python3
"""Source-contract adapter for synthetic tests; no helper import, bootstrap or CLI."""
from offline_escrow_capture import MAX_CHUNK, REGIONS

REGION_IDS={'user':8,'boot1':1,'boot2':2}


def geometry(values, sector_bytes):
    if sector_bytes not in (512,4096) or set(values)!=REGIONS:
        raise ValueError('Explicit ordinary-region geometry required')
    result=dict(values)
    if any(type(n) is not int or not 0<n<=64*1024**3 or n%sector_bytes for n in result.values()):
        raise ValueError('Invalid raw region geometry')
    return result


class OfflineLegacyReadBinding:
    """Callbacks must be independently qualified before any real use.

    A future readflash callback MUST include the prepared strict selection guard;
    readflash internally re-selects a region. A prior selection cannot prove that
    second selection succeeded. This adapter does not attest callback source.
    """
    def __init__(self, expected_geometry, observed_geometry, translator, selector, readflash,
                 *, backend_kind, storage_kind, iot, sector_bytes):
        if backend_kind!='legacy' or storage_kind!='emmc' or iot is not False:
            raise ValueError('Only the reviewed non-IoT legacy eMMC contract is supported')
        self.sector=sector_bytes
        self.expected=geometry(expected_geometry,sector_bytes)
        self.observed=observed_geometry
        self.translator=translator
        self.selector=selector
        self.reader=readflash
        self.active=None
        self._check_geometry()

    def _check_geometry(self):
        if geometry(self.observed(),self.sector)!=self.expected:
            raise ValueError('Observed geometry mismatch/change')

    def _translate(self, region, count):
        length,region_id=self.translator(parttype=region,length=count)
        if type(length) is not int or length!=count or type(region_id) is not int or region_id!=REGION_IDS[region]:
            raise ValueError('Backend clipped length or mapped the wrong region')
        return region_id

    def select_region(self, region):
        self.active=None
        if region not in REGIONS:raise ValueError('Unsupported region')
        self._check_geometry()
        region_id=self._translate(region,self.expected[region])
        if self.selector(region_id) is not True:
            raise ValueError('Region selection not acknowledged')
        self.active=region
        return True

    def read_chunk(self, region, offset, count):
        try:
            return self._read_checked(region,offset,count)
        except BaseException:
            self.active=None
            raise

    def _read_checked(self, region, offset, count):
        if region not in REGIONS or self.active!=region:
            raise ValueError('No acknowledged active region')
        if (type(offset) is not int or type(count) is not int or offset<0 or
            not 0<count<=MAX_CHUNK or offset%self.sector or count%self.sector or
            offset+count>self.expected[region]):
            raise ValueError('Read extent outside explicit aligned region/chunk bounds')
        self._check_geometry();self._translate(region,count)
        data=self.reader(addr=offset,length=count,filename='',parttype=region,display=False)
        if not isinstance(data,bytes) or len(data)!=count:
            raise ValueError('Backend returned incomplete/invalid memory-mode read')
        return data
