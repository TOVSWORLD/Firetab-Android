"""Guard reviewed order/alias evidence without pretending to run a kernel."""
import importlib.util
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('transition_audit',ROOT/'scripts/audit_power_transition_order.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)

class PowerTransitionOrder(unittest.TestCase):
    def test_actual_source_report(self):
        r=audit.audit();self.assertEqual(r,json.loads((audit.EVIDENCE/'report.json').read_text()))
        self.assertEqual(r['control_writes']['legacy_on'],r['control_writes']['ack_on'])
        self.assertNotEqual(r['control_writes']['legacy_off'],r['control_writes']['ack_off'])
        self.assertFalse(r['wakeup_qualification']['capability_change_justified'])
    def test_legacy_predicate_edges(self):
        self.assertFalse(audit.legacy_resume_needed(False,True,True))
        self.assertTrue(audit.legacy_resume_needed(True,False,False))
        self.assertFalse(audit.legacy_resume_needed(True,False,True))
        self.assertTrue(audit.legacy_noirq_skip(False,True,True))
        self.assertFalse(audit.legacy_noirq_skip(False,True,False))
    def test_mux_register_drift_rejected(self):
        old=(ROOT/'evidence/kernel-audit/legacy/drivers/clk/mediatek/clk-mt8163.c').read_text()
        new=(ROOT/'projects/firetabs-android/kernel/clock-port/overlay/drivers/clk/mediatek/clk-mt8163-topckgen.c').read_text()
        changed=new.replace('0x0050, 24, 2, 31, 0x0004, 7','0x0060, 24, 2, 31, 0x0004, 7')
        self.assertNotEqual(new,changed)
        with self.assertRaises(ValueError):audit.mux_contract(old,changed)
    def test_nonunit_parent_alias_rejected(self):
        old=(ROOT/'evidence/kernel-audit/legacy/drivers/clk/mediatek/clk-mt8163.c').read_text()
        new=(ROOT/'projects/firetabs-android/kernel/clock-port/overlay/drivers/clk/mediatek/clk-mt8163-topckgen.c').read_text()
        changed=old.replace('"mmpll_ck", "mmpll", 1, 1','"mmpll_ck", "mmpll", 1, 2')
        self.assertNotEqual(old,changed)
        with self.assertRaises(ValueError):audit.mux_contract(changed,new)
