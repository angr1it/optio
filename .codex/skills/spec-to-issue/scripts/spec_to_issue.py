#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REQUIRED_SECTIONS = [
    "Goal",
    "Why Now",
    "Scope",
    "Plan",
    "Validation",
    "Rollout",
    "Links",
]
CHECKBOX_RE = re.compile(r"^- \[(?P<state>[ xX])\] (?P<text>.+)$", re.MULTILINE)
LINK_TEMPLATE = r"^\s*-\s*{label}:\s*(?P<value>.+?)\s*$"
VALIDATION_STEP_MARKERS = (
    "make governance-check",
    "make test",
    "make check",
    "make smoke",
)
DEFERRED_MARKERS = ("carry over to", "deferred to", "deferred follow-up")


@dataclass(frozen=True)
class SpecDoc:
    path: Path
    title: str
    status: str
    owner: str
    issue_ref: str
    stage: str
    goal: str
    why_now: str
    scope: str
    plan: str
    validation: str
    rollout: str
    links: str


@dataclass(frozen=True)
class IssueDraft:
    title: str
    body: str


def find_repo_root(start_dir: Path) -> Path:
    for candidate in [start_dir, *start_dir.parents]:
        if (candidate / "AGENTS.md").exists():
            return candidate
    raise RuntimeError("could not locate repository root from script path")


ROOT = find_repo_root(Path(__file__).resolve().parent)


