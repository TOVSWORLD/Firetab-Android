from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from inspect_preloader_emi import inspect,GFH,MARKER


def fixture():
    data=bytearray(56+300+4+16);data[:8]=GFH
    struct.pack_into('<I',data,0x20,len(data));struct.pack_into('<I',data,0x2C,16)
    window=bytearray(300);window[:len(MARKER)+2]=MARKER+b'16'
    window[100:107]=b'MTK_BIN';data[56:356]=window
    struct.pack_into('<I',data,356,300)
    return data


class PreloaderEMITests(unittest.TestCase):
    def test_version_is_data_format_only_and_no_runtime_qualification(self):
        result=inspect(fixture())
        self.assertEqual(result['emi_data_bytes'],188)
        self.assertEqual(result['emi_format_version_hex'],'0x10')
        self.assertFalse(result['agent_acceptance_verified'])
        self.assertFalse(result['dram_capacity_or_layout_verified'])
        self.assertFalse(result['physical_test_ready'])

    def test_bad_header_signature_footer_markers_version_and_truncation_rejected(self):
        cases=[]
        data=fixture();struct.pack_into('<I',data,0x20,1);cases.append(data)
        data=fixture();struct.pack_into('<I',data,0x2C,99999);cases.append(data)
        data=fixture();struct.pack_into('<I',data,356,99999);cases.append(data)
        data=fixture();data[56+len(MARKER):56+len(MARKER)+2]=b'13';cases.append(data)
        data=fixture();data[156:163]=b'INVALID';cases.append(data)
        cases.extend([fixture()[:32],b'not-gfh'+bytes(400)])
        for data in cases:
            with self.assertRaises(ValueError):inspect(data)
