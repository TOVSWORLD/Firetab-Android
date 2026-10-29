import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import apply_usb_port
import test_usb_port as port_tests
LOCK=port_tests.LOCK
function=port_tests.function

class RoleErrors(unittest.TestCase):
    def test_generic_functions_unchanged_and_exact_match_scoped(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);port_tests.USBPort().tree(root);apply_usb_port.apply(root,LOCK['ack_commit'])
            new=(root/'drivers/usb/musb/mediatek.c').read_text();old=(ROOT/'evidence/usb-prerequisites/ack/mediatek.c').read_text()
            for name in ['mtk_otg_switch_set','mtk_musb_set_mode','mtk_musb_init','mtk_musb_exit']:
                self.assertEqual(function(new,name+'_legacy').replace(name+'_legacy',name),function(old,name))
            self.assertIn('{ .compatible = "mediatek,mt8163-musb", .data = &mt8163_musb_pdata }',new)
            self.assertIn('glue->strict_role_errors = soc && soc->strict_role_errors;',new)
            self.assertIn('return mtk_otg_switch_set(glue, role);',function(new,'mtk_musb_set_mode'))

    def test_all_target_and_expected_output_drift_fail_before_any_real_write(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);port_tests.USBPort().tree(root);paths=[root/LOCK['target']]+[root/p['target'] for p in LOCK['additional_patches']];before={p:p.read_bytes() for p in paths}
            paths[1].write_bytes(before[paths[1]]+b'\n')
            with self.assertRaises(ValueError):apply_usb_port.apply(root,LOCK['ack_commit'])
            self.assertEqual(paths[0].read_bytes(),before[paths[0]])
            paths[1].write_bytes(before[paths[1]])
            port=root/'port';shutil.copytree(apply_usb_port.PORT,port);lock=json.loads((port/'inputs.json').read_text());lock['additional_patches'][0]['patched_sha256']='0'*64;(port/'inputs.json').write_text(json.dumps(lock))
            with patch.object(apply_usb_port,'PORT',port),self.assertRaisesRegex(ValueError,'before source writes'):
                apply_usb_port.apply(root,LOCK['ack_commit'])
            for p in paths:self.assertEqual(p.read_bytes(),before[p])

    def test_actual_c_role_init_cleanup_transactions_in_ram(self):
        names=['mt8163_role_fault','mt8163_musb_phy_cleanup','mt8163_musb_phy_init','mt8163_otg_switch_set','mtk_otg_switch_set_legacy','mtk_otg_switch_set','musb_usb_role_sx_set','musb_usb_role_sx_get','mtk_musb_set_mode_legacy','mtk_musb_set_mode','mtk_musb_init_legacy','mtk_musb_init','mtk_musb_exit_legacy','mtk_musb_exit']
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);port_tests.USBPort().tree(root);apply_usb_port.apply(root,LOCK['ack_commit']);source=(root/'drivers/usb/musb/mediatek.c').read_text()
            code=(ROOT/'evidence/usb-role-errors/ram-harness.c').read_text().replace('/* ACTUAL_FUNCTIONS */','\n'.join(function(source,n) for n in names));c=root/'role.c';exe=root/'role';c.write_text(code)
            r=subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',str(c),'-o',str(exe)],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            r=subprocess.run([str(exe)],capture_output=True,text=True,timeout=5)
            self.assertEqual(r.returncode,0,r.stderr);self.assertIn('MT8163_ROLE_RAM_CONTROLS_PASS',r.stdout)
