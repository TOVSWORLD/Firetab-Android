from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_diagnostic_commandline import check, EXPECTED, REQUIRED, GENERIC_EXPECTED


class DiagnosticCommandLineTests(unittest.TestCase):
    def config(self):
        return 'CONFIG_CMDLINE="'+EXPECTED+'"\n'+'\n'.join('CONFIG_'+key+'=y' for key in REQUIRED)

    def test_force_contract_does_not_promote_runtime_readiness(self):
        result=check(self.config())
        self.assertTrue(result['resolved_config_contract_pass'])
        self.assertFalse(result['compiled_or_runtime_verified'])
        self.assertFalse(result['physical_test_ready'])

    def test_loader_extend_missing_support_duplicates_and_conflicting_limits_fail(self):
        for text in [self.config().replace('CMDLINE_FORCE=y','CMDLINE_FORCE=n'),
                     self.config()+'\nCONFIG_CMDLINE_EXTEND=y',
                     self.config().replace('nr_cpus=1','nr_cpus=1 nr_cpus=4'),
                     self.config().replace('SERIAL_8250_MT6577=y','SERIAL_8250_MT6577=m'),
                     self.config()+'\nCONFIG_CMDLINE_FORCE=y']:
            with self.assertRaises(ValueError):check(text)

    def test_generic_profile_requires_pl011_and_rejects_device_mmio_policy(self):
        config=self.config().replace(EXPECTED,GENERIC_EXPECTED)
        with self.assertRaises(ValueError):check(config,'generic-force')
        config+='\nCONFIG_SERIAL_AMBA_PL011_CONSOLE=y'
        self.assertEqual(check(config,'generic-force')['profile'],'generic-force')
        with self.assertRaises(ValueError):check(config,'device')
        with self.assertRaises(ValueError):check(self.config(),'generic-force')
