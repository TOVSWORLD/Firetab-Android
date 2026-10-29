import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from check_ordered_roadmap import validate
class OrderedRoadmap(unittest.TestCase):
 def setUp(self):self.plan=json.loads((ROOT/'docs/development/ordered-roadmap.json').read_text())
 def test_real_plan_has14_groups_and_single_execution_contract(self):self.assertEqual(validate(self.plan)['hardware_groups'],14)
 def test_duplicate_hardware_group_rejected(self):
  h=[t for t in self.plan['tasks'] if t['hardware_group']];h[1]['hardware_group']=h[0]['hardware_group']
  with self.assertRaises(ValueError):validate(self.plan)
 def test_forward_cycle_dependency_rejected(self):
  self.plan['tasks'][2]['depends_on']=[341]
  with self.assertRaises(ValueError):validate(self.plan)
 def test_task_cannot_attach_directly_to_feature(self):
  self.plan['tasks'][0]['parent']=8
  with self.assertRaises(ValueError):validate(self.plan)
 def test_missing_issue_pr_contract_rejected(self):
  self.plan['pr_contract']['primary_task_issue_required']=False
  with self.assertRaises(ValueError):validate(self.plan)
 def test_closed_nogo_cannot_implicitly_unblock_trial(self):
  next(t for t in self.plan['tasks'] if t['issue']==347)['conditions']=[]
  with self.assertRaises(ValueError):validate(self.plan)
