import json
from pathlib import Path
import struct
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audit_pl7_recovery import audit, mapped_object


class PL7Recovery(unittest.TestCase):
    def fixture(self):
        data = bytearray(139352)
        for item in json.loads((ROOT/'evidence/pl7-recovery-code/windows.json').read_text())['windows']:
            raw = bytes.fromhex(item['hex'])
            data[item['file_offset']:item['file_offset']+len(raw)] = raw
        return data

    def test_reference_site_is_a_literal_not_a_usb_patch_instruction(self):
        facts = audit(self.fixture())
        self.assertEqual(facts['usb_literal_reference']['text'], '       wLength = %x\n\n')
        self.assertFalse(facts['reference_patch_set_qualified_for_current_preloader'])
        self.assertFalse(facts['marker_absence_proves_exploit_patched'])
        self.assertFalse(facts['physical_boot_or_recovery_verified'])
        self.assertEqual(facts['checked_arb_call']['target'],'0x201934')

    def test_changed_header_literal_or_call_refused(self):
        for at in (28,0x16720,0x164d8,0x9ace,0x1ac70,0xc34):
            data = self.fixture()
            data[at] ^= 1
            with self.assertRaises(ValueError):
                audit(data)

    def test_analysis_object_has_mapping_but_no_entry_or_program_headers(self):
        raw = mapped_object(self.fixture())
        header = struct.unpack_from('<16sHHIIIIIHHHHHH',raw)
        self.assertEqual((header[1],header[4],header[5],header[10]),(1,0,0,0))
        self.assertEqual(struct.unpack_from('<I',raw,header[6]+40+12)[0],0x200d00)
