#!/usr/bin/env python3
"""Compare exact cached reference/current preloader bytes, never generate or apply patches."""
import argparse
import hashlib
import json
from pathlib import Path
from inspect_loader_layout import checked_file,preloader_layout

OLD = 'cefc66528a56626e65a553b7f97e0521e7939c195ce72794e7c4e14eab04619d'
CURRENT = 'b30d8d1292c620ed372050549cff27f153fec6c2467484b9202265c0a364fea5'


def compare(old,current):
    layouts = [preloader_layout(x) for x in (old,current)]
    if any(x['declared_load_base'] != 0x200d00 for x in layouts):
        raise ValueError('Unexpected declared reference mapping')
    sites=[]
    for address in (0x201934,0x217420,0x21b970,0x20a204):
        offset=address-0x200d00
        if any(not x['payload_offset'] <= offset < x['declared_code_end_exclusive']-0x200d00-16 for x in layouts):
            raise ValueError('Reference site outside declared code')
        a,b=old[offset:offset+16],current[offset:offset+16]
        sites.append({'declared_address':hex(address),'file_offset':offset,'older_window_sha256':hashlib.sha256(a).hexdigest(),
                      'current_window_sha256':hashlib.sha256(b).hexdigest(),'same_bytes':a==b,'function_identity_or_patch_safety_verified':False})
    return {'scope':'Static older mirror/current layout comparison; not installed boot-chain compatibility',
            'older_layout':layouts[0],'current_layout':layouts[1],'sites':sites,
            'older_marker_offset':old.find(b'check_part_overlapped done'),
            'current_marker_offset':current.find(b'check_part_overlapped done'),
            'marker_proves_exploitability':False,'older_original_build_verified':False,
            'newer_reference_patch_set_qualified_for_older_mirror':False,
            'recoverable_loading_path_qualified':False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--older',type=Path,required=True)
    p.add_argument('--current',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():p.error('Fresh output required')
    report={'older_sha256':OLD,'current_sha256':CURRENT,'facts':compare(checked_file(a.older,OLD),checked_file(a.current,CURRENT)),
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
