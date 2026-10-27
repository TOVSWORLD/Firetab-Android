import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from synthetic_escrow_fixture import image
from compare_offline_escrow import compare_sets


def capture(root):
    root.mkdir();regions={}
    for name,data in [('user',bytes(image())),('boot1',b'A'*512),('boot2',b'B'*512)]:
        (root/(name+'.bin')).write_bytes(data)
        regions[name]=dict(file=name+'.bin',expected_bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    path=root/'manifest.json';path.write_text(json.dumps(dict(logical_sector_bytes=512,regions=regions)))
    return path


class CaptureConsistencyTests(unittest.TestCase):
    def test_agreement_is_not_acquisition_or_restore_proof(self):
        with tempfile.TemporaryDirectory() as folder:
            a=capture(Path(folder)/'a');b=capture(Path(folder)/'b');r=compare_sets(a,b)
            self.assertTrue(r['offline_capture_sets_agree'])
            self.assertFalse(r['independently_acquired_verified']);self.assertFalse(r['restore_qualified'])

    def test_rejects_hardlink_alias_across_sets(self):
        with tempfile.TemporaryDirectory() as folder:
            a=capture(Path(folder)/'a');b=capture(Path(folder)/'b')
            target=b.parent/'boot1.bin';target.unlink();os.link(a.parent/'boot1.bin',target)
            with self.assertRaises(ValueError):compare_sets(a,b)

    def test_different_bytes_with_valid_individual_hashes_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            a=capture(Path(folder)/'a');b=capture(Path(folder)/'b');data=b'X'*512
            (b.parent/'boot2.bin').write_bytes(data);m=json.loads(b.read_text())
            m['regions']['boot2']['sha256']=hashlib.sha256(data).hexdigest();b.write_text(json.dumps(m))
            with self.assertRaises(ValueError):compare_sets(a,b)

    def test_corrupt_gpt_and_symlink_rejected(self):
        for fault in ('gpt','symlink'):
            with tempfile.TemporaryDirectory() as folder:
                a=capture(Path(folder)/'a');b=capture(Path(folder)/'b')
                if fault=='symlink':
                    target=b.parent/'boot2.bin';target.unlink();target.symlink_to(a.parent/'boot2.bin')
                else:
                    data=bytearray((b.parent/'user.bin').read_bytes());data[512]=0
                    (b.parent/'user.bin').write_bytes(data);m=json.loads(b.read_text())
                    m['regions']['user']['sha256']=hashlib.sha256(data).hexdigest();b.write_text(json.dumps(m))
                with self.assertRaises(ValueError):compare_sets(a,b)
