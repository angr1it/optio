#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / "var" / "docs" / "docs-lint-report.json"

REQUIRED_FILES = [
    ROOT / "AGENTS.md",
    ROOT / "README.md",
    ROOT / ".pre-commit-config.yaml",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "process" / "feature-driven-development.md",
    ROOT / "docs" / "roadmap" / "BACKLOG.md",
    ROOT / "docs" / "roadmap" / "ARCHIVE_BACKLOG.md",
    ROOT / "docs" / "roadmap" / "BACKLOG_TEMPLATE.md",
    ROOT / "docs" / "roadmap" / "iterations" / "ITERATION_TEMPLATE.md",
    ROOT / "docs" / "features" / "FEATURE_TEMPLATE.md",
    ROOT / "docs" / "testing" / "overview.md",
]

MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _normalize_target(raw: str) -> str:
    target = raw.strip()
    if "#" in target:
        target = target.split("#", 1)[0].strip()
    return target


def _is_external(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "#"))


def _resolve_path(src: Path, target: str) -> Path:
    if target.startswith("/"):
        return (ROOT / target.lstrip("/")).resolve()
    return (src.parent / target).resolve()


def _iter_markdown_files() -> List[Path]:
    files = sorted((ROOT / "docs").rglob("*.md"))
    files.append(ROOT / "AGENTS.md")
    files.append(ROOT / "README.md")

    seen = set()
    out: List[Path] = []
    for f in files:
        if f.exists() and f not in seen:
            seen.add(f)
            out.append(f)
    return out


def lint() -> List[str]:
    issues: List[str] = []

    for req in REQUIRED_FILES:
        if not req.exists():
            issues.append(f"missing required file: {req.relative_to(ROOT)}")

    for path in _iter_markdown_files():
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for raw_target in MD_LINK_RE.findall(line):
                target = _normalize_target(raw_target)
                if target == "" or _is_external(target):
                    continue
                resolved = _resolve_path(path, target)
                if not resolved.exists():
                    issues.append(
                        f"{rel}:{line_no}: broken markdown link -> {raw_target}"
                    )

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
        print("docs-lint: FAIL")
        for issue in issues:
            print(f"- {issue}")
        print(f"docs-lint: report -> {REPORT_PATH.relative_to(ROOT)}")
        return 1

    checked = len(_iter_markdown_files())
    print(f"docs-lint: OK ({checked} markdown files)")
    print(f"docs-lint: report -> {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
