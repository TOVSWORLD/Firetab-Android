import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('peripheral_bindings', ROOT/'scripts/validate_douglas_bindings.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PeripheralBindings(unittest.TestCase):
    def test_only_reviewed_compatible_changes_are_applied(self):
        data = json.loads((ROOT/'evidence/peripheral-bindings/changes.json').read_text())
        for change in data['changes']:
            with self.subTest(name=change['name']), tempfile.TemporaryDirectory() as directory:
                path = Path(directory)/change['schema']
                path.parent.mkdir(parents=True)
                evidence = ROOT/'evidence/peripheral-bindings'/change['name']
                original = (evidence/'original.yaml').read_bytes()
                path.write_bytes(original)
                module.apply_locked_proposal(Path(directory), data['ack_commit'], change['name']+'.json')
                proposed = path.read_bytes()
                self.assertEqual(proposed, (evidence/'proposed.yaml').read_bytes())
                self.assertEqual(proposed.replace(change['new'].encode(), change['old'].encode()), original)
                with self.assertRaisesRegex(ValueError, 'input hash'):
                    module.apply_locked_proposal(Path(directory), data['ack_commit'], change['name']+'.json')
