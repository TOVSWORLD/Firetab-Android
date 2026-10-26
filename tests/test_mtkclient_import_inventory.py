from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from inventory_mtkclient_cli_imports import imports


class ImportInventoryTests(unittest.TestCase):
    def test_import_optional_deferred_and_example_contexts_are_separate(self):
        source='''
raise RuntimeError('never execute upstream')
try:
 import optional_gui
except ImportError:
 import fallback
import mandatory
if __name__ == '__main__':
 import example_only
def later():
 import deferred
'''
        found={x['module']:x for x in imports(source)}
        self.assertTrue(found['optional_gui']['importerror_guard'])
        self.assertFalse(found['fallback']['importerror_guard'])
        self.assertTrue(found['example_only']['main_guard'])
        self.assertTrue(found['deferred']['deferred_scope'])
        self.assertFalse(found['mandatory']['deferred_scope'])

    def test_relative_import_is_not_mislabeled_as_resolved_external(self):
        found=imports('from . import sibling\nfrom package.module import Thing')
        self.assertTrue(found[0]['relative'])
        self.assertEqual(found[1]['module'],'package.module')
