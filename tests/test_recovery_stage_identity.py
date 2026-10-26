import hashlib
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from verify_recovery_stage_identity import stage_digest, patch_scope


class StageIdentityTests(unittest.TestCase):
    def test_signature_digest_is_not_signature_verification(self):
        raw=b'code'+b'sign'
        result=stage_digest(raw,8,hashlib.sha256(raw).hexdigest(),4)
        self.assertEqual(result['declared_signature_sha256'],hashlib.sha256(b'sign').hexdigest())
        for args in [(raw,7,hashlib.sha256(raw).hexdigest(),4),(raw,8,'0'*64,4),
                     (raw,8,hashlib.sha256(raw).hexdigest(),8)]:
            with self.assertRaises(ValueError):stage_digest(*args)

    def test_extension_is_parsed_without_execution(self):
        source='''
raise RuntimeError('must never execute')
class Example:
 def patch_da2(self): return self.patch_da2_readmem()
 def patch_da2_readmem(self): raise RuntimeError('must never execute')
'''
        result=patch_scope(source)
        self.assertFalse(result['patch_function_executed_by_this_audit'])
        self.assertFalse(result['uploaded_stage_identity_verified'])
        with self.assertRaises(ValueError):
            patch_scope(source.replace('return self.patch_da2_readmem()', 'return None'))
