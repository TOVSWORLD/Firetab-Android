import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_recovery_bootstrap import local_reachability, partition_switch_facts


class BootstrapAuditTests(unittest.TestCase):
    def test_reachable_write_and_external_calls_are_not_hidden(self):
        source = '''
class Example:
 def upload_da(self):
  self.stage()
 def stage(self):
  self.writeflash()
  self.agent.run()
  self.upload_da()
 def writeflash(self): pass
 def unrelated(self): self.formatflash()
'''
        result = local_reachability(source, 'upload_da')
        self.assertEqual(result['reachable_storage_write_methods'], ['writeflash'])
        self.assertIn('self.agent.run', result['external_calls_not_resolved'])
        self.assertNotIn('unrelated', result['same_file_reachable_methods'])

    def test_discarded_selection_failure_and_changed_source(self):
        source = '''
class Example:
 def readflash(self):
  self.sdmmc_switch_part(1)
  self.read()
 def sdmmc_switch_part(self, part):
  return False
'''
        result = partition_switch_facts(source)
        self.assertTrue(result['wrong_region_read_possible_if_selection_fails'])
        self.assertFalse(result['failure_observed_on_device'])
        with self.assertRaises(ValueError):
            partition_switch_facts(source.replace('self.sdmmc_switch_part(1)',
                'assert self.sdmmc_switch_part(1)'))
