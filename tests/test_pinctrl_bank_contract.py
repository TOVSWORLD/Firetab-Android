"""Reject source drift that changes GPIO geometry or EINT register ownership."""
import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pin_audit',ROOT/'scripts/audit_pinctrl_references.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)

class PinctrlBankContract(unittest.TestCase):
    def setUp(self):
        self.old=(ROOT/'evidence/kernel-audit/legacy/drivers/pinctrl/mediatek/pinctrl-mt8163.c').read_text()
        self.new=(ROOT/'projects/firetabs-android/kernel/pinctrl-port/overlay/drivers/pinctrl/mediatek/pinctrl-mt8163.c').read_text()
        self.ack=(ROOT/'evidence/pinctrl-port/ack/drivers/pinctrl/mediatek/mtk-eint.c').read_text()
    def test_actual_sources(self):
        r=audit.bank_contract(self.old,self.new,self.ack)
        self.assertEqual(len(r['identical_legacy_ack_eint_offsets']),18)
        self.assertEqual(r['gpio_and_eint_port_masks'],[15,7])
    def test_reject_changed_ack_register(self):
        with self.assertRaisesRegex(ValueError,'offset mismatch: ack'):
            audit.bank_contract(self.old,self.new,self.ack.replace('.ack       = 0x040','.ack       = 0x044'))
    def test_reject_changed_capacity(self):
        with self.assertRaisesRegex(ValueError,'geometry mismatch: ap_num'):
            audit.bank_contract(self.old,self.new.replace('.ap_num = 169','.ap_num = 168'),self.ack)
