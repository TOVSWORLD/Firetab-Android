import importlib.util
from pathlib import Path
import sys
import unittest

spec = importlib.util.spec_from_file_location('stock_facts', Path(__file__).resolve().parents[1] / 'scripts/collect_stock_facts.py')
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class FakeReader:
    def __init__(self, model='KFDOWI', device='douglas'):
        self.calls = []
        self.model, self.device = model, device

    def __call__(self, args):
        self.calls.append(args)
        key = args[-1]
        values = {'ro.product.manufacturer': b'Amazon', 'ro.product.model': self.model.encode(),
                  'ro.product.device': self.device.encode(), '/proc/cmdline': b'console=ttyS0 androidboot.serialno=SECRET bootopt=64S3 unknown=PRIVATE',
                  '/proc/device-tree/': b'memory@40000000 chosen serial-number',
                  '/proc/device-tree/version': b'hvt\0',
                  '/proc/device-tree/memory@40000000/reg': bytes.fromhex('00000000400000000000000060000000')}
        return module.Result(0, values[key]) if key in values else module.Result(1, stderr=b'unavailable SECRET')


class StockFacts(unittest.TestCase):
    def test_collects_only_allowlisted_read_commands(self):
        reader = FakeReader()
        result = module.collect(reader)
        self.assertNotIn('SECRET', str(result))
        self.assertNotIn('PRIVATE', str(result))
        for args in reader.calls:
            self.assertIn(args[0], ['shell', 'exec-out'])
            self.assertIn(args[1], ['getprop', 'cat', 'ls', 'uname'])
        memory = next(x for x in result['records'] if x['name'].endswith('/reg'))
        self.assertTrue(memory['available'])
        self.assertEqual(memory['hex'], '00000000400000000000000060000000')
        version = next(x for x in result['records'] if x['name'] == '/proc/device-tree/version')
        self.assertEqual(version['hex'], '68767400')

    def test_loader_versions_are_retained_without_reading_serial(self):
        fake = FakeReader()
        versions = {'ro.boot.pl_version': b'6', 'ro.boot.lk_version': b'2',
                    'ro.boot.tee_version': b'259', 'ro.build.version.fireos': b'5.3.7.3'}
        def reader(args):
            if args[:2] == ['shell', 'getprop'] and args[-1] in versions:
                fake.calls.append(args)
                return module.Result(0, versions[args[-1]])
            return fake(args)
        records = {x['name']: x for x in module.collect(reader)['records']}
        for key, value in versions.items():
            self.assertEqual(records[key]['text'], value.decode())
        self.assertFalse(any('serial' in x[-1] for x in fake.calls))

    def test_legacy_zero_exit_errors_are_unavailable_and_not_saved(self):
        fake = FakeReader()
        def reader(args):
            if args[-1] in ['/proc/iomem', '/proc/cmdline'] or 'uname' in args:
                return module.Result(0, b'/system/bin/sh: cat: Permission denied SECRET')
            return fake(args)
        report = module.collect(reader)
        self.assertNotIn('SECRET', str(report))
        for record in report['records']:
            if record['name'] in ['/proc/iomem', '/proc/cmdline', 'uname -r', 'uname -m']:
                self.assertFalse(record['available'])

    def test_partinfo_metadata_or_denial_never_requests_raw_blocks(self):
        for answer in [module.Result(0, b'Name Start Size\nlk 0x100000 0x80000\n'),
                       module.Result(0, b'cat: /proc/partinfo: Permission denied SECRET')]:
            fake = FakeReader()
            def reader(args):
                if args == ['shell', 'cat', '/proc/partinfo']:
                    fake.calls.append(args)
                    return answer
                return fake(args)
            result = module.collect(reader)
            record = next(x for x in result['records'] if x['name'] == '/proc/partinfo')
            self.assertEqual(record['available'], answer.stdout.startswith(b'Name '))
            self.assertNotIn('SECRET', str(result))
            self.assertFalse(any('/dev/block' in a or a == 'su' for call in fake.calls for a in call))

    def test_refuses_wrong_device_before_other_reads(self):
        reader = FakeReader(model='OTHER', device='other')
        with self.assertRaises(ValueError):
            module.collect(reader)
        self.assertEqual(len(reader.calls), 3)

    def test_no_serial_or_chosen_value_reads(self):
        reader = FakeReader()
        module.collect(reader)
        self.assertFalse(any(x[-1].endswith('/serial-number') or '/chosen/' in x[-1] for x in reader.calls))

    def test_memory_node_queries_are_bounded(self):
        fake = FakeReader()
        def reader(args):
            if args == ['shell', 'ls', '/proc/device-tree/']:
                return module.Result(0, ' '.join(f'memory@{x:x}' for x in range(20)).encode())
            return fake(args)
        result = module.collect(reader)
        selection = next(x for x in result['records'] if x['name'] == 'DT memory node selection')
        self.assertTrue(selection['limited'])
        self.assertEqual(len(selection['collected_nodes']), 8)
        self.assertEqual(sum('/memory@' in x[-1] for x in fake.calls), 24)

    def test_refuses_ambiguous_serial(self):
        with self.assertRaises(ValueError):
            module.ADBReader('adb', 'SERIAL; reboot')

    def test_host_output_limit_is_enforced(self):
        result = module.bounded_run([sys.executable, '-c', 'import sys; sys.stdout.write("x"*1000000)'], limit=1024)
        self.assertTrue(result.truncated)
        self.assertLessEqual(len(result.stdout), 1024)

    def test_host_timeout_is_enforced(self):
        result = module.bounded_run([sys.executable, '-c', 'import time; time.sleep(1)'], timeout=0.05)
        self.assertTrue(result.timed_out)
