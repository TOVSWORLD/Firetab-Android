import json
from pathlib import Path
import struct
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from trace_lk_handoff import arm_branch, thumb_call, analysis_object, trace


class LKHandoff(unittest.TestCase):
    def fixture(self):
        entries = json.loads((ROOT/'evidence/lk-handoff/anchors.json').read_text())['ranges']
        size = json.loads((ROOT/'evidence/ota-loaders/inspection-result.json').read_text())['loader_images']['lk.bin']['bytes']-512
        data = bytearray(size)
        for item in entries:
            raw = bytes.fromhex(item['hex'])
            data[item['offset']:item['offset']+len(raw)] = raw
        return data

    def test_signed_arm_and_thumb_cross_state_targets(self):
        self.assertEqual(arm_branch(0xea000007, 0), 0x24)
        self.assertEqual(arm_branch(0xeafffffe, 0x100), 0x100)
        self.assertEqual(thumb_call(0xf7ff, 0xfb44, 0x3e744), 0x3ddd0)
        self.assertEqual(thumb_call(0xf7fe, 0xed78, 0x3ddec), 0x3c8e0)
        with self.assertRaises(ValueError):
            arm_branch(0, 0)
        with self.assertRaises(ValueError):
            thumb_call(0xf7fe, 0xed79, 0x3ddec)

    def test_analysis_object_is_relocatable_without_entry_or_program_headers(self):
        raw = analysis_object(b'bytes for static analysis')
        header = struct.unpack_from('<16sHHIIIIIHHHHHH', raw)
        self.assertEqual((header[1], header[4], header[5], header[10]), (1, 0, 0, 0))
        self.assertEqual(raw[256:281], b'bytes for static analysis')
        with self.assertRaises(ValueError):
            analysis_object(b'')

    def test_selected_actual_anchors_preserve_limits_of_claim(self):
        result = trace(self.fixture())
        self.assertEqual(result['linked_base_from_startup_literal'], '0x4bd00000')
        self.assertEqual(result['smc_function_id'], '0x82000200')
        self.assertIn('jump to K64', result['k64_log_reference']['text'])
        self.assertEqual(result['fdt_label_reference']['text'], 'boot_linux_fdt')
        self.assertEqual(result['smc_registers_on_checked_path']['r3'], 0)
        self.assertEqual(result['smc_registers_on_checked_path']['r4'], 1)
        self.assertFalse(result['complete_parameter_lineage_verified'])
        self.assertFalse(result['secure_monitor_behavior_verified'])
        self.assertFalse(result['runtime_boot_verified'])

    def test_changed_instruction_anchor_refused(self):
        for offset, mask in [(0, 1), (0x48, 1), (0x3e73c, 1), (0x3c8f4, 1), (0x3e744, 1), (0x3ddef, 0x10)]:
            data = self.fixture()
            data[offset] ^= mask
            with self.assertRaises(ValueError):
                trace(data)
