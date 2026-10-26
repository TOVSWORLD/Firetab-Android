import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from build_primary_only_dtb import compare, source_audit


class PrimaryOnlyDT(unittest.TestCase):
    def fixture(self):
        before = {'/psci': {'compatible': '61'}, '/chosen': {'stdout-path': '62'}, '/memory': {'reg': '10'}}
        after = copy.deepcopy(before)
        encode = lambda s: ' '.join(f'{b:x}' for b in s.encode()+b'\0')
        after['/psci']['status'] = encode('disabled')
        after['/chosen']['bootargs'] = encode('nr_cpus=1 maxcpus=0')
        return before, after

    def test_only_two_reviewed_properties_added(self):
        result = compare(*self.fixture())
        self.assertTrue(result['original_properties_preserved'])
        self.assertFalse(result['boot_verified'])
        self.assertFalse(result['firmware_calls_globally_proven_absent'])

    def test_missing_limits_or_unrelated_changes_refused(self):
        for node, prop, value in [('/memory', 'reg', '99'), ('/psci', 'status', ''), ('/chosen', 'bootargs', 'maxcpus=1')]:
            before, after = self.fixture()
            after[node][prop] = value
            with self.assertRaises(ValueError):
                compare(before, after)

    def test_source_audit_does_not_confuse_maxcpus_with_firmware_probe_gate(self):
        facts = source_audit()
        self.assertFalse(facts['maxcpus_1_suppresses_psci_dt_init'])
        self.assertTrue(facts['maxcpus_0_skips_secondary_prepare_loop'])
