import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('binding_repair', ROOT/'scripts/validate_douglas_bindings.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class GunyahRepair(unittest.TestCase):
    def test_exact_repair_changes_only_three_indentation_tabs(self):
        with tempfile.TemporaryDirectory() as d:
            schema = Path(d)/'firmware/gunyah-cma-mem.yaml'
            schema.parent.mkdir()
            original = (ROOT/'evidence/gunyah-binding/original.yaml').read_bytes()
            schema.write_bytes(original)
            module.apply_gunyah_yaml_repair(Path(d), 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87')
            self.assertEqual(original.count(b'\t'), 3)
            self.assertEqual(schema.read_bytes(), original.replace(b'\t', b'      '))
            self.assertEqual(schema.read_bytes(), (ROOT/'evidence/gunyah-binding/indentation-repaired.yaml').read_bytes())
            with self.assertRaisesRegex(ValueError, 'input hash'):
                module.apply_gunyah_yaml_repair(Path(d), 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87')
