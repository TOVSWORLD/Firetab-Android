import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_usb_acm_userspace_abi import validate

class ACMUserspace(unittest.TestCase):
    def test_pinned_abi_and_configfs_contract(self):
        self.assertFalse(validate()['runtime_qualified'])

    def test_actual_setup_and_filesystem_code_with_ram_syscalls(self):
        cc = shutil.which('cc')
        self.assertIsNotNone(cc)
        with tempfile.TemporaryDirectory() as tmp:
            for name, marker in [('setup', 'FIRETABS_ACM_SETUP_RAM_CONTROLS_PASS'),
                                 ('fs', 'FIRETABS_ACM_FS_RAM_CONTROLS_PASS')]:
                binary = Path(tmp) / name
                result = subprocess.run([cc, '-std=c11', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', '-I', str(ROOT / 'projects/firetabs-android/diagnostic-usb'),
                    str(ROOT / ('evidence/usb-acm-userspace/' + name + '-ram.c')), '-o', str(binary)],
                    capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                run = subprocess.run([str(binary)], capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertIn(marker, run.stdout)

if __name__ == '__main__':
    unittest.main()
