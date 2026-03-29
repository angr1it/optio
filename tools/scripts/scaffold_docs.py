#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import Iterable, List

import validate_backlog

ROOT = Path(__file__).resolve().parents[2]
BACKLOG_PATH = ROOT / "docs" / "roadmap" / "BACKLOG.md"
FEATURES_DIR = ROOT / "docs" / "features"
ITERATIONS_DIR = ROOT / "docs" / "roadmap" / "iterations"

BACKLOG_ID_RE = re.compile(r"^BLG-\d{3}$")
ITERATION_ID_RE = re.compile(r"^ITR-[A-Za-z0-9-]+$")
TARGET_ITERATION_RE = re.compile(r"^(?:TBD|ITR-[A-Za-z0-9-]+)$")
VALID_PRIORITIES = {"high", "medium", "low"}
VALID_STATES = {"proposed", "ready", "in progress", "blocked", "deferred", "done"}


def _normalize_title(raw: str) -> str:
    cleaned = raw.replace("_", "-").strip("-")
    if cleaned == "":
        return "Untitled"
    return " ".join(part.capitalize() for part in cleaned.split("-") if part)


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _append_block(path: Path, block: str) -> None:
    current = _read_text(path)
    if current.strip() == "":
        content = block.strip() + "\n"
    else:
        content = current.rstrip() + "\n\n" + block.strip() + "\n"
    _write_text(path, content)


def _validate_backlog_id(item_id: str) -> None:
    if BACKLOG_ID_RE.match(item_id) is None:
        raise ValueError("backlog id must match BLG-###")


def _validate_iteration_id(iteration_id: str) -> None:
    if ITERATION_ID_RE.match(iteration_id) is None:
        raise ValueError("iteration id must match ITR-<token>")


def _validate_backlog_ids_exist(item_ids: Iterable[str]) -> None:
    known_ids, issues = validate_backlog.collect_known_backlog_ids()
    if issues:
        joined = "; ".join(issues)
        raise ValueError(f"cannot read backlog registry: {joined}")

    missing = sorted({item_id for item_id in item_ids if item_id not in known_ids})
    if missing:
        raise ValueError(
            "backlog id(s) not found in active/archive backlog: " + ", ".join(missing)
        )


def _validate_non_empty(value: str, label: str) -> None:
    if value.strip() == "":
        raise ValueError(f"{label} must be non-empty")


def create_backlog_item(args: argparse.Namespace) -> Path:
    _validate_backlog_id(args.id)
    _validate_non_empty(args.title, "title")
    _validate_non_empty(args.owner, "owner")
    if args.priority.strip().lower() not in VALID_PRIORITIES:
        raise ValueError("priority must be one of: High, Medium, Low")
    if args.state.strip().lower() not in VALID_STATES:
        raise ValueError("state must be one of: Proposed, Ready, In Progress, Blocked, Deferred, Done")
    if TARGET_ITERATION_RE.match(args.target_iteration.strip()) is None:
        raise ValueError("target iteration must be TBD or ITR-<token>")

    known_ids, issues = validate_backlog.collect_known_backlog_ids()
    if issues:
        raise ValueError("cannot read backlog files: " + "; ".join(issues))
    if args.id in known_ids:
        raise ValueError(f"backlog id already exists: {args.id}")

    block = f"""## {args.id}: {args.title}
**State:** {args.state}
**Priority:** {args.priority}
**Target iteration:** `{args.target_iteration}`
**Owner:** `{args.owner}`

## Context
- Add context.

## Why
- Add rationale.

## Scope
- Included:
- Explicitly out of scope:

## Acceptance Criteria
- Add measurable outcome(s).

## Validation
- Required checks:
  - `make test`
  - `make check`

## Links
- Feature spec(s): `docs/features/...`
- Iteration docs: `docs/roadmap/iterations/...`

## Change history
- `{date.today().isoformat()}`: created.
"""
    _append_block(BACKLOG_PATH, block)
    return BACKLOG_PATH


def create_feature_doc(args: argparse.Namespace) -> Path:
    _validate_non_empty(args.name, "name")
    _validate_backlog_id(args.backlog_id)
    _validate_non_empty(args.owner, "owner")
    _validate_backlog_ids_exist([args.backlog_id])

    file_name = args.name if args.name.endswith(".md") else f"{args.name}.md"
    path = FEATURES_DIR / file_name
    if path.exists() and not args.force:
        raise ValueError(f"feature file already exists: {path.relative_to(ROOT)}")

    title = args.title if args.title else _normalize_title(path.stem)
    content = f"""# {title}

Status: Draft
Owner: {args.owner}
Backlog: {args.backlog_id}

## Goal

## Scope
- Included:
- Non-goals:

## Design Notes
- Key decisions:
- Trade-offs:

## Acceptance Criteria
- Criterion 1

## Test Plan
- Unit checks:
- Integration/process checks:
- Required commands:
  - `make test`
  - `make check`

## Rollout
- Default behavior:
- Rollback/deprecation notes (if needed):

## Links
- Backlog: `docs/roadmap/BACKLOG.md`
- Iteration: `docs/roadmap/iterations/{args.iteration_id}/iteration.md`
- Related docs:
"""
    _write_text(path, content)
    return path


