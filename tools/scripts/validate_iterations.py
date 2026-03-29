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
ITERATIONS_DIR = ROOT / "docs" / "roadmap" / "iterations"
REPORT_PATH = ROOT / "var" / "docs" / "iterations-lint-report.json"

ITERATION_STATUS_RE = re.compile(r"^\*\*Status:\*\*\s*(.+?)\s*$", re.MULTILINE)
BACKLOG_ID_RE = re.compile(r"\bBLG-\d{3}\b")
SECTION_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
CHECKBOX_RE = re.compile(r"^\s*-\s+\[( |x)\]\s+.+$")
OPEN_CHECKBOX_RE = re.compile(r"^\s*-\s+\[ \]\s+.+$")
ORDERED_STEP_RE = re.compile(r"^\s*\d+\.\s+.+$")
PLAIN_BULLET_RE = re.compile(r"^\s*-\s+.+$")
FOLLOW_UP_REQUIRED_RE = re.compile(r"^\s*-\s+\[x\]\s+(Deferred:|Carried over:).+$")

REQUIRED_ITERATION_FILES = ["iteration.md", "execution-plan.md", "status-report.md"]
REQUIRED_ITERATION_SECTIONS = [
    "## Scope",
    "## Definition Of Done (DoD)",
    "## Carry-over",
    "## Closure",
]


def iter_iteration_dirs() -> List[Path]:
    if not ITERATIONS_DIR.exists():
        return []
    dirs = []
    for path in sorted(ITERATIONS_DIR.iterdir()):
        if not path.is_dir():
            continue
        if path.name.startswith("ITR-"):
            dirs.append(path)
    return dirs


def _extract_status(text: str) -> str:
    match = ITERATION_STATUS_RE.search(text)
    if match is None:
        return ""
    return match.group(1).strip()


def _extract_section_lines(text: str, heading: str) -> List[tuple[int, str]]:
    lines = text.splitlines()
    collected: List[tuple[int, str]] = []
    in_section = False

    for idx, line in enumerate(lines, start=1):
        heading_match = SECTION_HEADING_RE.match(line.strip())
        if heading_match is not None:
            if line.strip() == heading:
                in_section = True
                continue
            if in_section:
                break
        if in_section:
            collected.append((idx, line))

    return collected


def lint_execution_plan(
    path: Path,
    iteration_status: str,
) -> List[str]:
    issues: List[str] = []
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT)

    step_lines = _extract_section_lines(text, "## Steps")
    checklist_count = 0

    for line_no, line in step_lines:
        stripped = line.strip()
        if stripped == "":
            continue
        if CHECKBOX_RE.match(line):
            checklist_count += 1
            if FOLLOW_UP_REQUIRED_RE.match(line) and BACKLOG_ID_RE.search(line) is None:
                issues.append(
                    f"{rel}:{line_no}: checked 'Deferred:' or 'Carried over:' items must reference a follow-up backlog id BLG-###"
                )
            continue
        if ORDERED_STEP_RE.match(line) or PLAIN_BULLET_RE.match(line):
            issues.append(
                f"{rel}:{line_no}: actionable items in '## Steps' must use Markdown checkboxes"
            )

    if checklist_count == 0:
        issues.append(f"{rel}: missing checkbox steps under '## Steps'")

    if iteration_status.lower() in {"closed", "closed with follow-ups"}:
        for line_no, line in enumerate(text.splitlines(), start=1):
            if OPEN_CHECKBOX_RE.match(line):
                issues.append(
                    f"{rel}:{line_no}: closed iterations cannot leave open checklist items in execution-plan.md"
                )

    return issues


def lint_iteration_dir(path: Path, known_backlog_ids: Set[str] | None = None) -> List[str]:
    issues: List[str] = []
    rel = path.relative_to(ROOT)

    for file_name in REQUIRED_ITERATION_FILES:
        file_path = path / file_name
        if not file_path.exists():
            issues.append(f"{rel}: missing required file '{file_name}'")

    iteration_md = path / "iteration.md"
    iteration_status = ""
    if iteration_md.exists():
        text = iteration_md.read_text(encoding="utf-8")

        if ITERATION_STATUS_RE.search(text) is None:
            issues.append(f"{iteration_md.relative_to(ROOT)}: missing '**Status:**' line")
        else:
            iteration_status = _extract_status(text)

        for section in REQUIRED_ITERATION_SECTIONS:
            if section not in text:
                issues.append(
                    f"{iteration_md.relative_to(ROOT)}: missing required section '{section}'"
                )

        backlog_ids = sorted(set(BACKLOG_ID_RE.findall(text)))
        if len(backlog_ids) == 0:
            issues.append(
                f"{iteration_md.relative_to(ROOT)}: must reference at least one backlog id BLG-###"
            )
        elif known_backlog_ids is not None:
            for item_id in backlog_ids:
                if item_id not in known_backlog_ids:
                    issues.append(
                        f"{iteration_md.relative_to(ROOT)}: referenced backlog id '{item_id}' does not exist in docs/roadmap/BACKLOG.md or docs/roadmap/ARCHIVE_BACKLOG.md"
                    )

    execution_plan = path / "execution-plan.md"
    if execution_plan.exists():
        issues.extend(lint_execution_plan(execution_plan, iteration_status))

    return issues


def lint() -> List[str]:
    issues: List[str] = []
    known_backlog_ids, backlog_issues = validate_backlog.collect_known_backlog_ids()
    issues.extend(backlog_issues)

    if not ITERATIONS_DIR.exists():
        return [f"missing iterations directory: {ITERATIONS_DIR.relative_to(ROOT)}"]

    template_path = ITERATIONS_DIR / "ITERATION_TEMPLATE.md"
    if not template_path.exists():
        issues.append(f"missing iteration template: {template_path.relative_to(ROOT)}")

    dirs = iter_iteration_dirs()
    if len(dirs) == 0:
        issues.append("docs/roadmap/iterations: no iteration directories found (ITR-*)")

    for iteration_dir in dirs:
        issues.extend(lint_iteration_dir(iteration_dir, known_backlog_ids=known_backlog_ids))

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
        print("iterations-lint: FAIL")
        for issue in issues:
            print(f"- {issue}")
        print(f"iterations-lint: report -> {REPORT_PATH.relative_to(ROOT)}")
        return 1

    print("iterations-lint: OK")
    print(f"iterations-lint: report -> {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
