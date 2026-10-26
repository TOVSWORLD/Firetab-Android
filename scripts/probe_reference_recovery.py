#!/usr/bin/env python3
"""Bounded pinned third-party recovery archive inspection; never executes archive content."""
import argparse
import hashlib
import json
from pathlib import Path
from probe_stock_ota import RangeClient, zip_entries, extract_entry

URL = 'https://raw.githubusercontent.com/ryanfortner/FireHD8-2017/91f93505eee47d6848dc6e161f29011503106a33/amonet-douglas.zip'
SIZE = 22329263
BUDGET = 2*1024*1024
SELECTED = {'amonet/bin/preloader.bin': 'preloader.bin', 'amonet/bin/lk.bin': 'lk.bin',
            'amonet/step-1.sh': 'step-1.sh.txt', 'amonet/step-2.sh': 'step-2.sh.txt',
            'amonet/fastboot-step.sh': 'fastboot-step.sh.txt', 'amonet/brick-9820.sh': 'brick-9820.sh.txt',
            'amonet/bootrom-step-minimal.sh': 'bootrom-step-minimal.sh.txt',
            'amonet/modules/main.py': 'main.py.txt'}
EXPECTED = {'preloader.bin': 'cefc66528a56626e65a553b7f97e0521e7939c195ce72794e7c4e14eab04619d',
            'lk.bin': '7637da8754a7494f8907d07c7b25532476959956d1cfea856ab8ea6940176056'}


def plan(entries):
    chosen = []
    for name, local in SELECTED.items():
        item = entries[name]
        if not 0 < item['uncompressed_bytes'] <= 1024*1024 or item['compressed_bytes'] > 1024*1024:
            raise ValueError('Selected reference entry exceeds cap')
        chosen.append((item, local))
    if 65557+sum(x['compressed_bytes']+8192 for x,_ in chosen) > BUDGET:
        raise ValueError('Selected ranges exceed response budget')
    return chosen


def fetch(client, output):
    if client.size != SIZE or client.limit != BUDGET or client.url != URL:
        raise ValueError('Pinned archive identity/resource gate differs')
    if output.exists():
        raise ValueError('Fresh output directory required')
    chosen = plan(zip_entries(client))
    pending = []
    for entry, local in chosen:
        data = extract_entry(client,entry)
        digest = hashlib.sha256(data).hexdigest()
        if local in EXPECTED and digest != EXPECTED[local]:
            raise ValueError('Reference binary differs from inspected candidate')
        pending.append((local,data,{'name':entry['name'],'bytes':len(data),'sha256':digest,'zip_entry':entry}))
    output.mkdir(parents=True)
    for local,data,_ in pending:
        (output/local).write_bytes(data)
    result = {'scope':'Third-party mirror selection only; not original-author/Amazon-build/recovery qualification',
              'url':URL,'archive_bytes':client.size,'response_body_bytes':client.used,
              'body_budget':BUDGET,'etag':client.etag,'ranges':client.ranges,'files':[x[2] for x in pending],
              'original_author_archive_match_verified':False,'amazon_build_identity_verified':False,
              'firmware_or_helpers_executed':False}
    (output/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch',action='store_true',help='Opt in to strict byte ranges, maximum2MiB body')
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    if not args.fetch:
        parser.error('--fetch required; full22.3MB archive is never downloaded')
    print(json.dumps(fetch(RangeClient(URL,budget=BUDGET),args.output),indent=2))


if __name__ == '__main__':
    main()
