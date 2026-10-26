from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from probe_reference_recovery import plan,SELECTED


class ReferenceRecoveryProbe(unittest.TestCase):
    def fixture(self):
        return {name:{'name':name,'compressed_bytes':100,'uncompressed_bytes':200} for name in SELECTED}

    def test_exact_allowlist_never_selects_large_brick_images(self):
        entries = self.fixture()
        entries['amonet/bin/brick.img'] = {'compressed_bytes':1,'uncompressed_bytes':114780260}
        selected = plan(entries)
        self.assertEqual(len(selected),8)
        self.assertNotIn('brick.img',[local for _,local in selected])

    def test_missing_oversized_or_unbounded_entry_rejected(self):
        for key,value in [('uncompressed_bytes',1024*1024+1),('compressed_bytes',1024*1024+1),('uncompressed_bytes',0)]:
            entries = self.fixture()
            entries['amonet/bin/preloader.bin'][key] = value
            with self.assertRaises(ValueError):
                plan(entries)
        entries = self.fixture()
        del entries['amonet/bin/preloader.bin']
        with self.assertRaises(KeyError):
            plan(entries)
