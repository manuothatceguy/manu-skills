import sys
import tempfile
import unittest
from pathlib import Path

scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

import validate_deck


class TestValidateDeck(unittest.TestCase):
    def test_check_cloze_syntax_valid(self):
        text = "This is a {{c1::valid cloze}} with {{c2::another}}."
        errors = validate_deck.check_cloze_syntax(text)
        self.assertEqual(len(errors), 0)

    def test_check_cloze_syntax_unbalanced(self):
        text = "This is {{c1::broken cloze"
        errors = validate_deck.check_cloze_syntax(text)
        self.assertTrue(any("Unbalanced" in e for e in errors))

    def test_check_cloze_syntax_malformed(self):
        text = "This is {{broken}} cloze"
        errors = validate_deck.check_cloze_syntax(text)
        self.assertTrue(any("Malformed" in e for e in errors))

    def test_check_cloze_syntax_accepts_multiple_card_indices(self):
        errors = validate_deck.check_cloze_syntax("A {{c1,2,3::shared answer}} appears on three cards")
        self.assertEqual(errors, [])

    def test_check_cloze_syntax_rejects_zero_in_multiple_card_indices(self):
        errors = validate_deck.check_cloze_syntax("A {{c1,0::invalid answer}} has a zero index")
        self.assertTrue(any("Malformed" in error for error in errors))

    def test_check_cloze_syntax_rejects_zero_index(self):
        errors = validate_deck.check_cloze_syntax("This is {{c0::invalid}} cloze")
        self.assertTrue(any("Malformed" in e for e in errors))

    def test_check_cloze_syntax_rejects_empty_content(self):
        for cloze in ("{{c1::}}", "{{c1::   }}"):
            with self.subTest(cloze=cloze):
                errors = validate_deck.check_cloze_syntax(cloze)
                self.assertTrue(any("Malformed" in e for e in errors))

    def test_check_html_tags(self):
        valid = "<strong>Clean</strong> <code>code</code><br>"
        self.assertEqual(len(validate_deck.check_html_tags(valid)), 0)

        unclosed = "<strong>Unclosed"
        errors = validate_deck.check_html_tags(unclosed)
        self.assertTrue(any("Unclosed" in e for e in errors))

    def test_html_void_tags_do_not_need_closing_tags(self):
        html = '<strong>term</strong><wbr><img src="diagram.png"><br>'
        self.assertEqual(validate_deck.check_html_tags(html), [])

    def test_validate_deck_file(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".tsv") as tf:
            tf.write("Front 1\tBack 1\ttag1\n")
            tf.write("Front 2 {{c1::cloze}}\tBack 2\ttag2\n")
            temp_path = Path(tf.name)

        try:
            errors, warnings = validate_deck.validate_deck(temp_path)
            self.assertEqual(errors, 0)
            self.assertEqual(warnings, 0)
        finally:
            temp_path.unlink()

    def test_validate_deck_accepts_quoted_newline_in_field(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".tsv") as tf:
            tf.write('"Front\ncontinued"\tBack\ttag1\n')
            temp_path = Path(tf.name)

        try:
            errors, warnings = validate_deck.validate_deck(temp_path)
            self.assertEqual(errors, 0)
            self.assertEqual(warnings, 0)
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    unittest.main()
