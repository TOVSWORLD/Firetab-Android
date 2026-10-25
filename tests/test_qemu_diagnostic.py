from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_qemu_diagnostic as guest
import install_qemu_for_ci as dependencies


class GenericVMChecks(unittest.TestCase):
    def complete(self):
        return b'\n'.join(guest.MARKERS) + b'\nEND_FILE'*4

    def test_all_markers_and_completed_reads_are_required(self):
        self.assertTrue(guest.transcript_ready(self.complete()))
        self.assertFalse(guest.transcript_ready(b'\n'.join(guest.MARKERS)))
        self.assertFalse(guest.transcript_ready(self.complete().replace(b'MemTotal:', b'')))

    def test_panic_overrides_apparently_complete_markers(self):
        with self.assertRaisesRegex(ValueError, 'panic/Oops'):
            guest.transcript_ready(self.complete()+b'Kernel panic - not syncing')

    def test_failed_metadata_read_is_not_runtime_success(self):
        with self.assertRaises(ValueError):
            guest.transcript_ready(self.complete()+b'\nUNAVAILABLE\n')

    def test_apt_archive_bytes_are_summed(self):
        self.assertEqual(dependencies.package_bytes("'https://example/a.deb' a.deb 100 MD5Sum:x\n'https://example/b.deb' b.deb 200 MD5Sum:y"), 300)

    def test_oversized_or_unparseable_apt_plan_is_rejected(self):
        for plan in [f"'https://example/a' a {dependencies.LIMIT+1} hash", "'https://example/a' a unknown hash"]:
            with self.assertRaises(ValueError):
                dependencies.package_bytes(plan)
