import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_douglas_bindings import bounded_result_name


class BindingResultPaths(unittest.TestCase):
    def test_existing_paths_preserved_at_boundary(self):
        for n in [6,248,255]:
            name='x'*n
            self.assertEqual(bounded_result_name(name),name)

    def test_long_profiles_are_stable_distinct_and_bounded(self):
        a='result-'+('mt8163-provider-'*20)
        b=a+'extra-provider'
        self.assertEqual(bounded_result_name(a),bounded_result_name(a))
        self.assertNotEqual(bounded_result_name(a),bounded_result_name(b))
        self.assertLessEqual(len(bounded_result_name(a).encode()),255)

    def test_limit_is_bytes_not_character_count(self):
        name='é'*128
        self.assertLessEqual(len(bounded_result_name(name).encode()),255)
        self.assertNotEqual(bounded_result_name(name),name)
