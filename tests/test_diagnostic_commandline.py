from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_diagnostic_commandline import check, EXPECTED, REQUIRED


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
