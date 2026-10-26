import json
from pathlib import Path
import struct
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from compare_recovery_preloaders import compare


class RecoveryPreloaderComparison(unittest.TestCase):
    def fixture(self):
        result=[]
        for length in (138924,139352):
            b=bytearray(length)
            struct.pack_into('<IHH',b,0,0x014d4d4d,56,0)
            b[8:20]=b'FILE_INFO'+bytes(3)
            struct.pack_into('<5I',b,28,0x200d00,length,262144,768,292)
            result.append(b)
        for address in (0x201934,0x217420,0x21b970,0x20a204):
            off=address-0x200d00
            result[0][off:off+16]=bytes([1])*16
            result[1][off:off+16]=bytes([2])*16
        return result

    def test_selected_differences_never_qualify_downgrade_or_patch_set(self):
        result=compare(*self.fixture())
        self.assertTrue(all(not x['same_bytes'] for x in result['sites']))
        self.assertFalse(result['marker_proves_exploitability'])
        self.assertFalse(result['older_original_build_verified'])
        self.assertFalse(result['recoverable_loading_path_qualified'])

    def test_wrong_declared_mapping_refused(self):
        a,b=self.fixture()
        struct.pack_into('<I',a,28,0x201000)
        with self.assertRaises(ValueError):compare(a,b)
