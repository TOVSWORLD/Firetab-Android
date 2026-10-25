"""DT build integrity checks, independent of the external compiler."""
import hashlib
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_douglas_dtb import inspect_header, verify_inputs


class DTBuildTests(unittest.TestCase):
    def test_real_source_dependency_closure(self):
        index,experiment = verify_inputs()
        self.assertEqual(index['ack_commit'],experiment['ack_commit'])
        self.assertEqual(index['donor_commit'],experiment['donor_commit'])
        self.assertTrue(any(x['path'].endswith('/thermal.h') for x in index['records']))

    def test_header_rejects_bad_magic_and_truncation(self):
        for data in [b'', b'bad'*20, struct.pack('>10I',0xd00dfeed,41,40,40,0,17,16,0,0,0)]:
            with self.assertRaises(ValueError):
                inspect_header(data)

    def test_header_bounds_are_checked(self):
        data=struct.pack('>10I',0xd00dfeed,40,40,40,0,17,16,0,0,4)
        with self.assertRaisesRegex(ValueError,'block bounds'):
            inspect_header(data)


if __name__ == '__main__':
    unittest.main()
