#!/usr/bin/env python3
"""Verify bounded official-hosted loader digest matches; never qualifies installation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
HOSTS={'fireos-tablet-src.s3.amazonaws.com','fireos-tablet-updates.s3.us-west-2.amazonaws.com'}
MIRROR={'preloader.bin':'cefc66528a56626e65a553b7f97e0521e7939c195ce72794e7c4e14eab04619d',
        'lk.bin':'7637da8754a7494f8907d07c7b25532476959956d1cfea856ab8ea6940176056'}
CURRENT={'preloader.bin':'b30d8d1292c620ed372050549cff27f153fec6c2467484b9202265c0a364fea5',
         'lk.bin':'4ca0cca7ae9af6e959dc848b9ca002624c62e1bb93c83c0ecc89bae8d2186b08'}


def verify(report,expected):
    url=urlsplit(report['url'])
    if url.scheme!='https' or url.hostname not in HOSTS or url.username or url.password:
        raise ValueError('Expected known public Amazon source host')
    facts=report['identity']
    for key,value in [('ro.product.device','douglas'),('ro.product.model','KFDOWI'),
                      ('ro.product.manufacturer','Amazon'),('ro.board.platform','mt8163'),
                      ('ro.build.version.incremental',expected)]:
        if set(facts.get(key,[]))!={value}:raise ValueError('Model/build metadata mismatch')
    if not report['douglas_identity_matched'] or report['full_package_downloaded'] or report['signature_verified'] or report['hardware_tested']:
        raise ValueError('Unexpected scope/qualification flag')
    used,budget=report['response_body_bytes'],report['response_body_budget']
    if not 0<used<=budget==2*1024*1024 or sum(x['bytes'] for x in report['ranges'])!=used:
        raise ValueError('Invalid range-response resource account')
    if set(report['loader_images'])!=set(MIRROR):raise ValueError('Unexpected loader set')
    matches={}
    for name,item in report['loader_images'].items():
        if not 0<item['bytes']<=1024*1024 or not re.fullmatch('[0-9a-f]{64}',item['sha256']):
            raise ValueError('Invalid bounded loader digest')
        matches[name]={'bytes':item['bytes'],'sha256':item['sha256'],
                       'matches_mirrored_candidate':item['sha256']==MIRROR[name],
                       'matches_current_stock_candidate':item['sha256']==CURRENT[name]}
    return {'official_host_url':report['url'],'verified_metadata_build':expected,'matches':matches,
            'response_body_bytes':used,'full_ota_or_signature_verified':False,
            'original_helper_archive_authenticity_verified':False,
            'installed_antirollback_compatibility_verified':False,'downgrade_or_recovery_ready':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--expected-build',required=True)
    args=parser.parse_args()
    result=verify(json.loads(args.report.read_text()),args.expected_build)
    result['report_sha256']=hashlib.sha256(args.report.read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
