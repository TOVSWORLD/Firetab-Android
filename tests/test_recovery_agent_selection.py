import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_recovery_agent_selection import selector_facts


class AgentSelectionTests(unittest.TestCase):
    SOURCE = '''
class Selector:
 def parse_da_loader(self, da, ldr):
  if da.hw_sub_code == da.hw_sub_code: return True
 def setup(self, loader):
  if loader.hw_version <= self.hwver:
   return loader.sw_version <= self.swver
'''
    def test_tautology_is_distinct_from_actual_device_failure(self):
        facts = selector_facts(self.SOURCE)
        self.assertTrue(facts['dedup_subcode_self_comparison_lines'])
        self.assertFalse(facts['setup_reads_subcode'])
        self.assertFalse(facts['actual_device_selection_verified'])
        self.assertFalse(facts['subcode_compatibility_failure_observed_on_device'])

    def test_revised_selector_requires_new_audit(self):
        with self.assertRaises(ValueError):
            selector_facts(self.SOURCE.replace('== da.hw_sub_code', '== ldr.hw_sub_code'))
