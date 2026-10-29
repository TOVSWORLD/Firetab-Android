import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from apply_iommu_port import apply
LOCK=json.loads((ROOT/'projects/firetabs-android/kernel/iommu-port/inputs.json').read_text())


class IOMMUPort(unittest.TestCase):
    def tree(self,root):
        for row in LOCK['files']:
            target=root/row['target'];target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/row['original_source'],target)

    def test_actual_pinned_patch_and_unchanged_common_functions(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.tree(root);result=apply(root,LOCK['ack_commit'])
            self.assertFalse(result['runtime_qualified'])
            for row in LOCK['files']:
                original=(ROOT/row['original_source']).read_text();proposed=(root/row['target']).read_text()
                if 'iommu' in row['target']:
                    start='static int mtk_iommu_probe(';end='static void mtk_iommu_remove('
                else:
                    start='static int mtk_smi_larb_probe(';end='static void mtk_smi_larb_remove('
                self.assertEqual(original.split(start)[1].split(end)[0],proposed.split(start)[1].split(end)[0])
            with self.assertRaises(ValueError):apply(root,LOCK['ack_commit'])

    def test_revision_or_input_drift_rejected_before_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.tree(root)
            with self.assertRaises(ValueError):apply(root,'wrong')
            row=LOCK['files'][0];target=root/row['target'];target.write_bytes(target.read_bytes()+b'\n')
            other=root/LOCK['files'][1]['target'];unchanged=other.read_bytes()
            with self.assertRaises(ValueError):apply(root,LOCK['ack_commit'])
            self.assertEqual(other.read_bytes(),unchanged)
