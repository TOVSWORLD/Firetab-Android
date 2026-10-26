from pathlib import Path
import shutil
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from synthetic_acquisition_session import run_case,provenance
ROOT=Path(__file__).resolve().parents[1]


class SyntheticSessionTests(unittest.TestCase):
    def run_fixture(self,mode):
        (ROOT/'out').mkdir(exist_ok=True)
        root=Path(tempfile.mkdtemp(prefix='session-tests-',dir=ROOT/'out'))
        self.addCleanup(shutil.rmtree,root)
        return run_case(root/'session',mode,0.6 if mode=='stall' else 5),root/'session'

    def test_complete_generated_regions_pass_capture_hash_and_gpt_in_quarantine(self):
        report,path=self.run_fixture('success')
        self.assertTrue(report['scenario_passed']);self.assertTrue(report['host_session_accepted'])
        self.assertTrue(report['quarantine_retained']);self.assertFalse(report['physical_test_ready'])
        self.assertEqual(len(list(path.rglob('*.bin'))),3)
        self.assertEqual(report['provenance'],provenance())

    def test_short_response_is_rejected_without_completed_region_files(self):
        report,path=self.run_fixture('short')
        self.assertTrue(report['scenario_passed']);self.assertFalse(report['host_session_accepted'])
        self.assertEqual(report['supervision']['failure'],'worker_failed_or_no_completion')
        self.assertEqual(list(path.rglob('*.bin')),[])

    def test_stalled_packet_callback_is_stopped_by_worker_not_soft_deadline(self):
        report,path=self.run_fixture('stall')
        self.assertTrue(report['scenario_passed']);self.assertTrue(report['supervision']['timed_out'])
        self.assertFalse(report['host_session_accepted']);self.assertEqual(list(path.rglob('*.bin')),[])
