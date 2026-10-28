import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate_lk_handoff_coverage import validate


class LKHandoffCoverage(unittest.TestCase):
    def packet(self):return json.loads((ROOT/'evidence/lk-handoff-coverage/manifest.json').read_text())

    def test_source_consistency_never_implies_runtime_admission(self):
        result=validate(self.packet())
        self.assertEqual(result['receipts_checked'],9)
        self.assertEqual(result['qualified_runtime_gates'],0)
        self.assertFalse(result['ready_for_loading_trial'])
        self.assertFalse(result['beta_ready'])

    def test_runtime_promotion_rejected(self):
        for key in ['ready_for_loading_trial','beta_ready']:
            p=self.packet();p[key]=True
            with self.assertRaises(ValueError):validate(p)
        for gate in self.packet()['runtime_gates']:
            p=self.packet();p['runtime_gates'][gate]['qualified']=True
            with self.assertRaises(ValueError):validate(p)

    def test_missing_duplicate_cross_artifact_and_external_receipts_rejected(self):
        for change in ['missing','duplicate','artifact','outside','hash']:
            p=self.packet()
            if change=='missing':p['receipts'].pop()
            elif change=='duplicate':p['receipts'][-1]=copy.deepcopy(p['receipts'][0])
            elif change=='artifact':p['receipts'][0]['lk_sha256']='0'*64
            elif change=='outside':p['receipts'][0]['evidence']='../private/report.json'
            else:p['receipts'][0]['receipt_sha256']='0'*64
            with self.assertRaises(ValueError,msg=change):validate(p)

    def test_receipt_content_drift_rejected(self):
        p=self.packet()
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for row in p['receipts']:
                target=root/row['evidence'];target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes((ROOT/row['evidence']).read_bytes())
            validate(p,root)
            target=root/p['receipts'][-1]['evidence'];target.write_text(target.read_text()+'\n')
            with self.assertRaises(ValueError):validate(p,root)
