"""Exercise actual source ownership, including unsafe register/protection drift."""
import importlib.util
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('domain_audit',ROOT/'scripts/audit_power_domain_contract.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)

class PowerDomainContract(unittest.TestCase):
    def setUp(self):
        self.old,self.new,self.old_macros,self.new_macros=audit.load_sources()
    def test_real_source_report(self):
        result=audit.audit()
        self.assertEqual(result,json.loads((audit.EVIDENCE/'report.json').read_text()))
        self.assertEqual(len(result['domains']),8)
        self.assertEqual(sum(x['bus_protection_mask']!=0 for x in result['domains']),3)
        self.assertTrue(all(x['legacy_active_wakeup'] and not x['candidate_active_wakeup'] for x in result['domains']))
    def test_register_drift_rejected(self):
        changed=dict(self.new_macros,SPM_DIS_PWR_CON='0x240')
        with self.assertRaisesRegex(ValueError,'Domain field mismatch: mm.ctl_offs'):
            audit.compare(self.old,self.new,self.old_macros,changed)
    def test_bus_protection_drift_rejected(self):
        changed=dict(self.new_macros,MT8163_TOP_AXI_PROT_EN_MM_M0='BIT(2)')
        with self.assertRaisesRegex(ValueError,'Bus-protection mismatch: mm'):
            audit.compare(self.old,self.new,self.old_macros,changed)
    def test_unknown_or_executable_expression_rejected(self):
        with self.assertRaises(ValueError):audit.value('UNKNOWN',{})
        with self.assertRaises(ValueError):audit.value('__import__("os")',{})
