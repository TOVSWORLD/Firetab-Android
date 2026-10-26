from pathlib import Path
import hashlib
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from offline_escrow_capture import capture_region


class EscrowCaptureContractTests(unittest.TestCase):
    def test_complete_synthetic_capture_hashes_exact_requested_extents(self):
        data=b'abcdefghij';calls=[]
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'capture'
            def read(region,offset,count):
                calls.append((region,offset,count));return data[offset:offset+count]
            result=capture_region(target,'boot1',len(data),lambda r:True,read,4)
            self.assertEqual(calls,[('boot1',0,4),('boot1',4,4),('boot1',8,2)])
            self.assertEqual(target.read_bytes(),data)
            self.assertEqual(result['sha256'],hashlib.sha256(data).hexdigest())
            self.assertFalse(result['collection_region_identity_verified'])
            self.assertFalse(result['physical_test_ready'])

    def test_short_empty_oversized_failed_or_unacknowledged_input_never_publishes(self):
        for failure in ('short','empty','oversized','exception','ack'):
            with tempfile.TemporaryDirectory() as tmp:
                target=Path(tmp)/'capture';calls=[]
                def read(region,offset,count):
                    calls.append(offset)
                    if failure=='exception':raise OSError('synthetic transport failed')
                    return {'short':b'x','empty':b'','oversized':b'x'*5}.get(failure,b'xxxx')
                with self.assertRaises((ValueError,OSError)):
                    capture_region(target,'user',8,lambda r:False if failure=='ack' else True,read,4)
                self.assertFalse(target.exists());self.assertEqual(list(Path(tmp).iterdir()),[])
                if failure=='ack':self.assertEqual(calls,[])
                else:self.assertEqual(calls,[0])

    def test_existing_output_unknown_region_and_disk_shortage_do_not_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'capture';target.write_bytes(b'original')
            def forbidden(*args):raise AssertionError('Callback must not run')
            with self.assertRaises(ValueError):capture_region(target,'user',8,forbidden,forbidden)
            self.assertEqual(target.read_bytes(),b'original');target.unlink()
            with self.assertRaises(ValueError):capture_region(target,'rpmb',8,forbidden,forbidden)
            with patch('shutil.disk_usage',return_value=type('Disk',(),{'free':0})()):
                with self.assertRaises(ValueError):capture_region(target,'user',8,forbidden,forbidden)

    def test_publish_race_preserves_other_output_and_cleans_temporary_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'capture'
            def read(region,offset,count):target.write_bytes(b'other');return b'x'*count
            with self.assertRaises(FileExistsError):capture_region(target,'boot2',4,lambda r:True,read)
            self.assertEqual(target.read_bytes(),b'other')
            self.assertEqual(list(Path(tmp).iterdir()),[target])
