import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('pmic_compare', Path(__file__).resolve().parents[1] / 'scripts/compare_pmic_dtb.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PMICComparison(unittest.TestCase):
    def trees(self):
        baseline = {module.PREFIX + old: {'compatible': '1 2 3'} for old in module.RENAMES}
        candidate = {module.PREFIX + new: {'compatible': '1 2 3'} for new in module.RENAMES.values()}
        baseline['/memory@40000000'] = {'reg': '00 40 00 00'}
        candidate['/memory@40000000'] = {'reg': '00 40 00 00'}
        return baseline, candidate

    def test_only_allowed_path_renames_pass(self):
        self.assertTrue(module.compare(*self.trees())['property_values_identical'])

    def test_reject_property_change(self):
        old, new = self.trees()
        new['/memory@40000000']['reg'] = 'ff'
        with self.assertRaises(ValueError):
            module.compare(old, new)

    def test_reject_unexpected_node(self):
        old, new = self.trees()
        new['/unexpected'] = {}
        with self.assertRaises(ValueError):
            module.compare(old, new)

    def test_reject_missing_baseline(self):
        with self.assertRaises(ValueError):
            module.compare({}, {})
