import sys
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from select_kernel_build_scope import choose


class KernelBuildScope(unittest.TestCase):
    def test_usb_source_inputs_choose_one_usb_enabled_build(self):
        for path in ['projects/firetabs-android/kernel/usb-port/mt8163-usb2.patch','projects/firetabs-android/kernel/usb-port/inputs.json','scripts/apply_usb_port.py']:
            r=choose('pull_request',[path]);self.assertEqual(r,{'mode':'usb-providers','argument_profile':'none','qemu':False})

    def test_other_provider_changes_keep_existing_diagnostic_qemu(self):
        r=choose('pull_request',['scripts/apply_iommu_port.py']);self.assertEqual(r,{'mode':'diagnostic','argument_profile':'generic-force','qemu':True})

    def test_explicit_usb_build_cannot_claim_diagnostic_qemu(self):
        self.assertEqual(choose('workflow_dispatch',mode='usb-providers')['mode'],'usb-providers')
        with self.assertRaises(ValueError):choose('workflow_dispatch',mode='usb-providers',emulated_boot=True)
        with self.assertRaises(ValueError):choose('workflow_dispatch',mode='usb-providers',argument_profile='generic-force')


    def test_sym827_exact_scope_and_mixed_usb_rejection(self):
        for path in ['scripts/apply_sym827_port.py','scripts/build_sym827_provider.sh','projects/firetabs-android/kernel/regulator-port/inputs.json']:
            self.assertEqual(choose('pull_request',[path]), {'mode':'sym827-provider','argument_profile':'none','qemu':False})
            with self.assertRaises(ValueError):choose('pull_request',[path,'scripts/apply_usb_port.py'])
        self.assertEqual(choose('workflow_dispatch',mode='sym827-provider')['mode'],'sym827-provider')
        with self.assertRaises(ValueError):choose('workflow_dispatch',mode='sym827-provider',emulated_boot=True)
