import importlib.util
import io
from pathlib import Path
import struct
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('ota', Path(__file__).resolve().parents[1] / 'scripts/probe_stock_ota.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class MemoryClient:
    def __init__(self, data):
        self.data, self.size, self.reads = data, len(data), []
    def read(self, start, length):
        if start < 0 or length <= 0 or start + length > self.size:
            raise ValueError('bounds')
        self.reads.append((start, length))
        return self.data[start:start+length]


def fixture(model='KFDOWI'):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('META-INF/com/amazon/android/target.build.prop',
                         f'ro.product.manufacturer=Amazon\nro.product.model={model}\nro.product.device=douglas\nro.board.platform=mt8163\n')
        archive.writestr('boot.img', b'example boot payload')
        # No execution or arbitrary filesystem extraction of archive contents.
        archive.writestr('../../unwanted-script', b'never execute')
    return output.getvalue()


class OTAProbe(unittest.TestCase):
    def test_synthetic_matching_model_and_exact_boot_entry(self):
        report, data = module.probe(MemoryClient(fixture()), True)
        self.assertTrue(report['douglas_identity_matched'])
        self.assertEqual(data, b'example boot payload')

    def test_wrong_model_refuses_before_boot_entry_extraction(self):
        client = MemoryClient(fixture('KFSUWI'))
        with self.assertRaisesRegex(ValueError, 'Wrong model'):
            module.probe(client, True)

    def test_crc_and_decompression_limits_are_enforced(self):
        client = MemoryClient(fixture())
        entry = module.zip_entries(client)['boot.img']
        entry['crc32'] ^= 1
        with self.assertRaisesRegex(ValueError, 'CRC'):
            module.extract_entry(client, entry)
        entry['uncompressed_bytes'] = module.ENTRY_LIMIT + 1
        with self.assertRaisesRegex(ValueError, 'oversized'):
            module.extract_entry(client, entry)

    def test_invalid_directory_bounds_are_rejected(self):
        data = bytearray(fixture())
        offset = data.rfind(b'PK\x05\x06')
        struct.pack_into('<I', data, offset+16, 0)
        with self.assertRaises(ValueError):
            module.zip_entries(MemoryClient(data))

    def test_ignored_range_is_rejected_without_reading_body(self):
        class Response:
            def __init__(self, status, headers):
                self.status, self.headers, self.closed = status, headers, False
            def __enter__(self): return self
            def __exit__(self, *args): self.closed = True
            def geturl(self): return 'https://example.com/ota'
            def read(self, count): raise AssertionError('must not read full response')
        head = Response(200, {'Content-Length': '100', 'ETag': 'fixed', 'Accept-Ranges': 'bytes'})
        fallback = Response(200, {})
        responses = iter([head, fallback])
        client = module.RangeClient('https://example.com/ota', lambda *args, **kwargs: next(responses))
        with self.assertRaisesRegex(ValueError, 'refusing response body'):
            client.read(0, 20)
        self.assertTrue(head.closed and fallback.closed)

    def test_transfer_budget_is_checked_before_request(self):
        client = object.__new__(module.RangeClient)
        client.size, client.used, client.cache = module.LIMIT*2, module.LIMIT-1, []
        client.limit = module.LIMIT
        with self.assertRaisesRegex(ValueError, 'budget'):
            client.read(0, 1)
