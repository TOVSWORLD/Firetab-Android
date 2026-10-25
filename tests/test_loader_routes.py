import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from audit_loader_routes import assess


class LoaderRoutes(unittest.TestCase):
    def inputs(self):
        return (json.loads((ROOT/'evidence/stock-facts/runtime-contract.json').read_text()),
                json.loads((ROOT/'evidence/loader-routes/sources.json').read_text()))

    def test_actual_versions_reject_software_gate_but_do_not_prove_all_routes_impossible(self):
        result = assess(*self.inputs())
        self.assertFalse(result['legacy_software_version_gate_passes'])
        self.assertEqual(set(result['exceeded_version_limits']), {'preloader', 'lk', 'tee'})
        self.assertFalse(any(x['ready_for_custom_kernel'] for x in result['routes']))
        self.assertFalse(result['diagnostic_package_ready'])

    def test_older_versions_do_not_automatically_qualify_a_route(self):
        stock, sources = self.inputs()
        stock['loader_versions_decimal'] = sources['legacy_software_maximum_versions'].copy()
        result = assess(stock, sources)
        self.assertTrue(result['legacy_software_version_gate_passes'])
        self.assertFalse(any(x['ready_for_custom_kernel'] for x in result['routes']))

    def test_missing_or_invalid_version_is_not_treated_as_zero(self):
        for value in [-1, '7', True]:
            stock, sources = self.inputs()
            stock['loader_versions_decimal']['preloader'] = value
            with self.assertRaises(ValueError):
                assess(stock, sources)
        stock, sources = self.inputs()
        del stock['loader_versions_decimal']['tee']
        with self.assertRaises(ValueError):
            assess(stock, sources)
