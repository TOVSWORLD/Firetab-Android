from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from offline_mode_evidence import decode_mode_reply


class ModeEvidenceTests(unittest.TestCase):
    def test_prior_echo_does_not_leak_into_next_non_echo(self):
        first=decode_mode_reply(query_byte=b'Q',reply=b'Q')
        second=decode_mode_reply(query_byte=b'Q',reply=b'V')
        self.assertEqual(first['source_candidate'],'brom_echo')
        self.assertEqual(second['source_candidate'],'unknown')
        for result in [first,second]:
            self.assertFalse(result['protocol_mode_verified'])
            self.assertFalse(result['bootstrap_authorized'])
        first['source_candidate']='changed'
        self.assertEqual(second['source_candidate'],'unknown')

    def test_missing_or_extra_reply_never_reuses_prior_evidence(self):
        for reply in [None,False,b'',b'QQ']:
            with self.assertRaises(ValueError):decode_mode_reply(query_byte=b'Q',reply=reply)
