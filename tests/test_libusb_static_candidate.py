from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from stage_libusb_static_candidate import extract, fetch


class PinnedNativeCandidateTests(unittest.TestCase):
    def test_wrong_bytes_fail_before_archive_parser(self):
        with patch('tarfile.open',side_effect=AssertionError('Untrusted bytes must not reach parser')):
            with self.assertRaises(ValueError):extract(b'not the pinned bottle')

    def test_oversized_download_fails_before_persistence_or_archive(self):
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,maximum):return b'x'*maximum
        with patch('urllib.request.urlopen',return_value=Response()):
            with self.assertRaises(ValueError):fetch()
