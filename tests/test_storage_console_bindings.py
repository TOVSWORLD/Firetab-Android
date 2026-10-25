import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('storage_bindings', ROOT/'scripts/validate_douglas_bindings.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class StorageConsoleBindings(unittest.TestCase):
    def test_locked_proposals_preserve_all_other_constraint_bytes(self):
        cases = [('mt8163-mmc', 'mmc/mtk-sd.yaml',
                  b'          - enum:\n              - mediatek,mt7623-mmc\n              - mediatek,mt8163-mmc\n',
                  b'          - const: mediatek,mt7623-mmc\n'),
                 ('mt8163-uart-dma', 'dma/mediatek,uart-dma.yaml',
                  b'              - mediatek,mt8163-uart-dma\n', b'')]
        for name, schema, added, original_text in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                path = Path(directory)/schema
                path.parent.mkdir()
                evidence = ROOT/'evidence/storage-console-bindings'/name
                original = (evidence/'original.yaml').read_bytes()
                path.write_bytes(original)
                module.apply_locked_proposal(Path(directory), 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87', name+'.json')
                proposed = path.read_bytes()
                self.assertEqual(proposed, (evidence/'proposed.yaml').read_bytes())
                self.assertEqual(proposed.replace(added, original_text), original)
                with self.assertRaisesRegex(ValueError, 'input hash'):
                    module.apply_locked_proposal(Path(directory), 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87', name+'.json')
