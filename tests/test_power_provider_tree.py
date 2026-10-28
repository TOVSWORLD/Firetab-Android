"""Reject unsafe captured-tree topology/reference drift before device work."""
import importlib.util
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('power_tree',ROOT/'scripts/validate_power_provider_tree.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class PowerProviderTree(unittest.TestCase):
    def setUp(self):
        self.node=json.loads((ROOT/'evidence/scpsys-binding/captured-node.json').read_text())
        self.controller=self.node['power-controller']
    def test_actual_captured_tree(self):
        self.assertEqual(module.validate(self.node,2,3)['mfg_parent'],6)
    def test_wrong_bus_protection_target(self):
        self.controller['power-domain@0']['mediatek,infracfg']=[[3]]
        with self.assertRaisesRegex(ValueError,'INFRACFG'):module.validate(self.node,2,3)
    def test_mfg_cannot_be_flattened(self):
        self.controller['power-domain@7']=self.controller['power-domain@6'].pop('power-domain@7')
        with self.assertRaisesRegex(ValueError,'hierarchy'):module.validate(self.node,2,3)
    def test_duplicate_id_rejected(self):
        self.controller['power-domain@1']['reg']=[[2]]
        with self.assertRaisesRegex(ValueError,'duplicated'):module.validate(self.node,2,3)
    def test_disabling_domain_cannot_obtain_pass(self):
        self.controller['power-domain@4']['status']=['disabled']
        with self.assertRaisesRegex(ValueError,'disable/drop'):module.validate(self.node,2,3)
    def test_clock_name_count_must_match(self):
        self.controller['power-domain@1'].pop('clock-names')
        with self.assertRaisesRegex(ValueError,'clock/name'):module.validate(self.node,2,3)

    def test_stock_mfg_id_is_not_candidate_mfg(self):
        self.controller['power-domain@6']['clocks']=[[3,70]]
        with self.assertRaisesRegex(ValueError,'clock provider/ID'):module.validate(self.node,2,3)
    def test_stock_mm_id_is_not_candidate_mm(self):
        self.controller['power-domain@0']['clocks']=[[3,67]]
        with self.assertRaisesRegex(ValueError,'clock provider/ID'):module.validate(self.node,2,3)
    def test_wrong_clock_provider_cannot_pass_by_cell_count(self):
        self.controller['power-domain@6']['clocks']=[[2,54]]
        with self.assertRaisesRegex(ValueError,'clock provider/ID'):module.validate(self.node,2,3)
