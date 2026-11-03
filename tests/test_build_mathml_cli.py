import shutil
import subprocess
import sys
from pathlib import Path

import pytest


BUILD = Path(__file__).resolve().parents[1] / "skills" / "building-course-study-guides" / "scripts" / "build_mathml.py"


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="pandoc is required")
def test_build_mathml_accepts_ordered_fragments_without_editing_script(tmp_path):
    header = tmp_path / "00-header.html"
    unit = tmp_path / "01-unit.html"
    footer = tmp_path / "99-footer.html"
    output = tmp_path / "guide.html"
    header.write_text("<!doctype html><html><body>", encoding="utf-8")
    unit.write_text(r'<section id="unit"><p>\(x+1\)</p><div class="formula">\[\begin{aligned}x+1&=2\\x&=1\end{aligned}\]</div></section>', encoding="utf-8")
    footer.write_text("</body></html>", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(BUILD), "--output", str(output), str(header), str(unit), str(footer)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    built = output.read_text(encoding="utf-8")
    assert built.count("<math") == 2
    assert "<mtable" in built
    assert built.index('<section id="unit">') < built.index("</body>")


def test_build_mathml_rejects_uncompiled_math_without_writing_output(tmp_path):
    fragment = tmp_path / "fragment.html"
    output = tmp_path / "guide.html"
    fragment.write_text(r"<html><body><p>\frac{1}{2}</p></body></html>", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(BUILD), "--output", str(output), str(fragment)],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "uncompiled LaTeX" in result.stderr
    assert not output.exists()


def test_build_mathml_rejects_other_raw_latex_commands(tmp_path):
    fragment = tmp_path / "fragment.html"
    output = tmp_path / "guide.html"
    fragment.write_text(r"<html><body><p>\sqrt{x}</p></body></html>", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(BUILD), "--output", str(output), str(fragment)],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert not output.exists()


def test_build_mathml_preserves_latex_examples_inside_code(tmp_path):
    fragment = tmp_path / "fragment.html"
    output = tmp_path / "guide.html"
    fragment.write_text(r"<html><body><pre><code>\(x+1\) and \frac{1}{2}</code></pre></body></html>", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(BUILD), "--output", str(output), str(fragment)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    built = output.read_text(encoding="utf-8")
    assert r"\(x+1\) and \frac{1}{2}" in built
    assert "<math" not in built
