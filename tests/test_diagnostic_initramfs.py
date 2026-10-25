import importlib.util
from pathlib import Path
import struct
import unittest

spec = importlib.util.spec_from_file_location('diagnostic', Path(__file__).resolve().parents[1] / 'scripts/build_diagnostic_initramfs.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DiagnosticArtifacts(unittest.TestCase):
    def elf(self, program_type=1):
        data = bytearray(128)
        data[:7] = b'\x7fELF\x02\x01\x01'
        struct.pack_into('<HH', data, 16, 2, 183)
        struct.pack_into('<Q', data, 24, 0x400000)
        struct.pack_into('<Q', data, 32, 64)
        struct.pack_into('<HH', data, 54, 56, 1)
        struct.pack_into('<IIQQQQQQ', data, 64, program_type, 5, 0, 0x400000, 0, 128, 128, 4096)
        return data

    def test_elf_rejects_dynamic_interpreter_and_invalid_entry(self):
        self.assertFalse(module.inspect_elf(self.elf())['dynamic'])
        for kind in (2, 3):
            with self.assertRaises(ValueError):
                module.inspect_elf(self.elf(kind))
        data = self.elf()
        struct.pack_into('<Q', data, 24, 0x500000)
        with self.assertRaises(ValueError):
            module.inspect_elf(data)

    def test_elf_rejects_truncation_and_wrong_architecture(self):
        for data in (b'', self.elf()[:100]):
            with self.assertRaises(ValueError):
                module.inspect_elf(data)
        data = self.elf()
        struct.pack_into('<H', data, 18, 62)
        with self.assertRaises(ValueError):
            module.inspect_elf(data)

    def test_newc_content_alignment_metadata_and_determinism(self):
        entries = [('dev', 0o040755, b'', (0, 0)), ('dev/console', 0o020600, b'', (5, 1)), ('init', 0o100755, b'example', (0, 0))]
        data = module.archive(entries)
        self.assertEqual(data, module.archive(entries))
        self.assertEqual(len(data) % 512, 0)
        offset = 0
        actual = []
        while True:
            self.assertEqual(data[offset:offset+6], b'070701')
            fields = [int(data[offset+6+i*8:offset+14+i*8], 16) for i in range(13)]
            self.assertEqual(fields[2:6], [0, 0, 1, 0])
            begin = offset + 110
            name = data[begin:begin+fields[11]-1].decode()
            begin = (begin + fields[11] + 3) & ~3
            payload = data[begin:begin+fields[6]]
            offset = (begin + fields[6] + 3) & ~3
            if name == 'TRAILER!!!': break
            actual.append((name, fields[1], payload, (fields[9], fields[10])))
        self.assertEqual(actual, entries)
