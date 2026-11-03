import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).parents[1] / "scripts" / "clean_comments.py"


class CleanCommentsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("clean_comments", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_preserves_strings_and_docstrings(self):
        source = 'value = "# text."\ntext = """A sentence.\n# - literal.\n"""\n'
        self.assertEqual(self.module.clean_comments(source), source)

    def test_cleans_comment_and_preserves_internal_period(self):
        self.assertEqual(self.module.clean_comments('# I tried X. I kept Y.\n'), '# I tried X. I kept Y\n')

    def test_converts_comment_bullets(self):
        self.assertEqual(self.module.clean_comments('    # - first.\n'), '    #\tfirst\n')

    def test_preserves_inline_code_and_ellipsis(self):
        self.assertEqual(self.module.clean_comments('x = "#" # I keep this...\n'), 'x = "#" # I keep this...\n')

    def test_preserves_crlf(self):
        self.assertEqual(self.module.clean_comments('# I keep this.\r\n'), '# I keep this\r\n')

    def test_rejects_incomplete_input(self):
        with self.assertRaises((SyntaxError, self.module.tokenize.TokenError)):
            self.module.clean_comments('x = (\n# I keep this.\n')


if __name__ == "__main__":
    unittest.main()
