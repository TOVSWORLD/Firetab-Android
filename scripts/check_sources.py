#!/usr/bin/env python3
"""Validate source pins, ELF bitness, vendor inheritance and manifest paths offline."""
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
for entry in json.loads((root / 'evidence/sources.lock.json').read_text()):
    head = subprocess.check_output(['git', '-C', str(root / entry['directory']), 'rev-parse', 'HEAD'], text=True).strip()
    assert head == entry['commit'], entry['directory']
for manifest in (root / 'manifests').glob('*.xml'):
    projects = ET.parse(manifest).getroot().findall('project')
    paths = [x.attrib['path'] for x in projects]
    assert len(paths) == len(set(paths)), manifest
    assert all(len(x.attrib['revision']) == 40 for x in projects), manifest
device = root / 'sources/device-douglas/device.mk'
assert 'inherit-product, vendor/amazon/douglas/douglas-vendor.mk' in device.read_text()
vendor = root / 'sources/android_vendor_amazon_mt8163-common/proprietary'
for directory, elf_class in [('lib', 1), ('lib64', 2)]:
    for filename in ['egl/libGLES_mali.so', 'hw/gralloc.mt8163.mali.so', 'hw/hwcomposer.mt8163.so']:
        data = (vendor / directory / filename).read_bytes()
        assert data[:4] == b'\x7fELF' and data[4] == elf_class, filename
print('PASS: source pins, manifest paths, corrected inheritance, six ARM/ARM64 graphics ELF headers.')
print('No Android compilation or runtime validation performed.')
