from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from plan_mac_cli_packages import candidate


class MacPackagePlanTests(unittest.TestCase):
    def metadata(self):
        return {'info':{'name':'pycryptodomex','version':'3.24.1','requires_dist':None},
                'urls':[{'filename':'pycryptodomex-3.24.1-cp37-abi3-macosx_10_9_universal2.whl',
                         'size':100,'url':'https://files.pythonhosted.org/example',
                         'digests':{'sha256':'a'*64},'yanked':False}]}

    def test_candidate_is_not_an_installed_or_runtime_qualified_package(self):
        result=candidate(self.metadata(),'pycryptodomex','3.24.1')
        self.assertFalse(result['wheel_downloaded'])
        self.assertFalse(result['runtime_compatibility_verified'])

    def test_wrong_namespace_version_yank_or_free_thread_abi_not_substituted(self):
        for change in ('version','yanked','abi'):
            meta=self.metadata()
            if change=='version':meta['info']['version']='4.1.0'
            elif change=='yanked':meta['urls'][0]['yanked']=True
            else:meta['urls'][0]['filename']=meta['urls'][0]['filename'].replace('cp37-abi3','cp314-cp314t')
            with self.assertRaises(ValueError):candidate(meta,'pycryptodomex','3.24.1')
