import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import usb_acm_config
from select_kernel_build_scope import choose


class ACMProfile(unittest.TestCase):
    def fixture(self):
        # Policy-shaped synthetic input; only the actual Linux run resolves Kconfig.
        return (usb_acm_config.PROFILE/'fragment.config').read_text()

    def test_model_builtin_success_is_not_gadget_or_runtime_admission(self):
        result = usb_acm_config.check(self.fixture())
        self.assertTrue(result['passed'])
        self.assertFalse(result['gadget_userspace_implemented'])
        self.assertFalse(result['transport_qualified'])

    def test_modular_missing_forbidden_or_security_weakening_rejected(self):
        required, lock = usb_acm_config.requirements()
        for name in lock['required_builtin']:
            for value in ['m', 'n']:
                text = self.fixture().replace('CONFIG_'+name+'=y', 'CONFIG_'+name+'='+value)
                with self.subTest(symbol=name,value=value),self.assertRaises(ValueError):
                    usb_acm_config.check(text)
        for name in lock['required_disabled']:
            text=self.fixture().replace('# CONFIG_'+name+' is not set','CONFIG_'+name+'=y')
            with self.subTest(symbol=name),self.assertRaises(ValueError):usb_acm_config.check(text)
        with self.assertRaises(ValueError):usb_acm_config.check(self.fixture().replace('CONFIG_SECURITY_SELINUX=y',''))
        with self.assertRaises(ValueError):usb_acm_config.check(self.fixture()+'# CONFIG_USB_CONFIGFS is not set\n')
        with self.assertRaises(ValueError):usb_acm_config.check(self.fixture().replace('selinux,',''))
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);shutil.copytree(usb_acm_config.PROFILE,root/'profile')
            (root/'profile/fragment.config').write_text((root/'profile/fragment.config').read_text()+'# CONFIG_SECURITY_SELINUX is not set\n')
            with patch.object(usb_acm_config,'PROFILE',root/'profile'),self.assertRaises(ValueError):
                usb_acm_config.requirements()

    def test_actual_failed_resolved_config_remains_rejected(self):
        text=(ROOT/'evidence/usb-acm-profile/failed-resolved.config').read_text()
        for name in ['USB_CONFIGFS','USB_LIBCOMPOSITE','USB_F_ACM','USB_U_SERIAL']:
            self.assertIn('CONFIG_'+name+'=y',text)
        with self.assertRaisesRegex(ValueError,'SECURITY_NETWORK|SECURITY_SELINUX|LSM'):
            usb_acm_config.check(text)

    def test_acm_selection_is_one_explicit_build_without_qemu(self):
        for path in ['scripts/usb_acm_config.py','projects/firetabs-android/kernel/usb-acm/fragment.config','projects/firetabs-android/kernel/usb-acm/profile.json']:
            self.assertEqual(choose('pull_request',[path,'scripts/apply_usb_port.py']),
                             {'mode':'usb-acm-diagnostic','argument_profile':'none','qemu':False})
        self.assertEqual(choose('workflow_dispatch',mode='usb-acm-diagnostic')['mode'],'usb-acm-diagnostic')
        for kwargs in [{'emulated_boot':True},{'argument_profile':'generic-force'}]:
            with self.assertRaises(ValueError):choose('workflow_dispatch',mode='usb-acm-diagnostic',**kwargs)
