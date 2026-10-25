"""Contributor interface integrity, using isolated fixture content."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_community import validate_form, validate_links


class CommunityTests(unittest.TestCase):
    def test_documentation_cannot_link_to_untracked_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            validate_links('[guide](docs/guide.md#setup)', root, root, {'docs/guide.md'})
            with self.assertRaisesRegex(ValueError, 'Untracked/missing'):
                validate_links('[guide](docs/missing.md)', root, root, {'docs/guide.md'})
            with self.assertRaisesRegex(ValueError, 'outside repository'):
                validate_links('[escape](../escape.md)', root, root, set())

    def test_unknown_form_label_is_rejected(self):
        form = dict(name='Bug',description='Report',labels=['type:nonexistent'],body=[])
        with self.assertRaisesRegex(ValueError, 'unknown labels'):
            validate_form(form, {'type:bug'})


if __name__ == '__main__':
    unittest.main()
