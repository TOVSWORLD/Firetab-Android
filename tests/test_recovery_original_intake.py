import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from inspect_recovery_originals import inspect, CAP, ENTRY_CAP


class RecoveryOriginalIntake(unittest.TestCase):
    def packages(self, directory, members):
        paths = []
        for number in range(3):
            path = Path(directory) / f'{number}.zip'
            with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                for name, data in members:
                    archive.writestr(name, data)
            paths.append(path)
        return paths

    def test_content_identity_does_not_promote_origin_or_restore(self):
        with tempfile.TemporaryDirectory() as directory:
            # These are text bytes, never imported or executed.
            content = b'raise RuntimeError("must not execute")\n'
            paths = self.packages(directory, [('release/amonet/modules/main.py', content)])
            result = inspect(paths, {'amonet/modules/main.py': hashlib.sha256(content).hexdigest()})
            self.assertEqual(result['packages'][0]['selected_files'][0]['mirror_comparison'], 'equal')
            self.assertFalse(result['source_provenance_verified'])
            self.assertFalse(result['restore_qualified'])
            self.assertFalse(result['archive_contents_executed'])
            self.assertEqual(sorted(x.name for x in Path(directory).iterdir()), ['0.zip','1.zip','2.zip'])
            different = inspect(paths, {'amonet/modules/main.py': '0'*64})
            self.assertEqual(different['packages'][0]['selected_files'][0]['mirror_comparison'], 'different')

    def test_unsafe_duplicate_oversized_selected_entries_rejected(self):
        for members in [[('../escape', b'x')],
                        [('amonet/modules/main.py', b'x'), ('release/amonet/modules/main.py', b'y')],
                        [('amonet/modules/main.py', b'x'*(ENTRY_CAP+1))]]:
            with self.subTest(members=[x[0] for x in members]), tempfile.TemporaryDirectory() as directory:
                with self.assertRaises(ValueError):
                    inspect(self.packages(directory, members))

    def test_symlink_and_combined_file_budget_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = self.packages(directory, [('ignored.bin', b'x')])
            link = Path(directory)/'link.zip'
            link.symlink_to(paths[0])
            with self.assertRaises(OSError):
                inspect([link, *paths[1:]])
            with paths[0].open('r+b') as stream:
                stream.truncate(CAP)
            with self.assertRaises(ValueError):
                inspect(paths)
