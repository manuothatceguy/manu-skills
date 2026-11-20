import importlib.util
from pathlib import Path
import tempfile
import unittest

SKILL_DIR = Path(__file__).parents[1]
SCRIPT = SKILL_DIR / "scripts" / "lint_skill.py"
FRONTMATTER = "---\nname: sample\ndescription: Use when reviewing a sample.\n---\n"


class LintSkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("lint_skill", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def rules_for(self, body, frontmatter=FRONTMATTER, extra_files=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_text(frontmatter + body, encoding="utf-8")
            for name, text in (extra_files or {}).items():
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                (root / name).write_text(text, encoding="utf-8")
            return [finding[2] for finding in self.module.lint_skill(root)]

    def test_clean_skill_has_no_findings(self):
        self.assertEqual(self.rules_for("Run the linter, then read each finding.\n"), [])

    def test_flags_persona_openers_in_english_and_spanish(self):
        self.assertIn("persona-opener", self.rules_for("You are an expert Python developer.\n"))
        self.assertIn("persona-opener", self.rules_for("Sos un experto en React.\n"))

    def test_flags_shouting_but_not_code_spans(self):
        self.assertIn("shouting", self.rules_for("You MUST run the tests.\n"))
        self.assertNotIn("shouting", self.rules_for("Set `ALWAYS` in the config.\n"))

    def test_flags_incantations(self):
        self.assertIn("incantation", self.rules_for("Think step by step before answering.\n"))

    def test_flags_hardcoded_locations(self):
        self.assertIn("hardcoded-location", self.rules_for("Read /home/someone/notes/todo.md first.\n"))
        self.assertIn("hardcoded-location", self.rules_for("The server runs on localhost:3000.\n"))
        self.assertNotIn("hardcoded-location", self.rules_for("Read references/notes.md first.\n"))

    def test_flags_session_narrative(self):
        self.assertIn("session-narrative", self.rules_for("As we discussed, the parser skips blanks.\n"))

    def test_flags_external_references_and_stale_pins(self):
        self.assertIn("external-reference", self.rules_for("See https://example.com/docs for details.\n"))
        self.assertIn("stale-pin", self.rules_for("As of March 2026 the API returns XML.\n"))

    def test_flags_trivialities_and_missing_finish_line(self):
        self.assertIn("triviality", self.rules_for("Follow best practices.\n"))
        self.assertIn("no-finish-line", self.rules_for("Iterate until you are satisfied.\n"))

    def test_flags_human_facing_sections(self):
        self.assertIn("human-facing-section", self.rules_for("## Installation\n"))

    def test_flags_description_problems(self):
        missing = "---\nname: sample\n---\n"
        workflow = "---\nname: sample\ndescription: First reads the diff, then runs tests, finally writes a report.\n---\n"
        self.assertIn("description", self.rules_for("Body.\n", frontmatter=missing))
        self.assertIn("workflow-in-description", self.rules_for("Body.\n", frontmatter=workflow))

    def test_flags_broken_and_nested_pointers(self):
        self.assertIn("broken-pointer", self.rules_for("See [the notes](references/missing.md).\n"))
        nested = {"references/a.md": "See [more](b.md).\n", "references/b.md": "Leaf.\n"}
        self.assertIn("deep-nesting", self.rules_for("See [a](references/a.md).\n", extra_files=nested))

    def test_ignores_pointers_inside_code_fences(self):
        self.assertEqual(self.rules_for("```markdown\n[x](./<name>.md)\n```\n"), [])

    def test_flags_sprawl(self):
        self.assertIn("sprawl", self.rules_for("word " * (self.module.MAX_BODY_WORDS + 1) + "\n"))

    def test_muted_region_is_skipped(self):
        body = "<!-- skill-lint: off -->\nYou are an expert.\n<!-- skill-lint: on -->\nFollow best practices.\n"
        self.assertEqual(self.rules_for(body), ["triviality"])

    def test_own_skill_is_clean(self):
        self.assertEqual(self.module.lint_skill(SKILL_DIR), [])


if __name__ == "__main__":
    unittest.main()
