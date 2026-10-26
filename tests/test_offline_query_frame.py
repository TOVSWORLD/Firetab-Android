from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from offline_query_frame import validate_frame


class QueryFrameTests(unittest.TestCase):
    def test_synthetic_echo_and_payload_exact_match(self):
        self.assertEqual(validate_frame(command=b'Q',echo=b'Q',payload=bytes(4),expected_bytes=4),bytes(4))

    def test_unknown_echo_and_faulty_payload_are_not_evidence(self):
        for echo,payload in [(b'',bytes(4)),(b'X',bytes(4)),(b'QQ',bytes(4)),
                             (b'Q',bytes(3)),(b'Q',bytes(5)),(b'Q',None)]:
            with self.assertRaises(ValueError):
                validate_frame(command=b'Q',echo=echo,payload=payload,expected_bytes=4)
