import ctypes
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from run_qemu_diagnostic import cpu_contract_report


class CPUContractParsers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory()
        path = Path(cls.folder.name)
        header = ROOT/'projects/firetabs-android/diagnostic/cpu_contract.h'
        (path/'test.c').write_text('#include "'+str(header)+'"\nint limit(const char *s, unsigned long n) {return parse_limit(s,n,"nr_cpus","nr_cpus=1");}\nint online(const char *s,unsigned long n,int *v) {return parse_online(s,n,v);}\n')
        subprocess.run([shutil.which('cc') or 'clang', '-shared', '-fPIC', '-Wall', '-Wextra', '-Werror', str(path/'test.c'), '-o', str(path/'test.so')], check=True)
        cls.lib = ctypes.CDLL(str(path/'test.so'))
        cls.lib.limit.argtypes = [ctypes.c_char_p, ctypes.c_ulong]
        cls.lib.online.argtypes = [ctypes.c_char_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_int)]

    @classmethod
    def tearDownClass(cls):
        cls.lib = None
        cls.folder.cleanup()

    def test_real_c_argument_parser_bounds_and_redacted_verdicts(self):
        for raw, expected in [(b'serial=PRIVATE nr_cpus=1 maxcpus=0\n',1), (b'root=PRIVATE',0),
                              (b'nr_cpus=4',2), (b'nr_cpus=1 nr_cpus=4',3),
                              (b'nr_cpus=1 nr_cpus=1',3), (b'"nr_cpus=1"',4),
                              (b'nr_cpus=1\x00secret',4), (b'x'*4097,4), (b'',4)]:
            self.assertEqual(self.lib.limit(raw,len(raw)), expected)

    def test_real_c_cpu_ranges_and_invalid_input(self):
        for raw, expected, only in [(b'0\n',1,1), (b'0-3,5',5,0), (b'3',1,0),
                                    (b'0,0',-1,0), (b'3-1',-1,0), (b'0,',-1,0),
                                    (b'4096',-1,0), (b'99999999999',-1,0), (b'',-1,0)]:
            value = ctypes.c_int(0)
            self.assertEqual(self.lib.online(raw,len(raw),ctypes.byref(value)), expected)
            self.assertEqual(value.value,only)

    def block(self):
        return b'FIRETABS_CPU_CONTRACT_V1\nLIMIT_NR_CPUS=valid\nLIMIT_MAXCPUS=valid\nONLINE_CPUS=1\nONLINE_BOOT_CPU_ONLY=yes\nPSCI_DT_STATUS=disabled\nFIRETABS_CPU_CONTRACT_END\n'

    def test_generic_observer_distinct_from_primary_requirement(self):
        good = self.block()
        self.assertTrue(cpu_contract_report(good,True)['primary_only_contract_observed'])
        generic = good.replace(b'LIMIT_MAXCPUS=valid',b'LIMIT_MAXCPUS=missing')
        self.assertFalse(cpu_contract_report(generic)['primary_only_contract_observed'])
        with self.assertRaises(ValueError):
            cpu_contract_report(generic,True)

    def test_untrusted_or_duplicate_fields_never_enter_report(self):
        for raw in [self.block()+self.block(), self.block().replace(b'ONLINE_CPUS=1',b'ONLINE_CPUS=private-serial'),
                    self.block().replace(b'PSCI_DT_STATUS=disabled',b'SERIAL=private')]:
            with self.assertRaises(ValueError):
                cpu_contract_report(raw)
