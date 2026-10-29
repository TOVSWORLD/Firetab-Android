import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from audit_usb_prerequisites import audit,source_facts


class USBPrerequisites(unittest.TestCase):
    def fixture(self):return json.loads((ROOT/'evidence/usb-prerequisites/candidate-graph.json').read_text())

    def test_actual_disabled_candidate_is_metadata_pass_without_transport_admission(self):
        r=audit(self.fixture())
        self.assertTrue(r['declaration_contract_passed'])
        self.assertTrue(r['diagnostic_fragment_requests_usb_disabled'])
        for key in ['candidate_controller_enabled','candidate_phy_enabled','source_variant_qualified','usb_build_integration_verified','device_transport_qualified','runtime_qualified']:
            self.assertFalse(r[key],key)

    def test_unreviewed_usb_or_phy_activation_is_rejected(self):
        for role in ['controller','phy']:
            for state in [None,['okay']]:
                g=self.fixture()
                if state is None:g['nodes'][role].pop('status')
                else:g['nodes'][role]['status']=state
                with self.assertRaises(ValueError,msg=(role,state)):audit(g)

    def test_candidate_clock_phy_bank_irq_and_mode_drift_rejected(self):
        for mutation in ['clock-id','supplier','clock-order','link','type','bank','irq','mode']:
            g=self.fixture();n=g['nodes']
            if mutation=='clock-id':n['controller']['clocks'][1]=999
            elif mutation=='supplier':n['port0']['clocks'][0]=999
            elif mutation=='clock-order':n['controller']['clock-names'].reverse()
            elif mutation=='link':n['controller']['phys'][0]=n['port1']['phandle'][0]
            elif mutation=='type':n['controller']['phys'][1]=4
            elif mutation=='bank':n['phy']['reg'][-1]=4096
            elif mutation=='irq':n['controller']['interrupts'][1]=73
            else:n['controller']['dr_mode']=['host']
            with self.assertRaises(ValueError,msg=mutation):audit(g)

    def test_actual_pinned_fallback_bank_and_formula_are_not_legacy_equivalence(self):
        facts=source_facts();r=audit(self.fixture())
        self.assertEqual(facts['ack_v1_frequency_bank_offset'],0x100)
        self.assertEqual(facts['legacy_frequency_bank_offset'],0xf00)
        self.assertEqual(r['source_derived_frequency_value_addresses'],{'ack_generic_v1':'0x1121010c','legacy_declared_sif':'0x11210f0c'})
        self.assertFalse(r['same_frequency_bank'])
        self.assertNotEqual(facts['ack_v1_default_ref_mhz'],facts['legacy_formula_ref'])
        self.assertFalse(facts['legacy_applies_computed_slew'])
        self.assertEqual(facts['legacy_fixed_slew_byte'],0x60)
