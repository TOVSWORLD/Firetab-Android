import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from offline_security_observation import decode_target_config


class SecurityObservationTests(unittest.TestCase):
    def test_all_security_combinations_are_reported_not_authorized(self):
        for flags in range(8):
            result=decode_target_config(flags.to_bytes(4,'big')+bytes(2))
            for key,bit in [('sbc_reported',1),('sla_reported',2),('daa_reported',4)]:
                self.assertEqual(result[key],bool(flags & bit))
            self.assertFalse(result['bootstrap_authorized'])
            self.assertFalse(result['response_provenance_verified'])

    def test_missing_unsupported_status_and_bad_lengths_never_become_disabled(self):
        for reply in [None,False,b'',bytes(5),bytes(7),bytes(4)+b'\x00\x01']:
            with self.assertRaises(ValueError):decode_target_config(reply)
