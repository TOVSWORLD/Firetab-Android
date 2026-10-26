import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from audit_cpu_startup_contract import audit


class CPUStartupContract(unittest.TestCase):
    def test_reference_path_difference_and_unknown_monitor(self):
        result = audit()
        self.assertFalse(result['ack_supports_mt_boot_method'])
        self.assertTrue(result['ack_legacy_psci_ids_supported'])
        self.assertEqual(result['ack_arm64_psci_v02_cpu_on_id'], '0xc4000003')
        self.assertEqual(result['stock_explicit_cpu_on_id'], '0x84000003')
        self.assertIsNone(result['installed_monitor_supports_donor_v02_and_64bit_call'])
        self.assertFalse(result['primary_entry_verified'])
        self.assertFalse(result['secondary_cpu_boot_verified'])
        self.assertFalse(result['legacy_reference_matches_installed_kernel_binary'])

    def test_changed_reference_source_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            names = ['evidence/cpu-startup-contract/sources.json', 'evidence/stock-dtb/candidate-report.json']
            names += [x['path'] for x in json.loads((ROOT/names[0]).read_text())['records']]
            for name in names:
                path = root/name
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/name, path)
            self.assertFalse(audit(root)['physical_boot_verified'])
            path = root/'evidence/cpu-startup-contract/legacy-mtcmos.c'
            path.write_bytes(path.read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError, 'hash/size'):
                audit(root)
