import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate_usb_variant_definition import validate,validate_resources,legacy_byte,ack_field,DEFINITION


class USBVariantDefinition(unittest.TestCase):
    def fixture(self):return json.loads(DEFINITION.read_text())

    def test_finite_source_result_and_dedicated_resource(self):
        r=validate(self.fixture())
        self.assertEqual(r['states_checked'],65536)
        self.assertEqual(r['difference_masks']['eye_src6_shortcut'],'0x8700')
        self.assertEqual(r['frequency_value_address'],'0x11210f0c')
        self.assertTrue(r['resource_intervals_disjoint'])
        self.assertFalse(r['kernel_implementation_complete'])
        self.assertFalse(r['runtime_qualified'])

    def test_concrete_byte_vs_field_counterexample_and_high_bits(self):
        for high in [0,0x12340000,0xffff0000]:
            initial=high|0x8700
            self.assertEqual(legacy_byte(initial),high|0x6000)
            self.assertEqual(ack_field(initial,True),high|0x6700)
            self.assertEqual(ack_field(initial,False),high|0xe700)

    def test_naive_parent_expansion_overlaps_claimed_child(self):
        d=self.fixture();d['resources'][0]['length']=4096
        with self.assertRaisesRegex(ValueError,'Overlapping ownership'):validate_resources(d['resources'])
        d=self.fixture();d['resources'][1]['start']=0x11210800
        with self.assertRaisesRegex(ValueError,'Overlapping ownership'):validate_resources(d['resources'])

    def test_unqualified_policy_resource_or_readiness_drift_rejected(self):
        for change in ['missing-bank','wrong-bank','timeout','skip','override','byte','enable','generic-change']:
            d=self.fixture()
            if change=='missing-bank':d['resources'].pop(1)
            elif change=='wrong-bank':d['resources'][1]['start']=0x11210e00
            elif change=='timeout':d['frequency_bank']['timeout_us']=200
            elif change=='skip':d['slew_policy']['measurement_required']=False
            elif change=='override':d['slew_policy']['explicit_eye_override_action']='skip_measurement'
            elif change=='byte':d['slew_policy']['byte_value']=0x40
            elif change=='enable':d['candidate_enable_allowed']=True
            else:d['non_mt8163_changes_allowed']=True
            with self.assertRaises(ValueError,msg=change):validate(d)
