import copy
import struct
import sys
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from compare_usb_resource_dtb import compare,encode,reservations,PHY,USB0,USB1,CHILDREN


class USBResourceDTB(unittest.TestCase):
    def fixture(self):
        base={PHY:{'reg':encode(struct.pack('>4I',0,0x11210000,0,0x800)),'status':encode(b'disabled\0')},
              USB0:{'status':encode(b'disabled\0'),'phys':'0 0 0 1','clocks':'unchanged'},USB1:{'status':encode(b'disabled\0')},'/memory@40000000':{'reg':'unchanged'}}
        new=copy.deepcopy(base);new[PHY]['reg']=encode(struct.pack('>8I',0,0x11210000,0,0x800,0,0x11210f00,0,0x100));new[PHY]['reg-names']=encode(b'sif\0u2-frequency\0');return base,new

    def test_exact_isolated_delta_retains_disabled_unsupported_instance(self):
        b,n=self.fixture();r=compare(b,n,CHILDREN,CHILDREN,[],[])
        self.assertTrue(r['usb0_usb1_and_phy_remain_disabled']);self.assertFalse(r['usb1_port1_driver_supported']);self.assertFalse(r['runtime_qualified'])

    def test_unrelated_memory_names_resources_enable_and_order_drift_rejected(self):
        for kind in ['memory','names','reg','usb0','usb1','order','reservation','version','clock','phys','phandle','node']:
            b,n=self.fixture();order=CHILDREN;reserve=[]
            if kind=='memory':n['/memory@40000000']['reg']='changed'
            elif kind=='names':n[PHY]['reg-names']=encode(b'u2-frequency\0sif\0')
            elif kind=='reg':n[PHY]['reg']=encode(struct.pack('>4I',0,0x11210000,0,0x1000))
            elif kind in ['usb0','usb1']:n[USB0 if kind=='usb0' else USB1]['status']=encode(b'okay\0')
            elif kind=='order':order=list(reversed(CHILDREN))
            elif kind=='reservation':reserve=[(0x40000000,4096)]
            elif kind=='clock':n[USB0]['clocks']='changed'
            elif kind=='phys':n[USB0]['phys']='changed'
            elif kind=='phandle':n[PHY]['phandle']='changed'
            elif kind=='node':n.pop(USB1)
            else:n['/']={'version':'guessed'}
            with self.assertRaises(ValueError,msg=kind):compare(b,n,CHILDREN,order,[],reserve)

    def test_reservation_reader_preserves_entries_and_rejects_truncation(self):
        data=struct.pack('>10I',0xd00dfeed,72,0,0,40,17,16,0,0,0)+struct.pack('>4Q',0x40000000,4096,0,0)
        self.assertEqual(reservations(data),[(0x40000000,4096)])
        with self.assertRaises(ValueError):reservations(data[:-16])
