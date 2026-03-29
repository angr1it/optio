#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Set

import validate_backlog

ROOT = Path(__file__).resolve().parents[2]
FEATURES_DIR = ROOT / "docs" / "features"
REPORT_PATH = ROOT / "var" / "docs" / "features-lint-report.json"

BACKLOG_RE = re.compile(r"^Backlog:\s*(BLG-\d{3}(?:\s*,\s*BLG-\d{3})*)\s*$", re.MULTILINE)
STATUS_RE = re.compile(r"^Status:\s*.+$", re.MULTILINE)
OWNER_RE = re.compile(r"^Owner:\s*.+$", re.MULTILINE)

REQUIRED_SECTIONS = [
    "## Goal",
    "## Scope",
    "## Acceptance Criteria",
    "## Test Plan",
    "## Links",
]

SKIP_FILES = {"README.md", "FEATURE_TEMPLATE.md"}


def iter_feature_files() -> List[Path]:
    if not FEATURES_DIR.exists():
        return []
    files = []
    for path in sorted(FEATURES_DIR.glob("*.md")):
        if path.name in SKIP_FILES:
            continue
        files.append(path)
    return files


def _extract_backlog_ids(text: str) -> List[str]:
    match = BACKLOG_RE.search(text)
    if match is None:
        return []
    return re.findall(r"\bBLG-\d{3}\b", match.group(1))


def lint_feature(path: Path, known_backlog_ids: Set[str] | None = None) -> List[str]:
    issues: List[str] = []
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")

    if STATUS_RE.search(text) is None:
        issues.append(f"{rel}: missing 'Status:' line")

    if OWNER_RE.search(text) is None:
        issues.append(f"{rel}: missing 'Owner:' line")

    if BACKLOG_RE.search(text) is None:
        issues.append(f"{rel}: missing valid 'Backlog: BLG-###' line")
    else:
        referenced_ids = _extract_backlog_ids(text)
        if known_backlog_ids is not None:
            for item_id in referenced_ids:
                if item_id not in known_backlog_ids:
                    issues.append(
                        f"{rel}: referenced backlog id '{item_id}' does not exist in docs/roadmap/BACKLOG.md or docs/roadmap/ARCHIVE_BACKLOG.md"
                    )

    for section in REQUIRED_SECTIONS:
        if section not in text:
            issues.append(f"{rel}: missing required section '{section}'")

    if "docs/roadmap/iterations/" not in text:
        issues.append(f"{rel}: missing iteration link under docs/roadmap/iterations/")

    return issues


def lint() -> List[str]:
    issues: List[str] = []
    known_backlog_ids, backlog_issues = validate_backlog.collect_known_backlog_ids()
    issues.extend(backlog_issues)

    if not FEATURES_DIR.exists():
        return [f"missing features directory: {FEATURES_DIR.relative_to(ROOT)}"]

    feature_files = iter_feature_files()
    if len(feature_files) == 0:
        issues.append("docs/features: no feature specs found (excluding README/template)")

    for path in feature_files:
        issues.extend(lint_feature(path, known_backlog_ids=known_backlog_ids))

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
        print("features-lint: FAIL")
        for issue in issues:
            print(f"- {issue}")
        print(f"features-lint: report -> {REPORT_PATH.relative_to(ROOT)}")
        return 1

    print("features-lint: OK")
    print(f"features-lint: report -> {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