def create_iteration_bundle(args: argparse.Namespace) -> List[Path]:
    _validate_iteration_id(args.id)
    _validate_non_empty(args.owner, "owner")
    for item_id in args.backlog_ids:
        _validate_backlog_id(item_id)
    _validate_backlog_ids_exist(args.backlog_ids)

    itr_dir = ITERATIONS_DIR / args.id
    if itr_dir.exists() and not args.force:
        raise ValueError(f"iteration folder already exists: {itr_dir.relative_to(ROOT)}")
    itr_dir.mkdir(parents=True, exist_ok=True)

    title = args.title if args.title else _normalize_title(args.id)
    backlog_block = "\n".join(f"- {item_id}" for item_id in args.backlog_ids)

    iteration_md = itr_dir / "iteration.md"
    execution_plan_md = itr_dir / "execution-plan.md"
    status_report_md = itr_dir / "status-report.md"

    _write_text(
        iteration_md,
        f"""# Iteration {args.id}: {title}
**Status:** Planned
**Date:** {date.today().isoformat()}
**Owner:** {args.owner}

Related backlog items:
{backlog_block}

Related feature specs:
- `docs/features/...`

## Scope
- Included:
- Explicitly out of scope:

## Definition Of Done (DoD)
- Functional outcome gates:
- Test gates:
  - `make test`
  - `make check`
- Documentation gates:

## Carry-over
- Inherited items from previous iteration:
- Ownership and disposition for each item:

## Closure
- Final status:
- Completed items:
- Deferred items + follow-ups:
- Validation summary (latest successful checks):
""",
    )

    _write_text(
        execution_plan_md,
        f"""# Execution Plan: {args.id}

## Steps
- [ ] Confirm scope against backlog items.
- [ ] Execute tasks in small vertical slices.
- [ ] Run `make check` before closure.

## Risks
- Add risks.

## Mitigations
- Add mitigations.
""",
    )

    _write_text(
        status_report_md,
        f"""# Status Report: {args.id}

## Summary
- Current status: Planned
- Execution checklist status: 0/3 resolved in `execution-plan.md`
- Follow-ups: None

## Validation
- Pending `make check`.
""",
    )

    return [iteration_md, execution_plan_md, status_report_md]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scaffold roadmap/feature artifacts")
    sub = parser.add_subparsers(dest="command", required=True)

    backlog = sub.add_parser("backlog", help="append a backlog item to docs/roadmap/BACKLOG.md")
    backlog.add_argument("--id", required=True)
    backlog.add_argument("--title", required=True)
    backlog.add_argument("--owner", default="platform")
    backlog.add_argument("--priority", default="Medium")
    backlog.add_argument("--state", default="Proposed")
    backlog.add_argument("--target-iteration", default="TBD")

    feature = sub.add_parser("feature", help="create docs/features/<name>.md from scaffold")
    feature.add_argument("--name", required=True)
    feature.add_argument("--backlog-id", required=True)
    feature.add_argument("--owner", default="platform")
    feature.add_argument("--iteration-id", default="ITR-###")
    feature.add_argument("--title")
    feature.add_argument("--force", action="store_true")

    iteration = sub.add_parser("iteration", help="create iteration bundle under docs/roadmap/iterations/")
    iteration.add_argument("--id", required=True)
    iteration.add_argument("--backlog-id", dest="backlog_ids", action="append", required=True)
    iteration.add_argument("--owner", default="platform")
    iteration.add_argument("--title")
    iteration.add_argument("--force", action="store_true")

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if args.command == "backlog":
            path = create_backlog_item(args)
            print(f"created backlog item in {path.relative_to(ROOT)}")
        elif args.command == "feature":
            path = create_feature_doc(args)
            print(f"created feature doc {path.relative_to(ROOT)}")
        elif args.command == "iteration":
            paths = create_iteration_bundle(args)
            for path in paths:
                print(f"created {path.relative_to(ROOT)}")
        else:
            parser.error("unknown command")
    except ValueError as exc:
        print(f"scaffold-docs: ERROR: {exc}")
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
