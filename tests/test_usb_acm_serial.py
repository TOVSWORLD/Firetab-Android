from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import validate_usb_acm_serial as contract

class ACMSerial(unittest.TestCase):
    def test_actual_output_adapters_and_pid1_mapping_ram_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary=Path(tmp)/'serial'
            result=subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
                '-I',str(ROOT/'projects/firetabs-android/diagnostic-usb'),
                str(ROOT/'evidence/usb-acm-serial/serial-ram.c'),'-o',str(binary)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            result=subprocess.run([str(binary)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr);self.assertIn('FIRETABS_ACM_SERIAL_RAM_PASS',result.stdout)

    def test_full_pinned_uapi_struct_layout_not_host_libc(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'asm-generic').mkdir()
            shutil.copyfile(contract.EVIDENCE/'termbits-common.h',root/'asm-generic/termbits-common.h')
            shutil.copyfile(contract.EVIDENCE/'termbits.h',root/'actual-termbits.h')
            stat=(contract.EVIDENCE/'stat.h').read_text()
            declarations='\n'.join(re.search(r'struct '+name+r'\s*\{.*?^\};',stat,re.S|re.M)[0] for name in ['statx_timestamp','statx'])
            probe=root/'probe.c'
            probe.write_text('''#include <stddef.h>
#include <assert.h>
#include "actual-termbits.h"
typedef unsigned long long __u64;typedef long long __s64;
typedef unsigned int __u32;typedef int __s32;typedef unsigned short __u16;
'''+declarations+'''
#define FT_ACM_HOST_TEST 1
#include "acm_serial.h"
_Static_assert(sizeof(struct statx)==256,"statx buffer extent");
_Static_assert(offsetof(struct statx,stx_mode)==28,"statx mode offset");
_Static_assert(offsetof(struct statx,stx_rdev_major)==128,"statx rdev major offset");
_Static_assert(offsetof(struct statx,stx_rdev_minor)==132,"statx rdev minor offset");
_Static_assert(sizeof(struct ft_termios)==sizeof(struct termios),"termios extent");
_Static_assert(offsetof(struct ft_termios,line)==offsetof(struct termios,c_line),"line offset");
_Static_assert(offsetof(struct ft_termios,cc)==offsetof(struct termios,c_cc),"cc offset");
_Static_assert(offsetof(struct ft_termios,cflag)==offsetof(struct termios,c_cflag),"control flags offset");
int main(void){char b[64];assert(ft_acm_filesystem_ops.write!=0);assert(ft_serial_output(0,0,0,0)==-22);assert(ft_discover_udc(0,b,64)==-22);assert(ft_acm_setup(0,0,0,0,0,0,0)==-22);return 0;}
''')
            result=subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-I',str(root),
                '-I',str(ROOT/'projects/firetabs-android/diagnostic-usb'),str(probe),'-o',str(root/'probe')],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            subprocess.run([str(root/'probe')],check=True)

    def test_source_hash_and_wrong_ioctl_rejected(self):
        self.assertFalse(contract.validate()['runtime_qualified'])
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'acm_serial.h';source.write_text(contract.SOURCE.read_text().replace('FT_SERIAL_TCGETS 0x5401','FT_SERIAL_TCGETS 0x5402'))
            with patch.object(contract,'SOURCE',source):
                with self.assertRaises(ValueError):contract.validate()
            shutil.copytree(contract.EVIDENCE,root/'evidence')
            (root/'evidence/f_acm.c').write_text('wrong source')
            with patch.object(contract,'EVIDENCE',root/'evidence'):
                with self.assertRaises(ValueError):contract.validate()

if __name__=='__main__':unittest.main()
