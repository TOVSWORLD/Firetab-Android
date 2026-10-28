import bz2
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import zlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from reconstruct_stock_recovery import bsdiff,imgdiff,pinned_recovery,publish,CAP


def offset(n):
    return (abs(n)|(1<<63 if n<0 else 0)).to_bytes(8,'little')


def delta(old,new,control=None,diff=None,extra=b''):
    control=control if control is not None else [(len(new),0,0)]
    diff=diff if diff is not None else bytes((x-(old[i] if i<len(old) else 0))&255 for i,x in enumerate(new))
    c=bz2.compress(b''.join(offset(x) for triple in control for x in triple))
    d=bz2.compress(diff);e=bz2.compress(extra)
    return b'BSDIFF40'+offset(len(c))+offset(len(d))+offset(len(new))+c+d+e


def deflate(data):
    c=zlib.compressobj(6,8,-15,8,0)
    return c.compress(data)+c.flush()


class RecoveryReconstruction(unittest.TestCase):
    def test_bsdiff_diff_extra_and_negative_seek(self):
        p=delta(b'abc',b'abeXYZ',[(3,3,0)],b'\0\0\2',b'XYZ')
        self.assertEqual(bsdiff(b'abc',p),b'abeXYZ')
        p=delta(b'ab',b'aba',[(2,0,-2),(1,0,0)],b'\0'*3)
        self.assertEqual(bsdiff(b'ab',p),b'aba')
        with self.assertRaises(ValueError):bsdiff(b'abc',p[:-1])
        with self.assertRaises(ValueError):bsdiff(b'abc',delta(b'abc',b'x',[(9,0,0)],b'x'))

    def test_raw_and_normal_image_chunks_and_offset_rejection(self):
        raw=b'head';p=delta(b'abc',b'xbc');start=12+8+len(raw)+28
        header=b'IMGDIFF2'+struct.pack('<I',2)+struct.pack('<II',3,len(raw))+raw+struct.pack('<I3Q',0,0,3,start)
        self.assertEqual(imgdiff(b'abc',header+p),b'headxbc')
        bad=bytearray(header+p);struct.pack_into('<Q',bad,len(header)-8,0)
        with self.assertRaises(ValueError):imgdiff(b'abc',bytes(bad))
        with self.assertRaises(ValueError):imgdiff(b'abc',b'IMGDIFF2'+struct.pack('<I',33))

    def test_deflate_bonus_and_profile_caps(self):
        old=b'old source'*10;bonus=b'bonus';target=b'new recovery data'*25
        compressed=deflate(old);raw=b'prefix';start=12+8+len(raw)+64
        header=b'IMGDIFF2'+struct.pack('<I',2)+struct.pack('<II',3,len(raw))+raw+struct.pack('<I5Q5i',2,0,len(compressed),start,len(old)+len(bonus),len(target),6,8,-15,8,0)
        p=header+delta(old+bonus,target)
        self.assertEqual(imgdiff(compressed,p,bonus),raw+deflate(target))
        with self.assertRaises(ValueError):imgdiff(compressed,p,b'')
        bad=bytearray(p);struct.pack_into('<Q',bad,12+8+len(raw)+4+24,CAP+1)
        with self.assertRaises(ValueError):imgdiff(compressed,bytes(bad),bonus)
        with self.assertRaises(ValueError):pinned_recovery(b'fake',p,bonus)

    def test_publish_never_overwrites_and_cleans_failed_temporary(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'recovery.img';publish(path,b'first')
            with self.assertRaises(FileExistsError):publish(path,b'second')
            self.assertEqual(path.read_bytes(),b'first')
            with patch('reconstruct_stock_recovery.os.link',side_effect=OSError('host failure')):
                with self.assertRaises(OSError):publish(Path(d)/'other.img',b'incomplete')
            self.assertEqual([p.name for p in Path(d).iterdir()],['recovery.img'])
