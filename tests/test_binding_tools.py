import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from setup_binding_tools import select_items
from setup_dtb_tools import fetch

class BindingTools(unittest.TestCase):
    def test_locked_build_requirements_platform_and_total_budget(self):
        lock=json.loads((ROOT/'projects/firetabs-android/kernel/dtb/schema-tools.lock.json').read_text())
        items=select_items(lock,'Linux-x86_64','3.12');self.assertEqual(len(items),16);self.assertEqual(sum(x['bytes'] for x in items),4031591)
        for key,version in [('Darwin-arm64','3.15'),('Linux-x86_64','3.15')]:
            with self.assertRaises(ValueError):select_items(lock,key,version)
        changed=copy.deepcopy(lock);changed['max_download_bytes']=1
        with self.assertRaises(ValueError):select_items(changed,'Linux-x86_64','3.12')
        changed=copy.deepcopy(lock);changed['items'][0]['filename']='../escape.whl'
        with self.assertRaises(ValueError):select_items(changed,'Linux-x86_64','3.12')
    def test_cached_artifact_drift_and_missing_never_fetch_without_optin(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);raw=b'expected';item={'filename':'tool.whl','url':'https://files.pythonhosted.org/tool.whl','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
            with self.assertRaises(ValueError):fetch(item,root,False)
            (root/'tool.whl').write_bytes(b'drift')
            with self.assertRaises(ValueError):fetch(item,root,False)
            (root/'tool.whl').write_bytes(raw);self.assertEqual(fetch(item,root,False).read_bytes(),raw)

if __name__=='__main__':unittest.main()
