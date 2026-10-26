import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from verify_generic_force_evidence import verify


class RetainedForceEvidenceTests(unittest.TestCase):
    def inputs(self):
        folder=ROOT/'evidence/generic-forced-arguments'
        return json.loads((folder/'runtime-result.json').read_text()),(folder/'resolved.config').read_text()

    def test_executed_generic_evidence_retains_separate_physical_gate(self):
        record,config=self.inputs();result=verify(record,config)
        self.assertTrue(result['executed_generic_argument_selection_verified'])
        self.assertFalse(result['physical_test_ready'])
        self.assertFalse(result['primary_only_contract_observed'])

    def test_missing_conflict_bad_observation_or_hardware_claim_rejected(self):
        record,config=self.inputs()
        for change in ['incoming','observed','hardware']:
            bad=copy.deepcopy(record)
            if change=='incoming':bad['runtime']['command'][-1]='nr_cpus=1 maxcpus=0'
            elif change=='observed':bad['runtime']['cpu_contract']['verdicts']['LIMIT_MAXCPUS']='conflict'
            else:bad['runtime']['hardware_tested']=True
            with self.assertRaises(ValueError):verify(bad,config)
        with self.assertRaises(ValueError):verify(record,config+'\n# changed\n')
