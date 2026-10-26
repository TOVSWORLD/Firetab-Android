from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from synthetic_supervised_observation import run_case


class SupervisedObservationTests(unittest.TestCase):
    def test_success_parent_validates_owned_adapter_output(self):
        result=run_case('success')
        self.assertTrue(result['scenario_passed'])
        self.assertTrue(result['supervisor']['parent_validation_passed'])
        self.assertFalse(result['physical_test_ready'])

    def test_real_stalled_io_and_cleanup_children_are_reaped_and_rejected(self):
        for mode in ['io-stall','cleanup-stall']:
            result=run_case(mode)
            self.assertTrue(result['scenario_passed'])
            self.assertTrue(result['supervisor']['worker_reaped'])
            self.assertFalse(result['supervisor']['parent_validation_passed'])
            self.assertFalse(result['supervisor']['device_recovery_verified'])
