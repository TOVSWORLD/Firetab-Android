import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('lab_gapps', Path(__file__).resolve().parents[1] / 'scripts/prepare_lab_gapps.py')
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

class InstallerGuards(unittest.TestCase):
    def test_exact_target_abi_guard(self):
        self.assertEqual(M.tests(), 35)

    def test_exact_helper_guard_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            helper = Path(directory) / 'toybox'
            for status in (0, 1, 126):
                helper.write_text('#!/bin/sh\nexit ' + str(status) + '\n')
                helper.chmod(0o700)
                shell = 'error() { exit 19; }; getprop2() { echo armv7l; };\n' + M.GUARD
                result = subprocess.run(['sh', '-c', shell], env={**os.environ, 'TMP': directory}, capture_output=True)
                self.assertEqual(result.returncode, 0 if status == 0 else 19)

    def test_unknown_package_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'wrong.zip'
            target = Path(directory) / 'output.zip'
            source.write_bytes(b'wrong input')
            with self.assertRaises(AssertionError):
                M.prepare(source, target)
            self.assertFalse(target.exists())
