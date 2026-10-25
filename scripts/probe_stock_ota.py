#!/usr/bin/env python3
"""Opt-in bounded ZIP range inspection; never install, execute or pack firmware."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import urllib.parse
import urllib.request
import zlib

LIMIT = 20 * 1024 * 1024
ENTRY_LIMIT = 16 * 1024 * 1024
LOADER_BUDGET = 2 * 1024 * 1024
LOADER_ENTRY_LIMIT = 1024 * 1024
LOADER_ENTRIES = {'images/preloader.bin': 'preloader.bin', 'images/lk.bin': 'lk.bin'}


class RangeClient:
    def __init__(self, url, opener=urllib.request.urlopen, budget=LIMIT):
        if type(budget) is not int or not 0 < budget <= LIMIT:
            raise ValueError('Invalid response-body budget')
        self.limit = budget
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError('Credential-free HTTPS URL required')
        self.url, self.opener, self.used = url, opener, 0
        self.cache, self.ranges = [], []
        with opener(urllib.request.Request(url, method='HEAD'), timeout=35) as response:
            if response.status != 200 or response.geturl() != url:
                raise ValueError('Unexpected HEAD status or redirect')
            self.headers = dict(response.headers.items())
            self.size = int(response.headers['Content-Length'])
            self.etag = response.headers['ETag']
            if response.headers.get('Accept-Ranges') != 'bytes' or not 22 <= self.size < 0xffffffff:
                raise ValueError('Byte ranges and non-ZIP64 size required')

    def read(self, start, length):
        if start < 0 or length <= 0 or start + length > self.size:
            raise ValueError('Range outside archive')
        for begin, data in self.cache:
            if begin <= start and start + length <= begin + len(data):
                return data[start-begin:start-begin+length]
        if self.used + length + 1 > self.limit:
            raise ValueError('Response-body budget exceeded')
        request = urllib.request.Request(self.url, headers={
            'Range': f'bytes={start}-{start+length-1}', 'If-Match': self.etag,
            'Accept-Encoding': 'identity'})
        with self.opener(request, timeout=35) as response:
            if (response.status != 206 or response.geturl() != self.url or
                    response.headers.get('Content-Range') != f'bytes {start}-{start+length-1}/{self.size}' or
                    response.headers.get('ETag') != self.etag or
                    response.headers.get('Content-Encoding', 'identity') != 'identity'):
                raise ValueError('Range/entity not honored; refusing response body')
            data = response.read(length + 1)
        self.used += len(data)
        if len(data) != length:
            raise ValueError('Unexpected range length')
        self.cache.append((start, data))
        self.ranges.append({'offset': start, 'bytes': length, 'sha256': hashlib.sha256(data).hexdigest()})
        return data


def zip_entries(client):
    length = min(client.size, 65557)
    tail = client.read(client.size-length, length)
    offset = len(tail)
    while True:
        offset = tail.rfind(b'PK\x05\x06', 0, offset)
        if offset < 0:
            raise ValueError('EOCD not found')
        if offset + 22 <= len(tail):
            end = struct.unpack_from('<4s4H2IH', tail, offset)
            if offset + 22 + end[7] == len(tail):
                break
    if end[1] or end[2] or end[3] != end[4] or not 0 < end[4] < 4096 or end[5] > 524288:
        raise ValueError('Unsupported ZIP directory')
    if end[6] + end[5] != client.size-length+offset:
        raise ValueError('Invalid directory bounds or ZIP64')
    directory = client.read(end[6], end[5])
    entries, position = {}, 0
    for _ in range(end[4]):
        if position + 46 > len(directory):
            raise ValueError('Truncated directory')
        item = struct.unpack_from('<4s6H3I5H2I', directory, position)
        finish = position + 46 + item[10] + item[11] + item[12]
        if item[0] != b'PK\x01\x02' or finish > len(directory) or item[13]:
            raise ValueError('Invalid directory record')
        name = directory[position+46:position+46+item[10]].decode('utf-8' if item[3] & 2048 else 'ascii')
        if name in entries:
            raise ValueError('Duplicate ZIP name')
        entries[name] = {'name': name, 'flags': item[3], 'method': item[4], 'crc32': item[7],
                         'compressed_bytes': item[8], 'uncompressed_bytes': item[9], 'offset': item[16]}
        position = finish
    if position != len(directory):
        raise ValueError('Unexpected directory suffix')
    return entries


def extract_entry(client, entry):
    if (entry['flags'] & 1 or entry['method'] not in (0, 8) or
            entry['compressed_bytes'] > ENTRY_LIMIT or entry['uncompressed_bytes'] > ENTRY_LIMIT):
        raise ValueError('Unsupported/encrypted/oversized entry')
    header = struct.unpack('<4s5H3I2H', client.read(entry['offset'], 30))
    if header[0] != b'PK\x03\x04' or header[2] != entry['flags'] or header[3] != entry['method'] or header[9] + header[10] > 4096:
        raise ValueError('Local header mismatch')
    fields = client.read(entry['offset']+30, header[9]+header[10])
    name = fields[:header[9]].decode('utf-8' if header[2] & 2048 else 'ascii')
    if name != entry['name']:
        raise ValueError('Local name mismatch')
    if not header[2] & 8 and (header[6], header[7], header[8]) != (entry['crc32'], entry['compressed_bytes'], entry['uncompressed_bytes']):
        raise ValueError('Local size/CRC mismatch')
    offset = entry['offset']+30+len(fields)
    packed = client.read(offset, entry['compressed_bytes']) if entry['compressed_bytes'] else b''
    if entry['method'] == 8:
        decoder = zlib.decompressobj(-15)
        data = decoder.decompress(packed, entry['uncompressed_bytes']+1)
        if not decoder.eof or decoder.unconsumed_tail or decoder.unused_data:
            raise ValueError('Invalid or oversized DEFLATE stream')
    else:
        data = packed
    if len(data) != entry['uncompressed_bytes'] or zlib.crc32(data) != entry['crc32']:
        raise ValueError('Uncompressed size/CRC mismatch')
    return data


def probe(client, boot=False):
    entries = zip_entries(client)
    properties = extract_entry(client, entries['META-INF/com/amazon/android/target.build.prop'])
    allowed = {'ro.product.manufacturer', 'ro.product.model', 'ro.product.name', 'ro.product.device',
               'ro.board.platform', 'ro.build.fingerprint', 'ro.build.version.incremental',
               'ro.build.version.sdk', 'ro.build.version.release', 'ro.build.version.fireos'}
    identity = {}
    for line in properties.decode('utf-8').splitlines():
        key, sep, value = line.partition('=')
        if sep and key in allowed:
            identity.setdefault(key, []).append(value)
    expected = {'ro.product.manufacturer': 'Amazon', 'ro.product.model': 'KFDOWI',
                'ro.product.device': 'douglas', 'ro.board.platform': 'mt8163'}
    matched = all(identity.get(key) == [value] for key, value in expected.items())
    if boot and not matched:
        raise ValueError('Wrong model identity; refusing boot.img download')
    image = extract_entry(client, entries['boot.img']) if boot else None
    report = {'scope': 'Partial OTA inspection; ZIP CRC is not signature/full-package authentication',
              'identity': identity, 'douglas_identity_matched': matched,
              'properties_sha256': hashlib.sha256(properties).hexdigest(),
              'entries': list(entries.values()), 'boot_image': None}
    if image is not None:
        report['boot_image'] = {'bytes': len(image), 'sha256': hashlib.sha256(image).hexdigest()}
    return report, image


def inspect_loader(data):
    if not 8 <= len(data) <= LOADER_ENTRY_LIMIT:
        raise ValueError('Loader size outside static inspection limit')
    markers = {}
    for marker in [b'check_part_overlapped done', b'androidboot.lk_version', b'bootopt=']:
        offsets, start = [], 0
        while len(offsets) < 32:
            index = data.find(marker, start)
            if index < 0:
                break
            offsets.append(index)
            start = index+len(marker)
        markers[marker.decode()] = {'offsets': offsets, 'occurrences_capped_at_32': len(offsets) == 32}
    magic, declared = struct.unpack_from('<II', data)
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'first64_hex': data[:64].hex(), 'first_word_le': hex(magic),
            'mtk_512_prefix_magic': magic == 0x58881688,
            'declared_payload_bytes_if_mtk_prefix': declared if magic == 0x58881688 else None,
            'declared_payload_within_file_if_mtk_prefix': declared <= len(data)-512 if magic == 0x58881688 else None,
            'markers': markers, 'signature_verified': False, 'exploitability': 'not determined',
            'installed_binary_equivalence_verified': False, 'executed': False}


def probe_loaders(client, expected_build):
    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,128}', expected_build):
        raise ValueError('Explicit expected incremental build required')
    if getattr(client, 'limit', LOADER_BUDGET) > LOADER_BUDGET:
        raise ValueError('Loader client must enforce at most 2 MiB response-body budget')
    report, _ = probe(client)
    if not report['douglas_identity_matched']:
        raise ValueError('Wrong model identity; refusing loader extraction')
    if report['identity'].get('ro.build.version.incremental') != [expected_build]:
        raise ValueError('Wrong incremental build; refusing loader extraction')
    entries = {x['name']: x for x in report['entries']}
    selected = [entries[name] for name in LOADER_ENTRIES]
    if any(e['compressed_bytes'] > LOADER_ENTRY_LIMIT or e['uncompressed_bytes'] > LOADER_ENTRY_LIMIT for e in selected):
        raise ValueError('Oversized loader entry')
    if sum(e['compressed_bytes'] for e in selected)+getattr(client, 'used', 0)+2*(4096+30+3) > min(getattr(client, 'limit', LOADER_BUDGET), LOADER_BUDGET):
        raise ValueError('Planned loader extraction exceeds response-body budget')
    payloads = {LOADER_ENTRIES[e['name']]: extract_entry(client, e) for e in selected}
    report.update(expected_incremental_build=expected_build, build_identity_matched=True,
                  loader_images={name: inspect_loader(data) for name, data in payloads.items()})
    return report, payloads


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download', action='store_true')
    images = parser.add_mutually_exclusive_group()
    images.add_argument('--loader-images', action='store_true', help='Fetch only preloader/LK after explicit model/build match; 2 MiB body cap')
    parser.add_argument('--expected-build', help='Required incremental build for loader inspection')
    images.add_argument('--boot-image', action='store_true', help='Fetch boot.img only after matching douglas identity')
    parser.add_argument('--url', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if not args.download:
        parser.error('--download required for bounded network access')
    if args.output.exists():
        parser.error('Output path exists; refusing to overwrite')
    if args.loader_images and not args.expected_build:
        parser.error('--expected-build required with --loader-images')
    client = RangeClient(args.url, budget=LOADER_BUDGET if args.loader_images else LIMIT)
    payloads = {}
    if args.loader_images:
        report, payloads = probe_loaders(client, args.expected_build)
        image = None
    else:
        report, image = probe(client, args.boot_image)
    args.output.mkdir(parents=True)
    if image is not None:
        (args.output/'boot.img').write_bytes(image)
    for name, data in payloads.items():
        (args.output/name).write_bytes(data)
    report.update(url=client.url, headers=client.headers, response_body_bytes=client.used,
                  response_body_budget=client.limit, ranges=client.ranges, full_package_downloaded=False,
                  signature_verified=False, installed_build_matched=False, hardware_tested=False)
    (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: report[k] for k in ['identity', 'boot_image', 'response_body_bytes', 'signature_verified']}, indent=2))


if __name__ == '__main__':
    main()
