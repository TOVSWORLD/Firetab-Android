import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_dram_caller_gate import analyze


class CallerGateTests(unittest.TestCase):
    def test_nested_stage_call_is_contained_without_executing_source(self):
        source = '''def upload_da1(self):
    if self.set_stage2_config(1):
        if self.brom_send(None):
            return True
    return False
'''
        self.assertTrue(analyze(source)['all_stage_transfers_in_truthy_initializer_branch'])

    def test_stage_call_outside_gate_is_rejected(self):
        source = '''def upload_da1(self):
    if self.set_stage2_config(1):
        pass
    return self.brom_send(None)
'''
        with self.assertRaises(ValueError):
            analyze(source)
