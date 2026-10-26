from pathlib import Path
import shutil
import signal
import sys
import tempfile
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from offline_worker_supervisor import supervise_worker


def synthetic_complete(directory):
    (directory/'data').write_bytes(b'complete fake bytes')


def synthetic_failed(directory):
    (directory/'partial').write_bytes(b'partial')
    raise RuntimeError('private synthetic details must not escape')


def synthetic_stalled(directory):
    (directory/'partial').write_bytes(b'partial')
    signal.signal(signal.SIGTERM,signal.SIG_IGN)
    while True:time.sleep(0.02)


class WorkerSupervisionTests(unittest.TestCase):
    def test_completed_fake_worker_remains_quarantined_after_parent_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            outcome=supervise_worker(synthetic_complete,
                lambda p:(p/'data').read_bytes()==b'complete fake bytes',tmp,timeout_seconds=5)
            self.assertTrue(outcome.summary['worker_completed'])
            self.assertTrue(outcome.summary['parent_validation_passed'])
            self.assertFalse(outcome.summary['output_published'])
            self.assertFalse(outcome.summary['device_recovery_verified'])
            self.assertIsNotNone(outcome.quarantine_directory)
            shutil.rmtree(outcome.quarantine_directory)

    def test_stalled_fake_worker_is_reaped_and_partial_output_never_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            def forbidden(path):raise AssertionError('Timed-out output must not be validated')
            outcome=supervise_worker(synthetic_stalled,forbidden,tmp,timeout_seconds=1)
            self.assertTrue(outcome.summary['timed_out'])
            self.assertTrue(outcome.summary['worker_reaped'])
            self.assertTrue(outcome.summary['kill_requested'])
            self.assertFalse(outcome.summary['parent_validation_passed'])
            self.assertLess(outcome.summary['elapsed_seconds'],4)
            self.assertEqual(list(Path(tmp).iterdir()),[])

    def test_worker_error_or_validator_rejection_does_not_accept_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            for worker in (synthetic_failed,synthetic_complete):
                outcome=supervise_worker(worker,lambda p:False,tmp,timeout_seconds=5)
                self.assertFalse(outcome.summary['parent_validation_passed'])
                self.assertIsNone(outcome.quarantine_directory)
                self.assertNotIn('private',str(outcome.summary))
                self.assertEqual(list(Path(tmp).iterdir()),[])

    def test_invalid_unbounded_or_nan_deadline_rejected_before_worker(self):
        with tempfile.TemporaryDirectory() as tmp:
            for seconds in (0,31,float('nan'),True):
                with self.assertRaises(ValueError):supervise_worker(synthetic_complete,lambda p:True,tmp,timeout_seconds=seconds)
            self.assertEqual(list(Path(tmp).iterdir()),[])
