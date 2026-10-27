import struct
import unittest
import test_prepare_stage1_host_image as host_fixture
from compare_owned_link_bases import compare_link_bases


def shifted(data,base):
    result=bytearray(data)
    struct.pack_into('<I',result,24,base+1)
    struct.pack_into('<II',result,60,base,base)
    return result


class LinkBaseTests(unittest.TestCase):
    def test_normalized_equal_bytes_do_not_prove_physical_relocation(self):
        data=host_fixture.HostImageTests().source()
        result=compare_link_bases(data,shifted(data,0x10000000),second_base=0x10000000)
        self.assertTrue(result['normalized_load_bytes_equal'])
        self.assertFalse(result['arbitrary_runtime_relocation_verified'])

    def test_changed_linked_payload_is_rejected(self):
        data=host_fixture.HostImageTests().source();other=shifted(data,0x10000000);other[96]^=1
        with self.assertRaises(ValueError):compare_link_bases(data,other,second_base=0x10000000)

    def test_wrong_base_and_changed_instruction_state_rejected(self):
        data=host_fixture.HostImageTests().source();other=shifted(data,0x10000000)
        with self.assertRaises(ValueError):compare_link_bases(data,other,second_base=0x10001000)
        struct.pack_into('<I',other,24,0x10000000)
        with self.assertRaises(ValueError):compare_link_bases(data,other,second_base=0x10000000)
