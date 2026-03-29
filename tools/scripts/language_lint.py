#!/usr/bin/env python3
from __future__ import annotations

import ast
import io
import json
import re
import sys
import tokenize
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / "var" / "docs" / "language-lint-report.json"
NON_ASCII_RE = re.compile(r"[^\x00-\x7F]")
ESCAPE_HATCH = "NON_ENGLISH_OK"
ALLOWED_NON_ASCII_CHARS = {"—", "←", "→", "─", "│", "┌", "┐", "└", "┘", "├", "┤", "┬", "┴", "┼", "▼", "⚡"}
IGNORED_PATH_PARTS = {
    ".git",
    ".next",
    ".turbo",
    "agentic-template",
    "coverage",
    "dist",
    "docs copy",
    "node_modules",
    "scripts copy",
    "var",
}
JAVASCRIPT_LIKE_PATTERNS = ("*.js", "*.jsx", "*.mjs", "*.cjs", "*.ts", "*.tsx")
CSS_PATTERNS = ("*.css", "*.scss")
HASH_COMMENT_PATTERNS = ("*.sh", "*.toml", "*.yaml", "*.yml", "Dockerfile*")


def iter_markdown_files() -> List[Path]:
    files = [ROOT / "AGENTS.md", ROOT / "README.md"]
    files.extend(sorted((ROOT / "docs").rglob("*.md")))
    return [path for path in files if path.exists()]


def _is_ignored_path(path: Path) -> bool:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        rel = path
    return any(part in IGNORED_PATH_PARTS for part in rel.parts)


def _iter_repo_files(patterns: Sequence[str]) -> List[Path]:
    files = {
        path
        for pattern in patterns
        for path in ROOT.rglob(pattern)
        if not _is_ignored_path(path)
    }
    return sorted(files, key=lambda path: path.as_posix())


def iter_python_files() -> List[Path]:
    return _iter_repo_files(("*.py",))


def iter_javascript_like_files() -> List[Path]:
    return _iter_repo_files(JAVASCRIPT_LIKE_PATTERNS)


def iter_css_files() -> List[Path]:
    return _iter_repo_files(CSS_PATTERNS)


def iter_comment_files() -> List[Path]:
    files = [ROOT / "Makefile"]
    files.extend(_iter_repo_files(HASH_COMMENT_PATTERNS))
    deduped = {path for path in files if path.exists()}
    return sorted(deduped, key=lambda path: path.as_posix())


def lint_text_entries(path: Path, entries: Sequence[Tuple[int, str]], kind: str) -> List[str]:
    issues: List[str] = []
    allow_next_nonempty = False
    rel = path.relative_to(ROOT)

    for line_no, text in entries:
        stripped = text.strip()

        if ESCAPE_HATCH in text:
            allow_next_nonempty = True
            continue

        if stripped == "":
            continue

        if allow_next_nonempty:
            allow_next_nonempty = False
            continue

        non_ascii_chars = NON_ASCII_RE.findall(text)
        if non_ascii_chars and any(char not in ALLOWED_NON_ASCII_CHARS for char in non_ascii_chars):
            issues.append(
                f"{rel}:{line_no}: non-ASCII text found in repository {kind}; use English or add '{ESCAPE_HATCH}: <reason>'"
            )

    return issues


def lint_markdown_file(path: Path) -> List[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    entries = [(line_no, line) for line_no, line in enumerate(lines, start=1)]
    return lint_text_entries(path, entries, "documentation")


def _iter_python_comment_entries(source: str) -> Iterable[Tuple[int, str]]:
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.COMMENT:
            yield token.start[0], token.string


def _iter_python_docstring_entries(source: str) -> Iterable[Tuple[int, str]]:
    tree = ast.parse(source)
    lines = source.splitlines()
    nodes = [tree]
    nodes.extend(
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.AsyncFunctionDef, ast.ClassDef, ast.FunctionDef))
    )

    for node in nodes:
        body = getattr(node, "body", [])
        if not body:
            continue
        first = body[0]
        if not isinstance(first, ast.Expr):
            continue
        value = getattr(first, "value", None)
        if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
            continue
        start = first.lineno
        end = getattr(first, "end_lineno", start)
        for line_no in range(start, end + 1):
            yield line_no, lines[line_no - 1]


