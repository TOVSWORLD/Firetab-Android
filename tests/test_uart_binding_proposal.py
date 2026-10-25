import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bindings', ROOT / 'scripts/validate_douglas_bindings.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class UARTProposal(unittest.TestCase):
    def source(self, directory):
        path = Path(directory) / 'serial/mediatek,uart.yaml'
        path.parent.mkdir()
        path.write_bytes((ROOT / 'evidence/console-storage/ack/Documentation/devicetree/bindings/serial/mediatek,uart.yaml').read_bytes())
        return path

    def test_apply_actual_locked_patch_in_isolated_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            self.source(directory)
            profile, schema = module.apply_uart_proposal(Path(directory), 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87')
            self.assertEqual(profile['schema'], 'serial/mediatek,uart.yaml')
            self.assertTrue(schema.is_file())

    def test_modified_original_schema_is_rejected_before_application(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.source(directory)
            path.write_text(path.read_text() + '\n# changed upstream input\n')
            with self.assertRaisesRegex(ValueError, 'input hash/revision mismatch'):
                module.apply_uart_proposal(Path(directory), 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87')
