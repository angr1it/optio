#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECS_DIR = ROOT / "docs" / "specs"
REPORT_PATH = ROOT / "var" / "docs" / "specs-lint-report.json"

ALLOWED_STATUSES = {"Draft", "Accepted", "Implemented", "Superseded"}
ALLOWED_STAGES = {
    "Local pre-deploy",
    "Cluster rollout",
    "Post-deploy follow-up",
    "Cross-cutting change",
}
ALLOWED_PRIORITIES = {"P0", "P1", "P2", "P3"}
REQUIRED_SECTIONS = [
    "Goal",
    "Why Now",
    "Scope",
    "Sequencing",
    "Plan",
    "Validation",
    "Rollout",
    "Links",
]
SKIP_FILES = {"README.md", "SPEC_TEMPLATE.md"}
ISSUE_REF_RE = re.compile(r"^(?:#\d+|N/A(?:\s*\(.+\))?)$")
PR_REF_RE = re.compile(r"^(?:#\d+|https?://\S+/pull/\d+|pending|N/A(?:\s*\(.+\))?)$")
CHECKBOX_RE = re.compile(r"^- \[(?P<state>[ xX])\] (?P<text>.+)$", re.MULTILINE)
DEFERRED_RE = re.compile(r"\b(?:Deferred to|Carry over to)\b", re.IGNORECASE)
GITHUB_ISSUE_RE = re.compile(r"#\d+")
HEADING_RE = re.compile(r"^## (?P<title>.+)$", re.MULTILINE)
HEADER_TEMPLATE = r"^{label}:\s*(?P<value>.+?)\s*$"
LINK_TEMPLATE = r"^\s*-\s*{label}:\s*(?P<value>.+?)\s*$"
SPEC_DOC_REF_RE = re.compile(r"docs/specs/[A-Za-z0-9._/-]+\.md")


def iter_spec_files() -> list[Path]:
    if not SPECS_DIR.exists():
        return []

    files: list[Path] = []
    for path in sorted(SPECS_DIR.glob("*.md")):
        if path.name in SKIP_FILES:
            continue
        files.append(path)
    return files


def _extract_header_value(text: str, label: str) -> str | None:
    pattern = re.compile(HEADER_TEMPLATE.format(label=re.escape(label)), re.MULTILINE)
    match = pattern.search(text)
    if match is None:
        return None
    return match.group("value").strip()


