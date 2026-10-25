"""Rejection paths matter: gates must fail for corrupt or unsupported claims."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('gate', Path(__file__).resolve().parents[1] / 'scripts/ci.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class GateTests(unittest.TestCase):
    def test_large_deletion_and_truncation(self):
        old = b'line\n' * 400
        self.assertTrue(gate.truncation(old, b''))
        self.assertTrue(gate.truncation(old, b'line\n' * 200))
        self.assertFalse(gate.truncation(old, b'line\n' * 350))

    def test_unsafe_source_paths(self):
        for path in ['/tmp/escape', 'sources/../../escape', '']:
            with self.assertRaises(ValueError):
                gate.safe_path(path)
        self.assertEqual(gate.safe_path('sources/device-douglas'), 'sources/device-douglas')

    def test_empty_or_explicitly_unimplemented_code(self):
        for body in ['pass', '...', 'raise NotImplementedError("missing driver")']:
            with self.assertRaises(ValueError):
                gate.check_python('def driver():\n    ' + body, 'driver.py')
        gate.check_python('def driver():\n    return 42', 'driver.py')

    def test_passing_claim_without_logs(self):
        record = copy.deepcopy(gate.load('projects/firetabs-android/validation.json'))
        record['stages']['kernel_compile'] = {'status': 'passed', 'revision': 'a' * 40, 'evidence': []}
        with self.assertRaises(ValueError):
            gate.validate_progress(record, 'firetabs-android')

    def test_boot_cannot_precede_compilation(self):
        record = copy.deepcopy(gate.load('projects/firetabs-android/validation.json'))
        record['stages']['boot'] = {'status': 'passed', 'revision': 'a' * 40, 'evidence': [{'path': 'README.md', 'sha256': 'a' * 64}]}
        with self.assertRaisesRegex(ValueError, 'earlier validation'):
            gate.validate_progress(record, 'firetabs-android')

    def test_missing_evidence_fails(self):
        record = copy.deepcopy(gate.load('projects/crestron-panel/validation.json'))
        record['stages']['client_runtime'] = {'status': 'passed', 'revision': 'a' * 40, 'evidence': [{'path': 'absent.log', 'sha256': 'a' * 64}]}
        with self.assertRaisesRegex(ValueError, 'Missing/unsafe evidence'):
            gate.validate_progress(record, 'crestron-panel')


if __name__ == '__main__':
    unittest.main()
