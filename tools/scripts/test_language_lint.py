from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import language_lint


class LanguageLintTests(unittest.TestCase):
    def test_markdown_file_with_ascii_only_passes(self) -> None:
        with tempfile.TemporaryDirectory(dir=language_lint.ROOT / "var") as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text("# English only\n\nAll repository docs stay in English.\n", encoding="utf-8")

            issues = language_lint.lint_markdown_file(path)
            self.assertEqual([], issues)

    def test_markdown_file_with_non_ascii_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir=language_lint.ROOT / "var") as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text("# Заголовок\n", encoding="utf-8")

            issues = language_lint.lint_markdown_file(path)
            self.assertTrue(any("non-ASCII text found" in issue for issue in issues))

    def test_markdown_file_with_allowed_diagram_symbols_passes(self) -> None:
        with tempfile.TemporaryDirectory(dir=language_lint.ROOT / "var") as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text("Pipeline — plan → build → ship\n┌────┐\n│ OK │\n└────┘\n", encoding="utf-8")

            issues = language_lint.lint_markdown_file(path)
            self.assertEqual([], issues)

    def test_escape_hatch_allows_next_nonempty_line(self) -> None:
        with tempfile.TemporaryDirectory(dir=language_lint.ROOT / "var") as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text(
                "NON_ENGLISH_OK: preserve the external example text.\nПример внешнего текста.\n",
                encoding="utf-8",
            )

            issues = language_lint.lint_markdown_file(path)
            self.assertEqual([], issues)

    def test_python_comment_with_non_ascii_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir=language_lint.ROOT / "var") as tmp:
            path = Path(tmp) / "sample.py"
            path.write_text("# Комментарий\nvalue = 1\n", encoding="utf-8")

            issues = language_lint.lint_python_file(path)
            self.assertTrue(any("comments/docstrings" in issue for issue in issues))

    def test_typescript_comment_with_non_ascii_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir=language_lint.ROOT / "var") as tmp:
            path = Path(tmp) / "sample.ts"
            path.write_text("// Комментарий\nconst value = 1;\n", encoding="utf-8")

            issues = language_lint.lint_typescript_file(path)
            self.assertTrue(any("repository comments" in issue for issue in issues))

    def test_typescript_block_comment_with_non_ascii_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir=language_lint.ROOT / "var") as tmp:
            path = Path(tmp) / "sample.tsx"
            path.write_text("/*\n * Комментарий\n */\nexport const View = () => null;\n", encoding="utf-8")

            issues = language_lint.lint_typescript_file(path)
            self.assertTrue(any("repository comments" in issue for issue in issues))

    def test_typescript_comment_like_string_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory(dir=language_lint.ROOT / "var") as tmp:
            path = Path(tmp) / "sample.ts"
            path.write_text('const value = "// Комментарий";\nconst block = "/* Комментарий */";\n', encoding="utf-8")

            issues = language_lint.lint_typescript_file(path)
            self.assertEqual([], issues)

    def test_javascript_comment_with_non_ascii_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir=language_lint.ROOT / "var") as tmp:
            path = Path(tmp) / "sample.mjs"
            path.write_text("// Комментарий\nexport const value = 1;\n", encoding="utf-8")

            issues = language_lint.lint_javascript_like_file(path)
            self.assertTrue(any("repository comments" in issue for issue in issues))

    def test_css_block_comment_with_non_ascii_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir=language_lint.ROOT / "var") as tmp:
            path = Path(tmp) / "sample.css"
            path.write_text("/* Комментарий */\nbody { color: black; }\n", encoding="utf-8")

            issues = language_lint.lint_css_file(path)
            self.assertTrue(any("repository comments" in issue for issue in issues))

    def test_shell_comment_with_non_ascii_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir=language_lint.ROOT / "var") as tmp:
            path = Path(tmp) / "sample.sh"
            path.write_text("# Комментарий\nprintf 'ok\\n'\n", encoding="utf-8")

            issues = language_lint.lint_comment_file(path)
            self.assertTrue(any("repository comments" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
