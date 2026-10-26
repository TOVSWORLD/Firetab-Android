import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from verify_recovery_material_match import verify


class OfficialRecoveryMatch(unittest.TestCase):
    def load(self,build):
        return json.loads((ROOT/'evidence/official-recovery-material'/(build+'.json')).read_text())

    def test_mirror_pair_matches_older_amazon_served_build(self):
        facts=verify(self.load('636558520'),'50.6.3.6_user_636558520')
        self.assertTrue(all(x['matches_mirrored_candidate'] for x in facts['matches'].values()))
        self.assertFalse(facts['downgrade_or_recovery_ready'])
        self.assertFalse(facts['installed_antirollback_compatibility_verified'])

    def test_intermediate_and_newer_builds_keep_components_distinct(self):
        mid=verify(self.load('657611720'),'50.6.5.7_user_657611720')
        self.assertTrue(mid['matches']['preloader.bin']['matches_mirrored_candidate'])
        self.assertTrue(mid['matches']['lk.bin']['matches_current_stock_candidate'])
        latest=verify(self.load('659662320'),'50.6.5.9_user_659662320')
        self.assertTrue(all(x['matches_current_stock_candidate'] for x in latest['matches'].values()))

    def test_untrusted_host_identity_resource_or_scope_claim_refused(self):
        changes=[('url','https://untrusted.example/firmware'),('response_body_bytes',2097153),
                 ('signature_verified',True),('full_package_downloaded',True)]
        for key,value in changes:
            data=self.load('636558520');data[key]=value
            with self.assertRaises(ValueError):verify(data,'50.6.3.6_user_636558520')
        data=self.load('636558520');data['identity']['ro.product.device']=['suez']
        with self.assertRaises(ValueError):verify(data,'50.6.3.6_user_636558520')
        with self.assertRaises(ValueError):verify(self.load('636558520'),'wrong-build')
