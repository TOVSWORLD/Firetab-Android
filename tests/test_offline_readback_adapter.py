from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_offline_readback_adapter import guard_region_selection, select_darwin_library


class OfflineReadbackAdapterTests(unittest.TestCase):
    def test_synthetic_failure_aborts_before_next_read_and_success_continues(self):
        source='''
class DALegacy:
 def readflash(self):
  self.sdmmc_switch_part(1)
  self.transfer()
'''
        namespace={};exec(guard_region_selection(source),namespace) # Synthetic fixture only.
        for ack in (False,None,1,b'ack',True):
            instance=namespace['DALegacy']();events=[]
            instance.sdmmc_switch_part=lambda part:ack
            instance.transfer=lambda:events.append('read')
            if ack is True:instance.readflash();self.assertEqual(events,['read'])
            else:
                with self.assertRaises(RuntimeError):instance.readflash()
                self.assertEqual(events,[])

    def test_synthetic_library_finder_changes_only_darwin_and_never_loads(self):
        source='''
import sys
def finder(usb):
 return usb.backend.libusb1.get_backend(find_library=lambda name: 'libusb-1.0.so')
'''
        namespace={};exec(select_darwin_library(source,'/synthetic/libusb.dylib'),namespace)
        fake=SimpleNamespace(backend=SimpleNamespace(libusb1=SimpleNamespace(
            get_backend=lambda find_library:find_library('ignored'))))
        for platform,expected in [('darwin','/synthetic/libusb.dylib'),('linux','libusb-1.0.so')]:
            namespace['sys']=SimpleNamespace(platform=platform)
            self.assertEqual(namespace['finder'](fake),expected)

    def test_changed_or_ambiguous_source_fails_closed(self):
        with self.assertRaises(ValueError):guard_region_selection('class DALegacy: pass')
        with self.assertRaises(ValueError):select_darwin_library('import sys','/unused')
