from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from offline_legacy_read_binding import OfflineLegacyReadBinding,REGION_IDS
from offline_escrow_capture import capture_region


class OfflineLegacyBindingTests(unittest.TestCase):
    def make(self, translator=None, selector=None, reader=None, observed=None, **extra):
        sizes={'user':2048,'boot1':1024,'boot2':1024};self.events=[]
        def default_reader(**kwargs):self.events.append(kwargs);return b'x'*kwargs['length']
        options=dict(backend_kind='legacy',storage_kind='emmc',iot=False,sector_bytes=512)
        options.update(extra)
        return OfflineLegacyReadBinding(sizes,observed or (lambda:dict(sizes)),
            translator or (lambda parttype,length:(length,REGION_IDS[parttype])),
            selector or (lambda region:True),reader or default_reader,**options)

    def test_host_capture_uses_exact_byte_offsets_memory_mode_and_region(self):
        binding=self.make()
        with tempfile.TemporaryDirectory() as tmp:
            result=capture_region(Path(tmp)/'host','boot1',1024,binding.select_region,binding.read_chunk,512)
            self.assertEqual([(r['addr'],r['length']) for r in self.events],[(0,512),(512,512)])
            self.assertTrue(all(r['filename']=='' and r['parttype']=='boot1' and r['display'] is False for r in self.events))
            self.assertFalse(result['callback_binding_qualified'])

    def test_clipping_wrong_mapping_geometry_or_backend_rejected_before_read(self):
        for translate in [lambda parttype,length:(length-512,REGION_IDS[parttype]),
                          lambda parttype,length:(length,999)]:
            binding=self.make(translator=translate)
            with self.assertRaises(ValueError):binding.select_region('boot1')
            self.assertEqual(self.events,[])
        with self.assertRaises(ValueError):self.make(observed=lambda:{'user':4096,'boot1':1024,'boot2':1024})
        for kwargs in [{'backend_kind':'xflash'},{'storage_kind':'nand'},{'iot':True}]:
            with self.assertRaises(ValueError):self.make(**kwargs)

    def test_unselected_out_of_bounds_mutated_geometry_and_failed_reselection(self):
        sizes={'user':2048,'boot1':1024,'boot2':1024};binding=self.make(observed=lambda:dict(sizes))
        with self.assertRaises(ValueError):binding.read_chunk('boot1',0,512)
        for offset,count in [(1024,512),(1,512),(0,513),(0,2*1024*1024)]:
            binding.select_region('boot1')
            with self.assertRaises(ValueError):binding.read_chunk('boot1',offset,count)
        binding.select_region('boot1')
        sizes['boot1']=2048
        with self.assertRaises(ValueError):binding.read_chunk('boot1',0,512)
        def guarded_reader(**kwargs):raise RuntimeError('synthetic internal second selection failed')
        binding=self.make(reader=guarded_reader)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RuntimeError):capture_region(Path(tmp)/'host','boot1',1024,binding.select_region,binding.read_chunk,512)
            self.assertEqual(list(Path(tmp).iterdir()),[])
            self.assertIsNone(binding.active)

    def test_short_read_and_selection_failure_do_not_create_completed_capture(self):
        for binding in [self.make(reader=lambda **kwargs:b'x'),self.make(selector=lambda region:False)]:
            with tempfile.TemporaryDirectory() as tmp:
                with self.assertRaises(ValueError):capture_region(Path(tmp)/'host','boot2',1024,binding.select_region,binding.read_chunk,512)
                self.assertEqual(list(Path(tmp).iterdir()),[])
