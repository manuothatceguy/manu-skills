import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_repo", ROOT / "scripts" / "validate_repo.py")
validate_repo = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_repo)


def test_skill_frontmatter_requires_name_and_description(tmp_path):
    skill = tmp_path / "sample" / "SKILL.md"
    skill.parent.mkdir()
    skill.write_text("---\nname: sample\n---\nBody\n", encoding="utf-8")

    errors = validate_repo.validate_skill(skill)

    assert any("description" in error for error in errors)


def test_skill_local_reference_must_exist(tmp_path):
    skill = tmp_path / "sample" / "SKILL.md"
    skill.parent.mkdir()
    skill.write_text("---\nname: sample\ndescription: A skill\n---\n[missing](guide.md)\n", encoding="utf-8")

    errors = validate_repo.validate_skill(skill)

    assert any("guide.md" in error for error in errors)


def test_skill_frontmatter_and_existing_reference_pass(tmp_path):
    skill = tmp_path / "sample" / "SKILL.md"
    skill.parent.mkdir()
    (skill.parent / "guide.md").write_text("guide", encoding="utf-8")
    skill.write_text("---\nname: sample\ndescription: A skill\n---\n[guide](guide.md)\n", encoding="utf-8")

    assert validate_repo.validate_skill(skill) == []


def test_skill_links_inside_code_fences_are_examples(tmp_path):
    skill = tmp_path / "sample" / "SKILL.md"
    skill.parent.mkdir()
    skill.write_text("---\nname: sample\ndescription: A skill\n---\n```markdown\n[example](../other/file.md)\n```\n", encoding="utf-8")

    assert validate_repo.validate_skill(skill) == []


def test_html_validation_delegates_to_build_validator(tmp_path):
    html = tmp_path / "guide.html"
    html.write_text("<html><body><p>\\frac{1}{2}</p></body></html>", encoding="utf-8")

    errors = validate_repo.validate_html(html)

    assert errors
    assert any("LaTeX" in error or "comando" in error for error in errors)


def test_html_without_raw_latex_passes(tmp_path):
    html = tmp_path / "guide.html"
    html.write_text("<html><body><p><math><mi>x</mi></math></p></body></html>", encoding="utf-8")

    assert validate_repo.validate_html(html) == []


def test_tsv_validation_rejects_wrong_column_count(tmp_path):
    deck = tmp_path / "deck.tsv"
    deck.write_text("front\tback\n", encoding="utf-8")

    errors = validate_repo.validate_tsv(deck)

    assert errors


def test_tsv_validation_accepts_three_columns(tmp_path):
    deck = tmp_path / "deck.tsv"
    deck.write_text("front\tback\ttag\n", encoding="utf-8")

    assert validate_repo.validate_tsv(deck) == []


def test_tsv_validation_rejects_malformed_cloze(tmp_path):
    deck = tmp_path / "deck.tsv"
    deck.write_text("What? {{bad}}\tAnswer\ttag\n", encoding="utf-8")

    errors = validate_repo.validate_tsv(deck)

    assert errors


def test_tsv_validation_rejects_unbalanced_html(tmp_path):
    deck = tmp_path / "deck.tsv"
    deck.write_text("Question\t<strong>Answer\ttag\n", encoding="utf-8")

    errors = validate_repo.validate_tsv(deck)

    assert errors


def test_html_validation_requires_a_complete_document(tmp_path):
    html = tmp_path / "fragment.html"
    html.write_text("<p>Fragment</p>", encoding="utf-8")

    errors = validate_repo.validate_html(html)

    assert any("complete HTML document" in error for error in errors)


def test_staged_validation_uses_index_content_when_worktree_is_valid(tmp_path, monkeypatch, capsys):
    path = ROOT / "skills" / "building-course-study-guides" / "artifacts" / "staged-guide.html"
    path.parent.mkdir(exist_ok=True)
    path.write_text("<html><body><p>Compiled formula</p></body></html>", encoding="utf-8")
    staged = b"<html><body><p>\\frac{1}{2}</p></body></html>"
    _mock_git_index(monkeypatch, path, staged)

    result = validate_repo.main(["--staged"])

    assert result == 1
    assert "comando LaTeX" in capsys.readouterr().err
    path.unlink()


def test_staged_validation_uses_index_content_when_worktree_is_invalid(tmp_path, monkeypatch, capsys):
    path = ROOT / "skills" / "building-course-study-guides" / "artifacts" / "staged-guide.html"
    path.parent.mkdir(exist_ok=True)
    path.write_text("<html><body><p>\\frac{1}{2}</p></body></html>", encoding="utf-8")
    staged = b"<html><body><p>Compiled formula</p></body></html>"
    _mock_git_index(monkeypatch, path, staged)

    result = validate_repo.main(["--staged"])

    assert result == 0
    assert "Validated 1" in capsys.readouterr().out
    path.unlink()


def _mock_git_index(monkeypatch, path, staged_content):
    from types import SimpleNamespace
    import subprocess

    real_run = subprocess.run
    relative_path = path.relative_to(ROOT).as_posix().encode()

    def run(args, *positional, **kwargs):
        if args[0] == "git" and "diff" in args:
            return SimpleNamespace(returncode=0, stdout=relative_path + b"\0", stderr=b"")
        if args[0] == "git" and "show" in args:
            return SimpleNamespace(returncode=0, stdout=staged_content, stderr=b"")
        return real_run(args, *positional, **kwargs)

    monkeypatch.setattr(validate_repo.subprocess, "run", run)


def test_staged_validation_skips_html_outside_artifact_directories(monkeypatch):
    from types import SimpleNamespace

    def run(args, **kwargs):
        assert "--diff-filter=ACMRT" in args
        return SimpleNamespace(returncode=0, stdout=b"docs/example.html\0", stderr=b"")

    monkeypatch.setattr(validate_repo.subprocess, "run", run)

    assert validate_repo.staged_targets() == []


def test_staged_skill_reference_must_exist_in_index_even_when_worktree_has_it(tmp_path, monkeypatch):
    path = ROOT / "skills" / "staged-reference-sample" / "SKILL.md"
    path.parent.mkdir()
    reference = path.parent / "guide.md"
    reference.write_text("present only in worktree", encoding="utf-8")
    text = "---\nname: sample\ndescription: A skill\n---\n[guide](guide.md)\n"

    def run(args, **kwargs):
        assert args[1:3] == ["-C", str(ROOT)]
        return type("Result", (), {"returncode": 1, "stderr": b"missing from index"})()

    monkeypatch.setattr(validate_repo.subprocess, "run", run)
    try:
        errors = validate_repo.validate_skill(path, text, staged=True)
    finally:
        reference.unlink()
        path.parent.rmdir()

    assert any("guide.md" in error and "index" in error for error in errors)


def test_staged_invalid_utf8_returns_a_clear_error(monkeypatch, capsys):
    path = ROOT / "skills" / "staged-invalid-encoding" / "SKILL.md"
    _mock_git_index(monkeypatch, path, b"\xff")

    result = validate_repo.main(["--staged"])

    assert result == 1
    assert "not valid UTF-8" in capsys.readouterr().err
