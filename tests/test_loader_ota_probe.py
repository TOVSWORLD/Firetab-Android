import io
from pathlib import Path
import struct
import sys
import unittest
from unittest import mock
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import probe_stock_ota as ota


class MemoryClient:
    def __init__(self, data):
        self.data, self.size, self.limit = data, len(data), ota.LOADER_BUDGET
    def read(self, start, length):
        if start < 0 or length <= 0 or start+length > self.size:
            raise ValueError('bounds')
        return self.data[start:start+length]


def fixture(model='KFDOWI', build='build1'):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('META-INF/com/amazon/android/target.build.prop',
                   f'ro.product.manufacturer=Amazon\nro.product.model={model}\nro.product.device=douglas\nro.board.platform=mt8163\nro.build.version.incremental={build}\n')
        z.writestr('images/preloader.bin', b'HEADER00check_part_overlapped done\0')
        z.writestr('images/lk.bin', struct.pack('<II', 0x58881688, 8)+bytes(504)+b'payload!')
        z.writestr('../../execute', b'never extract or execute')
    return stream.getvalue()


class LoaderOTA(unittest.TestCase):
    def test_exact_whitelist_and_build_are_required(self):
        report, images = ota.probe_loaders(MemoryClient(fixture()), 'build1')
        self.assertEqual(set(images), {'preloader.bin', 'lk.bin'})
        self.assertTrue(report['build_identity_matched'])
        self.assertEqual(report['loader_images']['preloader.bin']['markers']['check_part_overlapped done']['offsets'], [8])
        self.assertEqual(report['loader_images']['preloader.bin']['exploitability'], 'not determined')
        self.assertTrue(report['loader_images']['lk.bin']['declared_payload_within_file_if_mtk_prefix'])

    def test_identity_rejection_precedes_any_loader_extraction(self):
        for model, build in [('KFSUWI', 'build1'), ('KFDOWI', 'other')]:
            with mock.patch.object(ota, 'extract_entry', wraps=ota.extract_entry) as extraction:
                with self.assertRaises(ValueError):
                    ota.probe_loaders(MemoryClient(fixture(model, build)), 'build1')
                self.assertEqual([c.args[1]['name'] for c in extraction.call_args_list],
                                 ['META-INF/com/amazon/android/target.build.prop'])

    def test_oversize_plan_and_lax_client_are_refused(self):
        client = MemoryClient(fixture())
        entries = ota.zip_entries(client)
        entries['images/lk.bin']['uncompressed_bytes'] = ota.LOADER_ENTRY_LIMIT+1
        with mock.patch.object(ota, 'zip_entries', return_value=entries):
            with self.assertRaisesRegex(ValueError, 'Oversized'):
                ota.probe_loaders(client, 'build1')
        client.limit = ota.LIMIT
        with self.assertRaisesRegex(ValueError, '2 MiB'):
            ota.probe_loaders(client, 'build1')

    def test_custom_budget_is_enforced_before_network_request(self):
        client = object.__new__(ota.RangeClient)
        client.size, client.limit, client.used, client.cache = 100, 16, 0, []
        with self.assertRaisesRegex(ValueError, 'budget'):
            client.read(0, 16)
        with self.assertRaises(ValueError):
            ota.RangeClient('https://example.com/ota', budget=True)

    def test_marker_scan_is_capped_and_size_refused(self):
        info = ota.inspect_loader(b'check_part_overlapped done'*100)
        self.assertEqual(len(info['markers']['check_part_overlapped done']['offsets']), 32)
        self.assertEqual(info['exploitability'], 'not determined')
        for data in [b'', bytes(ota.LOADER_ENTRY_LIMIT+1)]:
            with self.assertRaises(ValueError):
                ota.inspect_loader(data)
