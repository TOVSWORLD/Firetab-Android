from pathlib import Path
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('acm_pid1',ROOT/'scripts/build_usb_acm_initramfs.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class ACMPID1(unittest.TestCase):
    def test_actual_flow_and_adapters_only_ram_callbacks(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name,marker in [('flow','FIRETABS_ACM_PID1_FLOW_RAM_PASS'),('adapter','FIRETABS_ACM_PID1_ADAPTER_RAM_PASS')]:
                binary=Path(tmp)/name
                r=subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
                    '-I',str(module.SOURCE),str(ROOT/f'evidence/usb-acm-pid1/{name}-ram.c'),'-o',str(binary)],capture_output=True,text=True)
                self.assertEqual(r.returncode,0,r.stderr)
                r=subprocess.run([str(binary)],capture_output=True,text=True)
                self.assertEqual(r.returncode,0,r.stderr);self.assertIn(marker,r.stdout)

    def test_current_package_cannot_admit_gadget_and_rejects_gate_edits(self):
        self.assertFalse(module.admission_contract()['admitted'])
        with tempfile.TemporaryDirectory() as tmp:
            copy=Path(tmp)/'source';shutil.copytree(module.SOURCE,copy)
            header=copy/'admission.h';original=header.read_text()
            with patch.object(module,'SOURCE',copy):
                for gate in module.GATES:
                    header.write_text(original.replace(f'FT_{gate}_QUALIFIED 0',f'FT_{gate}_QUALIFIED 1'))
                    with self.assertRaises(ValueError):module.admission_contract()
                header.write_text(original.replace('FT_PHYSICAL_VID ""','FT_PHYSICAL_VID "0xffff"'))
                with self.assertRaises(ValueError):module.admission_contract()

    def test_archive_rejects_added_endpoints_duplicate_or_changed_pid1(self):
        elf=b'static ELF placeholder for archive unit control'
        entries=[(n,0o040755,b'',(0,0)) for n in module.NAMES[:5]]
        entries += [('dev/console',0o020600,b'',(5,1)),('init',0o100755,elf,(0,0))]
        raw=module.archive(entries);self.assertEqual(module.inspect_archive(raw,elf),module.NAMES)
        for extra in [('bin/sh',0o100755,b'bad',(0,0)),('dev/sda',0o060600,b'',(8,0)),('TRAILER!!!',0,b'hidden',(0,0)),entries[-1]]:
            with self.assertRaises(ValueError):module.inspect_archive(module.archive(entries+[extra]),elf)
        with self.assertRaises(ValueError):module.inspect_archive(raw,b'wrong init')
        with self.assertRaises(ValueError):module.inspect_archive(raw+b'nonzero tail',elf)

if __name__=='__main__':unittest.main()
