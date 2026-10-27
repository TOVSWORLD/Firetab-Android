#!/usr/bin/env python3
"""Reconcile pinned original-package metadata with selected source write arithmetic only."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW_SHA256 = '822b565413d1f34614dcd03b85d0eabcf0d157bc69c2b16262e875705d60443d'
SECTOR = 512


def extent(start_lba, content_bytes, capacity_bytes=None):
    if type(start_lba) is not int or type(content_bytes) is not int or start_lba < 0 or content_bytes <= 0:
        raise ValueError('Positive byte count and nonnegative integer LBA required')
    padded = ((content_bytes + SECTOR-1)//SECTOR)*SECTOR
    start = start_lba*SECTOR
    end = start+padded
    if end > 1 << 64:
        raise ValueError('Extent overflow')
    if capacity_bytes is not None and (type(capacity_bytes) is not int or capacity_bytes < end):
        raise ValueError('Extent exceeds supplied static capacity')
    return {'relative_start_bytes': start, 'content_bytes': content_bytes,
        'padded_bytes': padded, 'relative_end_exclusive': end,
        'static_capacity_bytes': capacity_bytes,
        'static_capacity_fit': None if capacity_bytes is None else True}


def audit():
    raw = (ROOT/'evidence/douglas-original-route/original-package-review.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != REVIEW_SHA256:
        raise ValueError('Pinned original-package review identity differs')
    review = json.loads(raw)
    entries = {x['name']: x for x in review['amonet-douglas-v1.2.zip']['entries']}
    def component(name, lba, capacity=None):
        item = entries['amonet/bin/'+name]
        return {'component': name, 'sha256': item['sha256'], **extent(lba,item['bytes'],capacity)}
    boot0 = [component('preloader.hdr0',0),component('preloader.hdr1',4),
             component('preloader.bin',8),component('preloader.bin',520)]
    # This is a separation check within the source's boot0 layout, not device capacity.
    for left,right in zip(boot0,boot0[1:]):
        if left['relative_end_exclusive'] > right['relative_start_bytes']:
            raise ValueError('Source-declared boot0 component ranges overlap')
    slot = 0x37000*SECTOR
    payload = [component('boot.hdr',0,slot),component('boot.payload',223223,slot)]
    if payload[0]['relative_end_exclusive'] > payload[1]['relative_start_bytes']:
        raise ValueError('Source-declared exploit components overlap')
    return {'scope':'Pinned metadata plus selected source layout arithmetic, not live GPT or write authorization',
        'review_sha256':REVIEW_SHA256,'sector_bytes_assumed_by_helper':SECTOR,
        'boot0_components':boot0,'boot0_component_ranges_disjoint':True,
        'declared_new_boot_recovery_slot_bytes':slot,
        'each_new_boot_recovery_slot_components':payload,
        'payload_tail_slack_bytes':slot-payload[-1]['relative_end_exclusive'],
        'partition_relative_components':[component('tz.img',0),component('lk.bin',0),component('twrp.img',0)],
        'generated_primary_gpt_bytes':34*SECTOR,'generated_backup_gpt_bytes':33*SECTOR,
        'actual_gpt_names_and_addresses_verified':False,'actual_target_capacities_verified':False,
        'selector_acknowledgement_verified':False,'native_payload_binary_source_match_verified':False,
        'independent_failure_return_qualified':False,'device_accessed':False,'physical_test_ready':False}


if __name__ == '__main__':
    print(json.dumps(audit(),indent=2))
