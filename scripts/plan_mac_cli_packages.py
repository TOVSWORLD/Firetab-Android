#!/usr/bin/env python3
"""Read cached official metadata only; never download/install wheels or use USB."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={'pycryptodome':'3.24.1','pycryptodomex':'3.24.1','colorama':'0.4.6','pyserial':'3.5','pyusb':'1.3.1'}


def candidate(metadata, name, version):
    if metadata['info']['name'].lower()!=name or metadata['info']['version']!=version:
        raise ValueError('Unexpected package/version metadata')
    matches=[]
    for file in metadata['urls']:
        filename=file['filename']
        suffix='-cp37-abi3-macosx_10_9_universal2.whl' if name.startswith('pycrypto') else '-none-any.whl'
        if not filename.endswith(suffix) or file.get('yanked'):
            continue
        if not name.startswith('pycrypto') and '-py3-' not in filename and '-py2.py3-' not in filename:
            continue
        matches.append(file)
    if len(matches)!=1:
        raise ValueError('Expected one explicitly scoped candidate wheel')
    file=matches[0]
    return {'package':name,'version':version,'filename':file['filename'],'bytes':file['size'],
            'url':file['url'],'sha256':file['digests']['sha256'],
            'requires_python':file.get('requires_python'),
            'requires_dist':metadata['info']['requires_dist'],
            'wheel_downloaded':False,'runtime_compatibility_verified':False}


def main():
    index=json.loads((ROOT/'evidence/mac-cli-resources/metadata-index.json').read_text())
    items=[]
    for record in index:
        name,version=record['package'],record['version']
        if EXPECTED.get(name)!=version:raise ValueError('Unexpected candidate package')
        raw=(ROOT/f'out/mac-cli-plan/{name}-{version}.json').read_bytes()
        if len(raw)!=record['bytes'] or hashlib.sha256(raw).hexdigest()!=record['sha256']:
            raise ValueError('Cached metadata identity mismatch')
        items.append(candidate(json.loads(raw),name,version))
    if {x['package'] for x in items}!=set(EXPECTED):raise ValueError('Incomplete package plan')
    print(json.dumps({'scope':'Candidate package/resource metadata, not an installation lock',
        'packages':items,'candidate_wheel_download_bytes':sum(x['bytes'] for x in items),
        'metadata_body_bytes':sum(x['bytes'] for x in index),
        'native_usb_backend_included':False,'native_backend_download_bytes_known':False,
        'expanded_install_disk_bytes_known':False,'installation_performed':False,
        'mac_cli_verified':False,'physical_test_ready':False},indent=2))


if __name__=='__main__':
    main()
