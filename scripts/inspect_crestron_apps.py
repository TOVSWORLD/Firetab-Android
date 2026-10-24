#!/usr/bin/env python3
"""Static inspection of size-checked panel app archives; never installs/runs APKs.

Requires the Android SDK's apkanalyzer on PATH. Run without --download against
existing work/crestron archives, or explicitly request the locked ~79 MiB download.
Full disassembly stays in ignored work/; tracked output is metadata and findings.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'work/crestron'
EVIDENCE = ROOT / 'evidence/crestron'
ANDROID = '{http://schemas.android.com/apk/res/android}'
CLASSES = {
    'h5display': {
        'CresStoreWrapper': 'com.crestron.cresstoreredis.CresStoreWrapper',
        'CresStoreManager': 'com.crestron.cresstore.CresStoreManager',
        'SecureStorageWrapper': 'com.crestron.securestorage.SecureStorageWrapper',
        'SignalTransportFactory': 'com.crestron.signal_transport.SignalTransportFactory',
    },
    'generalweb': {
        'GeneralWebInterface': 'com.crestron.generalweb.GeneralWebInterface',
    },
    'home-panel': {
        'HomeCresStoreWrapper': 'com.crestron.cresstoreredis.CresStoreWrapper',
        'HomeSignalTransportFactory': 'com.crestron.signal_transport.SignalTransportFactory',
    },
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download', action='store_true')
    args = parser.parse_args()
    analyzer = shutil.which('apkanalyzer')
    if not analyzer:
        raise SystemExit('Android SDK apkanalyzer is required; nothing installed automatically.')
    lock = json.loads((EVIDENCE / 'downloads.lock.json').read_text())
    WORK.mkdir(parents=True, exist_ok=True)
    results = []
    for entry in lock:
        name = entry['name']
        archive = WORK / f'{name}.zip'
        if not archive.exists():
            if not args.download:
                raise SystemExit(f'Missing {archive}; see --download (total ~79 MiB).')
            with urllib.request.urlopen(entry['url'], timeout=60) as response:
                data = response.read(entry['archive_bytes'] + 1)
            if len(data) != entry['archive_bytes'] or sha256(data) != entry['archive_sha256']:
                raise SystemExit(f'Archive changed: {name}; review upstream instead of updating pins silently.')
            archive.write_bytes(data)
        data = archive.read_bytes()
        if len(data) != entry['archive_bytes'] or sha256(data) != entry['archive_sha256']:
            raise SystemExit(f'Archive does not match lock: {name}')
        with zipfile.ZipFile(archive) as outer:
            apk_members = [i for i in outer.infolist() if i.filename.endswith('.apk')]
            if len(apk_members) != 1 or apk_members[0].file_size > 100_000_000:
                raise SystemExit(f'Unexpected archive contents: {name}')
            apk_data = outer.read(apk_members[0])
        if sha256(apk_data) != entry['apk_sha256']:
            raise SystemExit(f'APK does not match lock: {name}')
        apk = WORK / f'{name}.apk'
        apk.write_bytes(apk_data)
        manifest = subprocess.check_output([analyzer, 'manifest', 'print', str(apk)], text=True)
        (EVIDENCE / f'{name}-manifest.xml').write_text(manifest)
        xml = ET.fromstring(manifest)
        sdk = xml.find('uses-sdk')
        result = dict(name=name, package=xml.attrib['package'],
                      version=xml.attrib.get(ANDROID + 'versionName'),
                      min_sdk=sdk.attrib.get(ANDROID + 'minSdkVersion'),
                      target_sdk=sdk.attrib.get(ANDROID + 'targetSdkVersion'),
                      archive_sha256=entry['archive_sha256'], apk_sha256=entry['apk_sha256'])
        with zipfile.ZipFile(apk) as inner:
            libs = sorted(n for n in inner.namelist() if n.startswith('lib/') and n.endswith('.so'))
            result['native_libraries'] = libs
            result['native_abis'] = sorted({n.split('/')[1] for n in libs})
        inspections = []
        for label, cls in CLASSES[name].items():
            code = subprocess.check_output([analyzer, 'dex', 'code', '--class', cls, str(apk)], text=True)
            path = WORK / f'{label}.smali'
            path.write_text(code)
            # Record observable patterns without shipping full disassembled binaries.
            inspections.append(dict(class_name=cls, output=str(path.relative_to(ROOT)),
                                    sha256=sha256(code.encode()),
                                    load_library_literals=re.findall(
                                        r'const-string \w+, "([^"]+)"\s+invoke-static[^\n]+System;->loadLibrary', code),
                                    references_localhost='"127.0.0.1"' in code,
                                    references_cresstore_factory='CresStoreWrapper;->createInstance' in code,
                                    references_signal_factory='SignalTransportFactory;->createSignalTransport' in code))
        result['selected_class_inspections'] = inspections
        results.append(result)
    (EVIDENCE / 'apk-inspection.json').write_text(json.dumps(results, indent=2) + '\n')
    for r in results:
        print(r['package'], r['version'], 'min', r['min_sdk'], 'target', r['target_sdk'], r['native_abis'])
    print('Static inspection complete. No APK or native library executed, installed, or modified.')


if __name__ == '__main__':
    main()
