from pathlib import Path
import struct
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from preflight_mac_usb_library import inspect,inspect_file,ARM64


def dylib(cpu=ARM64,kind=6):
    command=struct.pack('<6I',0xD,32,24,0,0,0)+b'libusb\0\0'
    return struct.pack('<8I',0xFEEDFACF,cpu,0,kind,1,len(command),0,0)+command


def fat(wide=False):
    payload=dylib();data=bytearray(4096+len(payload))
    struct.pack_into('>II',data,0,0xCAFEBABF if wide else 0xCAFEBABE,1)
    if wide:struct.pack_into('>IIQQII',data,8,ARM64,0,4096,len(payload),12,0)
    else:struct.pack_into('>IIIII',data,8,ARM64,0,4096,len(payload),12)
    data[4096:]=payload
    return data


class MacUSBStaticPreflightTests(unittest.TestCase):
    def test_thin_and_fat32_fat64_are_static_structure_only(self):
        for data in (dylib(),fat(),fat(True)):
            self.assertTrue(inspect(data)['header_structure_valid'])
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'native';path.write_bytes(dylib())
            alias=Path(tmp)/'alias';alias.symlink_to(path)
            result=inspect_file(alias)
            self.assertFalse(result['native_code_loaded'])
            self.assertFalse(result['libusb_exports_verified'])
            self.assertFalse(result['usb_enumerated'])

    def test_elf_x86_executable_and_truncated_input_are_rejected(self):
        for data in (b'\x7fELF'+bytes(60),dylib(0x01000007),dylib(kind=2),dylib()[:31]):
            with self.assertRaises(ValueError):inspect(data)

    def test_bad_fat_bounds_or_identity_and_load_commands_rejected(self):
        cases=[]
        data=fat();struct.pack_into('>I',data,8+8,4);cases.append(data)
        data=fat();struct.pack_into('>I',data,8,0x01000007);cases.append(data)
        data=bytearray(dylib());struct.pack_into('<I',data,36,4096);cases.append(data)
        data=bytearray(dylib());struct.pack_into('<I',data,40,31);data[-1]=65;cases.append(data)
        for data in cases:
            with self.assertRaises(ValueError):inspect(data)
