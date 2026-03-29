#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECS_DIR = ROOT / "docs" / "specs"
ISSUE_REF_RE = re.compile(r"^(?:#\d+|N/A(?:\s*\(.+\))?)$")
VALID_SPEC_STAGES = {
    "local pre-deploy",
    "cluster rollout",
    "post-deploy follow-up",
    "cross-cutting change",
}
VALID_PRIORITIES = {"p0", "p1", "p2", "p3"}


def _normalize_title(raw: str) -> str:
    cleaned = raw.replace("_", "-").strip("-")
    if cleaned == "":
        return "Untitled"
    return " ".join(part.capitalize() for part in cleaned.split("-") if part)


def _validate_non_empty(value: str, label: str) -> None:
    if value.strip() == "":
        raise ValueError(f"{label} must be non-empty")


def _validate_issue_ref(issue_ref: str) -> None:
    if ISSUE_REF_RE.match(issue_ref.strip()) is None:
        raise ValueError("issue must match #123 or N/A (reason)")


def _validate_spec_stage(stage: str) -> None:
    if stage.strip().lower() not in VALID_SPEC_STAGES:
        raise ValueError(
            "stage must be one of: Local pre-deploy, Cluster rollout, Post-deploy follow-up, Cross-cutting change"
        )


def _validate_priority(priority: str) -> None:
    if priority.strip().lower() not in VALID_PRIORITIES:
        raise ValueError("priority must be one of: P0, P1, P2, P3")


def create_spec_doc(args: argparse.Namespace) -> Path:
    _validate_non_empty(args.name, "name")
    _validate_non_empty(args.owner, "owner")
    _validate_issue_ref(args.issue)
    _validate_spec_stage(args.stage)
    _validate_priority(args.priority)

    file_name = args.name if args.name.endswith(".md") else f"{args.name}.md"
    path = SPECS_DIR / file_name
    if path.exists() and not args.force:
        raise ValueError(f"spec file already exists: {path.relative_to(ROOT)}")

    title = args.title if args.title else _normalize_title(path.stem)
    content = f"""# {title}

Status: Draft
Owner: {args.owner}
Issue: {args.issue}
Stage: {args.stage}
Priority: {args.priority}

## Goal

## Why Now

## Scope

- Included:
- Non-goals:

## Sequencing

- Blocked by:
  - none
- Blocks:
  - <spec, issue, or rollout step that stays blocked until this lands>
- Parallelizable with:
  - none

## Plan

- [ ] Land the local code and documentation changes.
- [ ] Run `make governance-check`.
- [ ] Run `make check`.
- [ ] Open or link any deferred follow-up as `#123` before closure.

## Validation

- Local checks:
  - `make governance-check`
  - `make check`
- Manual validation:
- Deferred validation for cluster rollout:

## Rollout

- Cluster impact:
- Rollout order:
- Rollback notes:

## Links

- Issue: {args.issue}
- PR: pending
- Related docs: `AGENTS.md`
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scaffold governance docs")
    sub = parser.add_subparsers(dest="command", required=True)

    spec = sub.add_parser("spec", help="create docs/specs/<name>.md from scaffold")
    spec.add_argument("--name", required=True)
    spec.add_argument("--owner", default="platform")
    spec.add_argument("--issue", default="N/A (local pre-deploy planning)")
    spec.add_argument("--stage", default="Local pre-deploy")
    spec.add_argument("--priority", default="P1")
    spec.add_argument("--title")
    spec.add_argument("--force", action="store_true")

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if args.command == "spec":
            path = create_spec_doc(args)
            print(f"created spec doc {path.relative_to(ROOT)}")
        else:
            parser.error("unknown command")
    except ValueError as exc:
        print(f"scaffold-docs: ERROR: {exc}")
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
