#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parents[2]
ACTIVE_BACKLOG = ROOT / "docs" / "roadmap" / "BACKLOG.md"
ARCHIVE_BACKLOG = ROOT / "docs" / "roadmap" / "ARCHIVE_BACKLOG.md"
REPORT_PATH = ROOT / "var" / "docs" / "backlog-lint-report.json"

ENTRY_RE = re.compile(r"^##\s+(BLG-\d{3}):\s+.+$")
STATE_RE = re.compile(r"^\*\*State:\*\*\s*(.+?)\s*$")
PRIORITY_RE = re.compile(r"^\*\*Priority:\*\*\s*(.+?)\s*$")
TARGET_RE = re.compile(r"^\*\*Target iteration:\*\*\s*(.+?)\s*$")
OWNER_RE = re.compile(r"^\*\*Owner:\*\*\s*(.+?)\s*$")

VALID_STATES = {"proposed", "ready", "in progress", "blocked", "deferred", "done"}
VALID_PRIORITIES = {"high", "medium", "low"}
TARGET_ALLOWED_RE = re.compile(r"^(?:`?TBD`?|`?ITR-[A-Za-z0-9-]+`?)$")


@dataclass(frozen=True)
class BacklogEntry:
    item_id: str
    state: str
    priority: str
    target_iteration: str
    owner: str
    source: Path
    line: int


def _normalize_value(raw: str) -> str:
    return raw.strip().strip("`").strip()


def parse_entries(path: Path) -> Tuple[List[BacklogEntry], List[str]]:
    if not path.exists():
        return [], [f"missing backlog file: {path.relative_to(ROOT)}"]

    lines = path.read_text(encoding="utf-8").splitlines()
    entries: List[BacklogEntry] = []
    issues: List[str] = []

    current_id = ""
    current_line = 0
    current_state = ""
    current_priority = ""
    current_target = ""
    current_owner = ""

    def flush() -> None:
        nonlocal current_id, current_line, current_state, current_priority, current_target, current_owner
        if current_id == "":
            return
        missing = []
        if current_state == "":
            missing.append("State")
        if current_priority == "":
            missing.append("Priority")
        if current_target == "":
            missing.append("Target iteration")
        if current_owner == "":
            missing.append("Owner")
        if missing:
            issues.append(
                f"{path.relative_to(ROOT)}:{current_line}: {current_id} missing required fields: {', '.join(missing)}"
            )
        else:
            entries.append(
                BacklogEntry(
                    item_id=current_id,
                    state=_normalize_value(current_state),
                    priority=_normalize_value(current_priority),
                    target_iteration=_normalize_value(current_target),
                    owner=_normalize_value(current_owner),
                    source=path,
                    line=current_line,
                )
            )
        current_id = ""
        current_line = 0
        current_state = ""
        current_priority = ""
        current_target = ""
        current_owner = ""

    for idx, line in enumerate(lines, start=1):
        heading = ENTRY_RE.match(line.strip())
        if heading is not None:
            flush()
            current_id = heading.group(1)
            current_line = idx
            continue

        if current_id == "":
            continue

        state_match = STATE_RE.match(line.strip())
        if state_match is not None and current_state == "":
            current_state = state_match.group(1)
            continue

        priority_match = PRIORITY_RE.match(line.strip())
        if priority_match is not None and current_priority == "":
            current_priority = priority_match.group(1)
            continue

        target_match = TARGET_RE.match(line.strip())
        if target_match is not None and current_target == "":
            current_target = target_match.group(1)
            continue

        owner_match = OWNER_RE.match(line.strip())
        if owner_match is not None and current_owner == "":
            current_owner = owner_match.group(1)
            continue

    flush()
    return entries, issues


def validate_entries(active: List[BacklogEntry], archive: List[BacklogEntry]) -> List[str]:
    issues: List[str] = []
    seen: Dict[str, BacklogEntry] = {}

    def check(entry: BacklogEntry, is_archive: bool) -> None:
        key = entry.state.lower()
        if key not in VALID_STATES:
            issues.append(
                f"{entry.source.relative_to(ROOT)}:{entry.line}: {entry.item_id} has invalid state '{entry.state}'"
            )

        prio = entry.priority.lower()
        if prio not in VALID_PRIORITIES:
            issues.append(
                f"{entry.source.relative_to(ROOT)}:{entry.line}: {entry.item_id} has invalid priority '{entry.priority}'"
            )

        if not TARGET_ALLOWED_RE.match(entry.target_iteration):
            issues.append(
                f"{entry.source.relative_to(ROOT)}:{entry.line}: {entry.item_id} has invalid target iteration '{entry.target_iteration}'"
            )

        if entry.owner == "":
            issues.append(
                f"{entry.source.relative_to(ROOT)}:{entry.line}: {entry.item_id} has empty owner"
            )

        if is_archive and key != "done":
            issues.append(
                f"{entry.source.relative_to(ROOT)}:{entry.line}: archive item {entry.item_id} must have State Done"
            )

        if not is_archive and key == "done":
            issues.append(
                f"{entry.source.relative_to(ROOT)}:{entry.line}: active item {entry.item_id} must be moved to archive when Done"
            )

        prev = seen.get(entry.item_id)
        if prev is not None:
            issues.append(
                f"{entry.source.relative_to(ROOT)}:{entry.line}: duplicate backlog id {entry.item_id}; "
                f"already defined at {prev.source.relative_to(ROOT)}:{prev.line}"
            )
        else:
            seen[entry.item_id] = entry

    for item in active:
        check(item, is_archive=False)
    for item in archive:
        check(item, is_archive=True)

    return issues


def lint() -> List[str]:
    active_entries, active_issues = parse_entries(ACTIVE_BACKLOG)
    archive_entries, archive_issues = parse_entries(ARCHIVE_BACKLOG)
    issues = active_issues + archive_issues
    issues.extend(validate_entries(active_entries, archive_entries))
    return issues


def collect_known_backlog_ids() -> Tuple[Set[str], List[str]]:
    active_entries, active_issues = parse_entries(ACTIVE_BACKLOG)
    archive_entries, archive_issues = parse_entries(ARCHIVE_BACKLOG)
    issues = active_issues + archive_issues
    ids = {entry.item_id for entry in active_entries}
    ids.update(entry.item_id for entry in archive_entries)
    return ids, issues


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
        print("backlog-lint: FAIL")
        for issue in issues:
            print(f"- {issue}")
        print(f"backlog-lint: report -> {REPORT_PATH.relative_to(ROOT)}")
        return 1

    print("backlog-lint: OK")
    print(f"backlog-lint: report -> {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
