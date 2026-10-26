from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_qemu_diagnostic as guest
import install_qemu_for_ci as dependencies


class GenericVMChecks(unittest.TestCase):
    def complete(self):
        return b'\n'.join(guest.MARKERS) + b'\nEND_FILE'*4 + b'\nFIRETABS_CPU_CONTRACT_V1\nLIMIT_NR_CPUS=missing\nLIMIT_MAXCPUS=missing\nONLINE_CPUS=1\nONLINE_BOOT_CPU_ONLY=yes\nPSCI_DT_STATUS=unavailable\nFIRETABS_CPU_CONTRACT_END\n'

    def test_all_markers_and_completed_reads_are_required(self):
        self.assertTrue(guest.transcript_ready(self.complete()))
        self.assertFalse(guest.transcript_ready(b'\n'.join(guest.MARKERS)))
        self.assertFalse(guest.transcript_ready(self.complete().replace(b'MemTotal:', b'')))

    def test_panic_overrides_apparently_complete_markers(self):
        with self.assertRaisesRegex(ValueError, 'panic/Oops'):
            guest.transcript_ready(self.complete()+b'Kernel panic - not syncing')

    def test_failed_metadata_read_is_not_runtime_success(self):
        for ending in [b'\n', b'\r\n']:
            for error in [b'UNAVAILABLE', b'READ_ERROR']:
                with self.subTest(ending=ending, error=error):
                    with self.assertRaisesRegex(ValueError, 'diagnostic read failure'):
                        guest.transcript_ready(self.complete().replace(b'\n', ending)+ending+error+ending)

    def test_apt_archive_bytes_are_summed(self):
        self.assertEqual(dependencies.package_bytes("'https://example/a.deb' a.deb 100 MD5Sum:x\n'https://example/b.deb' b.deb 200 MD5Sum:y"), 300)

    def test_oversized_or_unparseable_apt_plan_is_rejected(self):
        for plan in [f"'https://example/a' a {dependencies.LIMIT+1} hash", "'https://example/a' a unknown hash"]:
            with self.assertRaises(ValueError):
                dependencies.package_bytes(plan)

    def test_forced_arguments_need_actual_verdicts_not_just_cpu_count(self):
        with self.assertRaises(ValueError):guest.forced_argument_result(self.complete())
        good=self.complete().replace(b'LIMIT_NR_CPUS=missing',b'LIMIT_NR_CPUS=valid').replace(
            b'LIMIT_MAXCPUS=missing',b'LIMIT_MAXCPUS=valid')
        self.assertTrue(guest.forced_argument_result(good)['forced_limits_observed'])
        self.assertFalse(guest.cpu_contract_report(good)['primary_only_contract_observed'])
        with self.assertRaises(ValueError):
            guest.forced_argument_result(good.replace(b'LIMIT_MAXCPUS=valid',b'LIMIT_MAXCPUS=conflict'))
