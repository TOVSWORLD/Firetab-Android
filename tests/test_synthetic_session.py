from pathlib import Path
import json
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

    def test_retained_scenarios_share_executed_source_and_keep_live_gates_false(self):
        folder=ROOT/'evidence/synthetic-acquisition-session'
        records={mode:json.loads((folder/(mode+'.json')).read_text()) for mode in ('success','short','stall')}
        self.assertEqual({r['project_revision'] for r in records.values()},
                         {'e2b62d49840d7a162023dee83f845b2e2cc5051e'})
        self.assertEqual(records['success']['provenance'],records['short']['provenance'])
        self.assertEqual(records['success']['provenance'],records['stall']['provenance'])
        for record in records.values():
            self.assertTrue(record['scenario_passed']);self.assertTrue(record['working_tree_clean'])
            self.assertFalse(record['device_accessed']);self.assertFalse(record['physical_test_ready'])
        self.assertTrue(records['success']['validated_capture_metadata']['user']['checks']['gpt']['both_headers_and_tables_valid'])
        self.assertFalse(records['short']['host_session_accepted'])
        self.assertTrue(records['stall']['supervision']['timed_out'])
