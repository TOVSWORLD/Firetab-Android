from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_forced_argument_inputs import keys, header_arguments


class ForcedArgumentInputTests(unittest.TestCase):
    def test_key_only_inventory_preserves_duplicates_without_values(self):
        self.assertEqual(keys('console=public console=private-value bootopt=x'),
                         ['console','console','bootopt'])
        for value in ['console=bad\nvalue','console=\x01','bad/key=1']:
            with self.assertRaises(ValueError):keys(value)

    def test_invalid_boot_header_cannot_supply_trusted_arguments(self):
        with self.assertRaises(ValueError):header_arguments(b'ANDROID!')
