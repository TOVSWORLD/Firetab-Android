import unittest
from synthetic_supervised_diagnostic import run_case


class SupervisedDiagnosticTests(unittest.TestCase):
    def test_complete_synthetic_frame_capture_validated_by_parent(self):
        result=run_case('success')
        self.assertTrue(result['scenario_passed'])
        self.assertTrue(result['supervisor']['parent_validation_passed'])
        self.assertFalse(result['supervisor']['output_published'])

    def test_actual_stalls_reaped_and_never_accepted(self):
        for mode in ('write-stall','read-stall','cleanup-stall'):
            with self.subTest(mode=mode):
                result=run_case(mode)
                self.assertTrue(result['scenario_passed'])
                self.assertTrue(result['supervisor']['worker_reaped'])
                self.assertFalse(result['supervisor']['parent_validation_passed'])
                self.assertFalse(result['forced_stop_confirms_device_cleanup'])
