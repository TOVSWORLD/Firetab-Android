import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate_iommu_dependencies import validate,PATHS


class IOMMUDependencies(unittest.TestCase):
    def fixture(self):return json.loads((ROOT/'evidence/iommu-smi-port/candidate-graph.json').read_text())

    def test_actual_graph_accepts_reviewed_duplicate_clock_roles(self):
        result=validate(self.fixture());self.assertEqual(result['larbs_checked'],4)
        self.assertFalse(result['runtime_qualified'])
        common=self.fixture()['nodes'][PATHS['common']]
        self.assertEqual(common['clocks'][:2],common['clocks'][2:])

    def test_missing_or_duplicate_larb_id_and_common_target_rejected(self):
        for change in ['id','common','disabled','references']:
            g=self.fixture();n=g['nodes'][PATHS['larb2']]
            if change=='id':n['mediatek,larb-id']=[1]
            elif change=='common':n['mediatek,smi']=[999]
            elif change=='disabled':n['status']=['disabled']
            else:g['nodes'][PATHS['iommu']]['mediatek,larbs'].pop()
            with self.assertRaises(ValueError,msg=change):validate(g)

    def test_clock_provider_role_id_or_power_domain_drift_rejected(self):
        for change in ['clock-id','provider','names','domain']:
            g=self.fixture();n=g['nodes'][PATHS['larb1']]
            if change=='clock-id':n['clocks'][1]=99
            elif change=='provider':n['clocks'][0]=999
            elif change=='names':n['clock-names']=['smi','apb']
            else:n['power-domains'][1]=0
            with self.assertRaises(ValueError,msg=change):validate(g)

    def test_iommu_bank_irq_cell_and_declared_resource_checks(self):
        for change in ['reg','irq','cells','duplicate']:
            g=self.fixture();n=g['nodes'][PATHS['iommu']]
            if change=='reg':n['reg'][-1]=2048
            elif change=='irq':n['interrupts']=[]
            elif change=='cells':n['#iommu-cells']=[2]
            else:n['phandle']=g['nodes'][PATHS['common']]['phandle']
            with self.assertRaises(ValueError,msg=change):validate(g)