def _extract_section_body(text: str, title: str) -> str | None:
    match = re.search(
        rf"^## {re.escape(title)}\n(?P<body>.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        return None
    return match.group("body").strip()


def _extract_link_value(section_body: str, label: str) -> str | None:
    pattern = re.compile(LINK_TEMPLATE.format(label=re.escape(label)), re.MULTILINE)
    match = pattern.search(section_body)
    if match is None:
        return None
    return match.group("value").strip()


def _extract_labeled_list(section_body: str, label: str) -> list[str]:
    prefix = f"- {label}:"
    items: list[str] = []
    active = False

    for raw_line in section_body.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith(prefix):
            active = True
            tail = stripped[len(prefix) :].strip()
            if tail:
                items.append(tail)
            continue

        if not active:
            continue

        if stripped == "":
            continue

        if raw_line.startswith("  - "):
            items.append(raw_line[4:].strip())
            continue

        if stripped.startswith("- "):
            active = False
            continue

        if raw_line.startswith("  "):
            items.append(stripped)
            continue

        active = False

    return items


def lint_spec(path: Path) -> list[str]:
    issues: list[str] = []
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")

    status = _extract_header_value(text, "Status")
    owner = _extract_header_value(text, "Owner")
    issue_ref = _extract_header_value(text, "Issue")
    stage = _extract_header_value(text, "Stage")
    priority = _extract_header_value(text, "Priority")

    if status is None:
        issues.append(f"{rel}: missing 'Status:' line")
    elif status not in ALLOWED_STATUSES:
        allowed = " | ".join(sorted(ALLOWED_STATUSES))
        issues.append(f"{rel}: invalid Status '{status}' (expected: {allowed})")

    if owner is None or owner == "":
        issues.append(f"{rel}: missing 'Owner:' line")

    if issue_ref is None:
        issues.append(f"{rel}: missing 'Issue:' line")
    elif ISSUE_REF_RE.match(issue_ref) is None:
        issues.append(f"{rel}: invalid Issue '{issue_ref}' (expected: #123 or N/A (...))")

    if stage is None:
        issues.append(f"{rel}: missing 'Stage:' line")
    elif stage not in ALLOWED_STAGES:
        allowed = " | ".join(sorted(ALLOWED_STAGES))
        issues.append(f"{rel}: invalid Stage '{stage}' (expected: {allowed})")

    if priority is None:
        issues.append(f"{rel}: missing 'Priority:' line")
    elif priority not in ALLOWED_PRIORITIES:
        allowed = " | ".join(sorted(ALLOWED_PRIORITIES))
        issues.append(f"{rel}: invalid Priority '{priority}' (expected: {allowed})")

    sections: dict[str, str] = {}
    for section in REQUIRED_SECTIONS:
        body = _extract_section_body(text, section)
        if body is None:
            issues.append(f"{rel}: missing required section '## {section}'")
            continue
        sections[section] = body

    plan = sections.get("Plan")
    if plan is not None:
        checklist_items = list(CHECKBOX_RE.finditer(plan))
        if not checklist_items:
            issues.append(f"{rel}: '## Plan' must contain markdown checklist items")
        elif status == "Implemented":
            open_items = [
                item.group("text").strip()
                for item in checklist_items
                if item.group("state") == " "
            ]
            if open_items:
                issues.append(
                    f"{rel}: Status 'Implemented' requires all '## Plan' checklist items to be completed"
                )

        for line in plan.splitlines():
            stripped = line.strip()
            if stripped == "":
                continue
            if DEFERRED_RE.search(stripped) and GITHUB_ISSUE_RE.search(stripped) is None:
                issues.append(
                    f"{rel}: deferred/carry-over item must reference a GitHub issue (example: '#123')"
                )

    sequencing = sections.get("Sequencing")
    if sequencing is not None:
        for label in ("Blocked by", "Blocks", "Parallelizable with"):
            items = _extract_labeled_list(sequencing, label)
            if not items:
                issues.append(f"{rel}: '## Sequencing' must include non-empty '- {label}:' items")
                continue

            for item in items:
                if item.lower() == "none":
                    continue
                for ref in SPEC_DOC_REF_RE.findall(item):
                    if not (ROOT / ref).exists():
                        issues.append(
                            f"{rel}: sequencing reference points to a missing spec doc: {ref}"
                        )

    links = sections.get("Links")
    if links is not None:
        linked_issue = _extract_link_value(links, "Issue")
        linked_pr = _extract_link_value(links, "PR")
        related_docs = _extract_link_value(links, "Related docs")

        if linked_issue is None:
            issues.append(f"{rel}: '## Links' must include '- Issue:'")
        elif issue_ref is not None and linked_issue != issue_ref:
            issues.append(f"{rel}: '## Links' issue must match the header Issue value exactly")

        if linked_pr is None:
            issues.append(f"{rel}: '## Links' must include '- PR:'")
        elif PR_REF_RE.match(linked_pr) is None:
            issues.append(
                f"{rel}: invalid PR link '{linked_pr}' (expected: #123, full PR URL, pending, or N/A (...))"
            )

        if related_docs is None or related_docs == "":
            issues.append(f"{rel}: '## Links' must include non-empty '- Related docs:'")

    required_headings = {f"## {section}" for section in REQUIRED_SECTIONS}
    for heading in HEADING_RE.finditer(text):
        title = heading.group("title").strip()
        if f"## {title}" not in required_headings and title.startswith("Local Plan"):
            issues.append(f"{rel}: use the canonical heading '## Plan'")

    return issues


def lint() -> list[str]:
    if not SPECS_DIR.exists():
        return [f"missing specs directory: {SPECS_DIR.relative_to(ROOT)}"]

    issues: list[str] = []
    for path in iter_spec_files():
        issues.extend(lint_spec(path))
    return issues


def _write_report(issues: list[str]) -> None:
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
        print("specs-lint: FAIL")
        for issue in issues:
            print(f"- {issue}")
        print(f"specs-lint: report -> {REPORT_PATH.relative_to(ROOT)}")
        return 1

    print("specs-lint: OK")
    print(f"specs-lint: report -> {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
