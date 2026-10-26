import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_offline_escrow import verify_region, regular_file


from synthetic_escrow_fixture import image


class OfflineEscrowTests(unittest.TestCase):
    def check(self, data, sector=512):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'fixture.bin'; path.write_bytes(data)
            return verify_region(path, len(data), hashlib.sha256(data).hexdigest(), sector)

    def test_both_independent_locations_512_and_4096(self):
        for sector in [512, 4096]:
            result = self.check(image(sector), sector)
            self.assertTrue(result['gpt']['separate_secondary_location_checked'])
            self.assertEqual(result['gpt']['used_partition_count'], 1)

    def test_corrupted_primary_secondary_and_array(self):
        for offset in [512+24, 127*512+24, 2*512, 95*512]:
            data = image(); data[offset] ^= 1
            with self.assertRaises(ValueError): self.check(data)

    def test_copied_primary_is_not_a_secondary_header(self):
        data = image(); data[-512:] = data[512:1024]
        with self.assertRaises(ValueError): self.check(data)

    def test_recomputed_crc_does_not_hide_geometry_or_disagreement(self):
        mutations = [lambda l,b,t: struct.pack_into('<Q', b, 32, 7),
                     lambda l,b,t: struct.pack_into('<I', b, 80, 0xffffffff),
                     lambda l,b,t: struct.pack_into('<Q', b, 72, 40),
                     lambda l,b,t: b.__setitem__(slice(56,72), b'X'*16) if l==127 else None]
        for mutation in mutations:
            with self.assertRaises(ValueError): self.check(image(mutate=mutation))

    def test_overlap_with_valid_crc(self):
        def overlap(lba, block, table):
            table[128:144] = b'T'*16; table[144:160] = b'V'*16
            struct.pack_into('<QQ', table, 160, 45, 55)
            struct.pack_into('<I', block, 88, zlib.crc32(table))
        with self.assertRaises(ValueError): self.check(image(mutate=overlap))

    def test_short_or_wrong_hash_and_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'data'; path.write_bytes(b'abc')
            for length, digest in [(4, hashlib.sha256(b'abc').hexdigest()), (3, '0'*64)]:
                with self.assertRaises(ValueError): verify_region(path,length,digest)
            alias = Path(tmp)/'alias'; alias.symlink_to(path)
            with self.assertRaises(ValueError):
                with regular_file(alias): pass
            with self.assertRaises(ValueError):
                with regular_file(Path(tmp)): pass

    def test_cli_sanitizes_failure_and_does_not_claim_restore(self):
        script = Path(__file__).resolve().parents[1]/'scripts/verify_offline_escrow.py'
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            records={}
            for name, data in [('user',image()),('boot1',b'A'*512),('boot2',b'B'*512)]:
                (base/name).write_bytes(data)
                records[name]={'file':name,'expected_bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
            manifest=base/'private.json'
            manifest.write_text(json.dumps({'logical_sector_bytes':512,'regions':records}))
            result=subprocess.run([sys.executable,str(script),str(manifest)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout)
            self.assertFalse(json.loads(result.stdout)['restore_qualified'])
            records['boot1']['file']='household-private-nonexistent'
            manifest.write_text(json.dumps({'logical_sector_bytes':512,'regions':records}))
            result=subprocess.run([sys.executable,str(script),str(manifest)],capture_output=True,text=True)
            self.assertEqual(result.returncode,1)
            self.assertNotIn('household',result.stdout+result.stderr)
            self.assertFalse(json.loads(result.stdout)['offline_file_integrity_pass'])
