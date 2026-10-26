import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from trace_lk_bootargs import trace, required_limits


class LKBootargs(unittest.TestCase):
    def fixture(self):
        data = bytearray(485040)
        for item in json.loads((ROOT/'evidence/lk-bootargs/windows.json').read_text()):
            data[item['start']:item['end']] = bytes.fromhex(item['hex'])
        return data

    def test_selected_writer_is_replacement_with_unknown_global_lineage(self):
        facts = trace(self.fixture())
        self.assertEqual([r['text'] for r in facts['references']], ['%s %s', '/chosen', 'bootargs'])
        self.assertFalse(facts['checked_writer_preserves_existing_dt_bootargs_by_itself'])
        self.assertFalse(facts['runtime_boot_verified'])
        self.assertTrue(facts['unknowns'])

    def test_changed_property_buffer_length_or_call_rejected(self):
        for at in (0x3ed22, 0x3ed92, 0x3e5cc, 0x3e5d0, 0x3e5d8, 0x46994, 0x4699e, 0x65eb4):
            data = self.fixture()
            data[at] ^= 1
            with self.assertRaises(ValueError):
                trace(data)

    def test_unique_plain_diagnostic_arguments(self):
        facts = required_limits('console=ttyMT0 nr_cpus=1 maxcpus=0 panic=-1')
        self.assertTrue(facts['required_tokens_present_once'])
        self.assertFalse(facts['effective_kernel_arguments_verified'])

    def test_conflicting_missing_quoted_and_duplicate_limits_rejected(self):
        for text in ['maxcpus=0', 'nr_cpus=1 maxcpus=1', 'nr_cpus=1 maxcpus=0 maxcpus=4',
                     'nr_cpus=1 nr_cpus=1 maxcpus=0', '"nr_cpus=1 maxcpus=0"',
                     'nr_cpus=1 maxcpus=0\n', 'nr_cpus=1 maxcpus=0 '+('x'*16384)]:
            with self.assertRaises(ValueError):
                required_limits(text)
