import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_pr_issue import references, validate


class IssueTraceability(unittest.TestCase):
    def test_explicit_refs(self):
        self.assertEqual(references('Updates #106\nCloses #24\nRefs #106'), [24, 106])
        self.assertEqual(validate('Closes #24', lambda n: {'number': n}), [24])

    def test_missing_examples_and_pr_rejected(self):
        for text in ('See #24', '<!-- Closes #24 -->', '```\nRefs #24\n```', 'Closes #...'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                validate(text, lambda n: {'number': n})
        with self.assertRaises(ValueError):
            validate('Refs #12', lambda n: {'number': n, 'pull_request': {}})

    def test_missing_issue_fails(self):
        def unavailable(number):
            raise OSError('Issue unavailable')
        with self.assertRaises(OSError):
            validate('Updates #24', unavailable)
