import unittest
from decode_offline_emmc_geometry import decode_geometry


def supplied(sector=0):
    data=bytearray(512);data[192]=8;data[61]=sector;data[226]=32
    data[212:216]=(2*1024*1024).to_bytes(4,'little')
    return data


class GeometryTests(unittest.TestCase):
    def test_capacities_and_region_naming(self):
        result=decode_geometry(bytes(supplied()))
        self.assertEqual(result['region_bytes'],dict(user=1024**3,boot1=4*1024**2,boot2=4*1024**2))
        self.assertEqual(result['linux_boot_suffix_mapping']['boot2'],'boot1')
        self.assertFalse(result['region_selection_verified'])

    def test_4096_data_sectors_do_not_change_sec_count_units(self):
        a=decode_geometry(bytes(supplied(0)));b=decode_geometry(bytes(supplied(1)))
        self.assertEqual(a['region_bytes'],b['region_bytes']);self.assertEqual(b['logical_sector_bytes'],4096)

    def test_rpmb_access_is_not_ordinary_region(self):
        data=supplied();data[179]=3
        result=decode_geometry(bytes(data));self.assertFalse(result['supplied_access_is_ordinary_region'])
        self.assertFalse(result['region_selection_verified'])

    def test_malformed_or_unreviewed_fields_reject(self):
        cases=[bytes(511),bytearray(512)]
        for offset,value in [(192,9),(61,2),(226,0)]:
            data=supplied();data[offset]=value;cases.append(bytes(data))
        data=supplied();data[212:216]=bytes(4);cases.append(bytes(data))
        for data in cases:
            with self.assertRaises(ValueError):decode_geometry(data)