def resolve_spec_path(raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()

    if not path.exists():
        raise ValueError(f"spec file does not exist: {raw}")
    if not path.is_file():
        raise ValueError(f"spec path is not a file: {raw}")
    return path


def rel_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def extract_title(text: str) -> str:
    match = re.search(r"^# (?P<title>.+)$", text, re.MULTILINE)
    if match is None:
        raise ValueError("missing top-level '# <title>' heading")
    return match.group("title").strip()


def extract_header_value(text: str, label: str) -> str | None:
    pattern = re.compile(rf"^{re.escape(label)}:\s*(?P<value>.+?)\s*$", re.MULTILINE)
    match = pattern.search(text)
    if match is None:
        return None
    return match.group("value").strip()


def extract_section_body(text: str, title: str) -> str | None:
    match = re.search(
        rf"^## {re.escape(title)}\n(?P<body>.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        return None
    return match.group("body").strip()


def extract_link_value(links_body: str, label: str) -> str | None:
    pattern = re.compile(LINK_TEMPLATE.format(label=re.escape(label)), re.MULTILINE)
    match = pattern.search(links_body)
    if match is None:
        return None
    return match.group("value").strip()


def extract_labeled_list(section_body: str, label: str) -> list[str]:
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


def parse_spec(path: Path) -> SpecDoc:
    text = path.read_text(encoding="utf-8")
    title = extract_title(text)
    status = extract_header_value(text, "Status")
    owner = extract_header_value(text, "Owner")
    issue_ref = extract_header_value(text, "Issue")
    stage = extract_header_value(text, "Stage")

    missing: list[str] = []
    if status is None:
        missing.append("Status")
    if owner is None:
        missing.append("Owner")
    if issue_ref is None:
        missing.append("Issue")
    if stage is None:
        missing.append("Stage")

    sections: dict[str, str] = {}
    for section in REQUIRED_SECTIONS:
        body = extract_section_body(text, section)
        if body is None:
            missing.append(f"## {section}")
            continue
        sections[section] = body

    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"{rel_path(path)} is missing required fields/sections: {joined}")

    assert status is not None
    assert owner is not None
    assert issue_ref is not None
    assert stage is not None

    return SpecDoc(
        path=path,
        title=title,
        status=status,
        owner=owner,
        issue_ref=issue_ref,
        stage=stage,
        goal=sections["Goal"],
        why_now=sections["Why Now"],
        scope=sections["Scope"],
        plan=sections["Plan"],
        validation=sections["Validation"],
        rollout=sections["Rollout"],
        links=sections["Links"],
    )


def build_acceptance_criteria(local_plan: str, scope: str) -> tuple[list[str], list[str]]:
    criteria: list[str] = []
    deferred: list[str] = []

    for match in CHECKBOX_RE.finditer(local_plan):
        item = match.group("text").strip()
        lowered = item.lower()
        if any(marker in lowered for marker in VALIDATION_STEP_MARKERS):
            continue
        if any(marker in lowered for marker in DEFERRED_MARKERS):
            deferred.append(item)
            continue
        criteria.append(item)

    if not criteria:
        criteria = extract_labeled_list(scope, "Included")

    if not criteria:
        criteria = ["Deliver the scoped change described in the primary spec."]

    return criteria, deferred


def render_validation_signals(spec: SpecDoc) -> str:
    lines: list[str] = []

    local_checks = extract_labeled_list(spec.validation, "Local checks")
    manual_checks = extract_labeled_list(spec.validation, "Manual validation")
    deferred_rollout = extract_labeled_list(spec.validation, "Deferred validation for cluster rollout")
    cluster_impact = extract_labeled_list(spec.rollout, "Cluster impact")
    rollout_order = extract_labeled_list(spec.rollout, "Rollout order")
    rollback_notes = extract_labeled_list(spec.rollout, "Rollback notes")

    if local_checks:
        lines.append("- Checks:")
        lines.extend(f"  - {item}" for item in local_checks)

    if manual_checks:
        lines.append("- Manual validation:")
        lines.extend(f"  - {item}" for item in manual_checks)

    if deferred_rollout:
        lines.append("- Deferred rollout validation:")
        lines.extend(f"  - {item}" for item in deferred_rollout)

    if cluster_impact or rollout_order or rollback_notes:
        lines.append("- Rollout notes:")
        lines.extend(f"  - Cluster impact: {item}" for item in cluster_impact)
        if rollout_order:
            lines.append("  - Rollout order:")
            lines.extend(f"    - {item}" for item in rollout_order)
        if rollback_notes:
            lines.append("  - Rollback notes:")
            lines.extend(f"    - {item}" for item in rollback_notes)

    if not lines:
        lines.append("- Checks: document the required local and manual validation steps.")

    return "\n".join(lines)


def render_related_context(spec: SpecDoc) -> str:
    lines = [
        f"- Primary spec: `{rel_path(spec.path)}`",
        f"- Spec status: `{spec.status}`",
        f"- Spec stage: `{spec.stage}`",
        f"- Spec owner: `{spec.owner}`",
        f"- Spec issue field: `{spec.issue_ref}`",
    ]

    related_docs = extract_link_value(spec.links, "Related docs")
    if related_docs:
        lines.append(f"- Related docs: {related_docs}")

    linked_pr = extract_link_value(spec.links, "PR")
    if linked_pr:
        lines.append(f"- Linked PR field in spec: `{linked_pr}`")

    return "\n".join(lines)


def render_governance_follow_up(spec: SpecDoc, deferred_items: list[str]) -> str:
    lines = [
        f"- Keep implementation and PR scope aligned with `{rel_path(spec.path)}`.",
        "- Update the spec if scope, rollout, or validation changes during implementation.",
    ]

    if deferred_items:
        lines.append("- Carry-over items already called out in the spec:")
        lines.extend(f"  - {item}" for item in deferred_items)
    else:
        lines.append("- If anything is deferred, move it to GitHub issues or project items before closure.")

    return "\n".join(lines)


def build_issue_draft(spec: SpecDoc) -> IssueDraft:
    acceptance_criteria, deferred_items = build_acceptance_criteria(spec.plan, spec.scope)
    body = "\n\n".join(
        [
            "## Summary\n\n" + spec.goal.strip(),
            "## Why Now\n\n" + spec.why_now.strip(),
            "## Scope\n\n" + spec.scope.strip(),
            "## Acceptance Criteria\n\n" + "\n".join(f"- {item}" for item in acceptance_criteria),
            "## Validation Signals\n\n" + render_validation_signals(spec),
            "## Related Context\n\n" + render_related_context(spec),
            "## Governance Follow-Up\n\n" + render_governance_follow_up(spec, deferred_items),
        ]
    ).strip()

    return IssueDraft(title=spec.title, body=body + "\n")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render a GitHub issue draft from an Optio spec doc")
    parser.add_argument("spec_path", help="Path to docs/specs/<name>.md")
    parser.add_argument("--title-only", action="store_true")
    parser.add_argument("--body-only", action="store_true")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.title_only and args.body_only:
        parser.error("--title-only and --body-only cannot be used together")

    try:
        spec = parse_spec(resolve_spec_path(args.spec_path))
        draft = build_issue_draft(spec)
    except ValueError as exc:
        print(f"spec-to-issue: ERROR: {exc}", file=sys.stderr)
        return 2
    except RuntimeError as exc:
        print(f"spec-to-issue: ERROR: {exc}", file=sys.stderr)
        return 2

    if args.title_only:
        print(draft.title)
        return 0

    if args.body_only:
        print(draft.body, end="")
        return 0

    print("Title:")
    print(draft.title)
    print()
    print("Body:")
    print(draft.body, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
