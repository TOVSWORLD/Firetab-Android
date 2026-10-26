"""Native host C unit tests; not ARM execution or a device transport."""
import pathlib
import shutil
import subprocess
import tempfile
import unittest


class NativeDispatcherTests(unittest.TestCase):
    def test_owned_c_core_with_synthetic_arrays_and_callbacks(self):
        compiler = shutil.which('cc')
        if compiler is None:
            self.skipTest('Host C compiler unavailable')
        root = pathlib.Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as folder:
            executable = pathlib.Path(folder) / 'host-protocol-test'
            subprocess.run([compiler, '-std=c11', '-Wall', '-Wextra', '-Werror',
                '-I', str(root/'diagnostic/protocol'), str(root/'diagnostic/protocol/dispatcher.c'),
                str(root/'tests/native/diagnostic_dispatcher_test.c'), '-o', str(executable)],
                check=True, capture_output=True, timeout=30)
            subprocess.run([str(executable)], check=True, capture_output=True, timeout=5)
