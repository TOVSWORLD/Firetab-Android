"""Source locks reject drift and path/origin substitution without fetching anything."""
import copy
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from kernel_audit import verify_records


class KernelAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'source.c').write_bytes(b'actual source\n')
        self.record = dict(status=200, path='source.c', url='https://raw.githubusercontent.com/owner/repo/'+'a'*40+'/source.c', bytes=14, sha256=hashlib.sha256(b'actual source\n').hexdigest())

    def test_source_drift_rejected(self):
        self.assertEqual(verify_records({'records':[self.record]}, self.root), 1)
        (self.root/'source.c').write_bytes(b'changed bytes\n')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            verify_records({'records':[self.record]}, self.root)

    def test_duplicate_and_escape_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            verify_records({'records':[self.record,self.record]}, self.root)
        record = copy.deepcopy(self.record)
        record['path'] = '../escape.c'
        with self.assertRaisesRegex(ValueError, 'Unsafe path'):
            verify_records({'records':[record]}, self.root)

    def test_origin_substitution_rejected(self):
        record = copy.deepcopy(self.record)
        record['url'] = 'https://example.com/source.c'
        with self.assertRaisesRegex(ValueError, 'Unexpected source origin'):
            verify_records({'records':[record]}, self.root)


if __name__ == '__main__':
    unittest.main()
