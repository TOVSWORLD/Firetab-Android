from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from synthetic_observation_package import run_case


class ObservationPackageTests(unittest.TestCase):
    def test_integrated_success_stays_synthetic_and_unqualified(self):
        result=run_case('success')
        self.assertTrue(result['scenario_passed'])
        self.assertTrue(result['observation_decoded'])
        self.assertFalse(result['bootstrap_authorized'])
        self.assertFalse(result['mode_evidence']['protocol_mode_verified'])
        self.assertEqual(len(result['source_sha256']),5)

    def test_fault_scenarios_stop_after_first_query_and_discard_results(self):
        for mode,error in [('bad-echo','ValueError'),('late','TimeoutError')]:
            result=run_case(mode)
            self.assertTrue(result['scenario_passed'])
            self.assertFalse(result['observation_decoded'])
            self.assertIsNone(result['observation'])
            self.assertIsNone(result['mode_evidence'])
            self.assertEqual(result['symbolic_queries'],['hardware_code'])
            self.assertEqual(result['error_class'],error)
            self.assertEqual(result['session_state'],'invalid')