def lint_python_file(path: Path) -> List[str]:
    source = path.read_text(encoding="utf-8")
    entries = list(_iter_python_comment_entries(source))
    entries.extend(_iter_python_docstring_entries(source))
    entries.sort(key=lambda item: item[0])
    return lint_text_entries(path, entries, "comments/docstrings")


def _iter_c_like_comment_entries(source: str, *, allow_line_comments: bool) -> Iterable[Tuple[int, str]]:
    i = 0
    line_no = 1
    state = "code"
    comment_start_line = 1
    buffer: List[str] = []

    while i < len(source):
        ch = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ""

        if state == "code":
            if allow_line_comments and ch == "/" and nxt == "/":
                state = "line_comment"
                comment_start_line = line_no
                buffer = []
                i += 2
                continue
            if ch == "/" and nxt == "*":
                state = "block_comment"
                comment_start_line = line_no
                buffer = []
                i += 2
                continue
            if ch == "'":
                state = "single_quote"
            elif ch == '"':
                state = "double_quote"
            elif ch == "`":
                state = "template"
            elif ch == "\n":
                line_no += 1
            i += 1
            continue

        if state == "line_comment":
            if ch == "\n":
                yield comment_start_line, "".join(buffer)
                state = "code"
                line_no += 1
                i += 1
                continue
            buffer.append(ch)
            i += 1
            continue

        if state == "block_comment":
            if ch == "*" and nxt == "/":
                text = "".join(buffer)
                for offset, line in enumerate(text.splitlines()):
                    yield comment_start_line + offset, line
                state = "code"
                i += 2
                continue
            if ch == "\n":
                line_no += 1
            buffer.append(ch)
            i += 1
            continue

        if ch == "\\":
            if i + 1 < len(source) and source[i + 1] == "\n":
                line_no += 1
            i += 2
            continue

        if state == "single_quote":
            if ch == "'":
                state = "code"
            elif ch == "\n":
                line_no += 1
            i += 1
            continue

        if state == "double_quote":
            if ch == '"':
                state = "code"
            elif ch == "\n":
                line_no += 1
            i += 1
            continue

        if state == "template":
            if ch == "`":
                state = "code"
            elif ch == "\n":
                line_no += 1
            i += 1
            continue

    if state == "line_comment":
        yield comment_start_line, "".join(buffer)
    elif state == "block_comment":
        text = "".join(buffer)
        for offset, line in enumerate(text.splitlines()):
            yield comment_start_line + offset, line


def _iter_javascript_like_comment_entries(source: str) -> Iterable[Tuple[int, str]]:
    return _iter_c_like_comment_entries(source, allow_line_comments=True)


def _iter_css_comment_entries(source: str) -> Iterable[Tuple[int, str]]:
    return _iter_c_like_comment_entries(source, allow_line_comments=False)


def lint_javascript_like_file(path: Path) -> List[str]:
    source = path.read_text(encoding="utf-8")
    entries = list(_iter_javascript_like_comment_entries(source))
    return lint_text_entries(path, entries, "comments")


def lint_typescript_file(path: Path) -> List[str]:
    return lint_javascript_like_file(path)


def lint_css_file(path: Path) -> List[str]:
    source = path.read_text(encoding="utf-8")
    entries = list(_iter_css_comment_entries(source))
    return lint_text_entries(path, entries, "comments")


def lint_comment_file(path: Path) -> List[str]:
    entries: List[Tuple[int, str]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.lstrip().startswith("#"):
            entries.append((line_no, line))
    return lint_text_entries(path, entries, "comments")


def lint() -> List[str]:
    issues: List[str] = []

    for path in iter_markdown_files():
        issues.extend(lint_markdown_file(path))

    for path in iter_python_files():
        issues.extend(lint_python_file(path))

    for path in iter_javascript_like_files():
        issues.extend(lint_javascript_like_file(path))

    for path in iter_css_files():
        issues.extend(lint_css_file(path))

    for path in iter_comment_files():
        issues.extend(lint_comment_file(path))

    return issues


def _write_report(issues: List[str]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": len(issues) == 0,
        "issues": issues,
    }
    REPORT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> int:
    issues = lint()
    _write_report(issues)

    if issues:
        print("language-lint: FAIL")
        for issue in issues:
            print(f"- {issue}")
        print(f"language-lint: report -> {REPORT_PATH.relative_to(ROOT)}")
        return 1

    print("language-lint: OK")
    print(f"language-lint: report -> {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
