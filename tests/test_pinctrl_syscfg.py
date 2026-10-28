import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate_pinctrl_syscfg import validate,source_layout
from validate_douglas_bindings import apply_locked_proposal


class PinctrlSyscfg(unittest.TestCase):
    def fixture(self):
        return {'provider':{'compatible':['mediatek,mt8163-pctl-a-syscfg','syscon'],
                'phandle':14,'reg':[[0,0x10005000,0,4096]]},
                'consumer':{'compatible':['mediatek,mt8163-pinctrl'],'mediatek,pctl-regmap':[[14]]}}

    def test_known_source_extent_and_symbolic_phandle(self):
        result=validate(self.fixture());self.assertEqual(result['source_layout']['required_extent_bytes'],0xf5c)
        self.assertFalse(result['runtime_qualified'])
        node=self.fixture();node['provider']['phandle']=42;node['consumer']['mediatek,pctl-regmap']=[[42]]
        self.assertEqual(validate(node)['provider_phandle'],42)

    def test_wrong_or_missing_target_and_unused_second_map_rejected(self):
        for target in [[],[[13]],[[14],[15]],[[14,0]]]:
            node=self.fixture();node['consumer']['mediatek,pctl-regmap']=target
            with self.assertRaises(ValueError):validate(node)

    def test_resource_underflow_wrong_base_growth_or_disabled_rejected(self):
        for reg in [[[0,0x10005000,0,0xf58]],[[0,0x10004000,0,4096]],[[0,0x10005000,0,8192]],[[False,0x10005000,0,4096]],[1],[]]:
            node=self.fixture();node['provider']['reg']=reg
            with self.assertRaises(ValueError):validate(node)
        node=self.fixture();node['provider']['status']=['disabled']
        with self.assertRaises(ValueError):validate(node)

    def test_patch_only_changes_exact_provider_compatibles(self):
        evidence=ROOT/'evidence/pinctrl-syscfg-binding'
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);p=root/'mfd/syscon.yaml';p.parent.mkdir();original=(evidence/'original.yaml').read_bytes();p.write_bytes(original)
            apply_locked_proposal(root,'d9318bdb4c34e8b2d997b4f67ced56b120b22b87','mt8163-pctl-syscfg.json')
            proposed=p.read_bytes();self.assertEqual(proposed,(evidence/'proposed.yaml').read_bytes())
            self.assertEqual(proposed.replace(b'          - mediatek,mt8163-pctl-a-syscfg\n',b''),original)
            with self.assertRaises(ValueError):apply_locked_proposal(root,'d9318bdb4c34e8b2d997b4f67ced56b120b22b87','mt8163-pctl-syscfg.json')
