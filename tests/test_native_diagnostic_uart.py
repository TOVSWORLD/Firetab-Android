"""Native synthetic register-array test, not device MMIO or ARM execution."""
import pathlib
import shutil
import subprocess
import tempfile
import unittest


class NativeUARTTests(unittest.TestCase):
    def test_bounded_polling_counts_and_divisor_alias_guard(self):
        cc=shutil.which('cc')
        if not cc:self.skipTest('Host C compiler unavailable')
        root=pathlib.Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as folder:
            executable=pathlib.Path(folder)/'synthetic-uart'
            subprocess.run([cc,'-std=c11','-Wall','-Wextra','-Werror','-I',str(root/'diagnostic/logging'),
                str(root/'diagnostic/logging/uart.c'),str(root/'diagnostic/logging/marker.c'),str(root/'tests/native/diagnostic_uart_test.c'),
                '-o',str(executable)],check=True,capture_output=True,timeout=30)
            subprocess.run([str(executable)],check=True,capture_output=True,timeout=5)
