#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / "var" / "docs" / "change-scope-report.json"
SENSITIVE_PREFIXES = (
    "apps/api/src/db/",
    "apps/api/src/routes/",
    "apps/api/src/workers/",
    "helm/",
    "k8s/",
)
SPEC_DOC_RE = re.compile(r"^docs/specs/.+\.md$")
SPEC_REF_RE = re.compile(r"^(?:docs/specs/.+\.md|N/A(?:\s*\(.+\))?)$")
PR_SPEC_RE = re.compile(r"^\s*-\s*Spec:\s*`?(?P<value>[^`\n]+)`?\s*$", re.MULTILINE)


def _run_git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "git command failed")
    return completed.stdout.strip()


def _git_lines(*args: str) -> list[str]:
    try:
        output = _run_git(*args)
    except RuntimeError:
        return []

    return sorted({line.strip() for line in output.splitlines() if line.strip()})


def collect_changed_files() -> list[str]:
    changed = {
        * _git_lines("diff", "--name-only", "--cached"),
        * _git_lines("diff", "--name-only"),
        * _git_lines("ls-files", "--others", "--exclude-standard"),
    }
    if changed:
        return sorted(changed)

    base_ref = os.environ.get("GITHUB_BASE_REF", "").strip()
    if base_ref:
        base_diff = _git_lines("diff", "--name-only", f"origin/{base_ref}...HEAD")
        if base_diff:
            return base_diff

    last_commit = _git_lines("diff", "--name-only", "HEAD^..HEAD")
    if last_commit:
        return last_commit

    return _git_lines("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD")


def find_sensitive_paths(paths: list[str]) -> list[str]:
    return sorted(
        path
        for path in paths
        if any(path.startswith(prefix) for prefix in SENSITIVE_PREFIXES)
    )


def find_changed_spec_docs(paths: list[str]) -> list[str]:
    return sorted(path for path in paths if SPEC_DOC_RE.match(path))


def extract_spec_ref_from_pr_body(body: str) -> str | None:
    match = PR_SPEC_RE.search(body)
    if match is None:
        return None
    return match.group("value").strip()


def load_pr_context() -> tuple[bool, str | None]:
    event_path = os.environ.get("GITHUB_EVENT_PATH", "").strip()
    if event_path == "":
        return False, None

    path = Path(event_path)
    if not path.exists():
        return False, None

    payload = json.loads(path.read_text(encoding="utf-8"))
    pull_request = payload.get("pull_request")
    if not isinstance(pull_request, dict):
        return False, None

    body = pull_request.get("body")
    if not isinstance(body, str):
        return True, None

    return True, extract_spec_ref_from_pr_body(body)


def validate_spec_ref(spec_ref: str, root: Path = ROOT) -> str | None:
    if SPEC_REF_RE.match(spec_ref) is None:
        return "spec reference must be 'docs/specs/<name>.md' or 'N/A (reason)'"

    if spec_ref.startswith("docs/specs/"):
        spec_path = root / spec_ref
        if not spec_path.exists():
            return f"referenced spec doc does not exist: {spec_ref}"

    return None


def lint_change_scope(
    changed_files: list[str],
    *,
    override_spec_ref: str | None = None,
    pr_spec_ref: str | None = None,
    in_pr_context: bool = False,
    root: Path = ROOT,
) -> list[str]:
    issues: list[str] = []
    sensitive_paths = find_sensitive_paths(changed_files)
    if not sensitive_paths:
        return issues

    changed_specs = find_changed_spec_docs(changed_files)
    effective_spec_ref = override_spec_ref or pr_spec_ref
    if effective_spec_ref is not None:
        spec_issue = validate_spec_ref(effective_spec_ref, root=root)
        if spec_issue is not None:
            issues.append(spec_issue)
            return issues

    if in_pr_context:
        if effective_spec_ref is None:
            issues.append(
                "sensitive paths changed without a PR spec reference; fill '- Spec:' in the PR template"
            )
        return issues

    if changed_specs:
        return issues

    if effective_spec_ref is None:
        issues.append(
            "sensitive paths changed without a local spec reference; create/update docs/specs/*.md "
            "or run make governance-check SPEC_REF='docs/specs/<name>.md' (or 'N/A (reason)')"
        )

    return issues


def lint() -> tuple[list[str], list[str]]:
    changed_files = collect_changed_files()
    override_spec_ref = os.environ.get("OPTIO_SPEC_REF", "").strip() or None
    in_pr_context, pr_spec_ref = load_pr_context()
    issues = lint_change_scope(
        changed_files,
        override_spec_ref=override_spec_ref,
        pr_spec_ref=pr_spec_ref,
        in_pr_context=in_pr_context,
    )
    return changed_files, issues


def _write_report(changed_files: list[str], issues: list[str]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": len(issues) == 0,
        "changed_files": changed_files,
        "sensitive_paths": find_sensitive_paths(changed_files),
        "changed_specs": find_changed_spec_docs(changed_files),
        "issues": issues,
    }
    REPORT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> int:
    changed_files, issues = lint()
    _write_report(changed_files, issues)

    if issues:
        print("change-scope-lint: FAIL")
        for issue in issues:
            print(f"- {issue}")
        print(f"change-scope-lint: report -> {REPORT_PATH.relative_to(ROOT)}")
        return 1

    print("change-scope-lint: OK")
    print(f"change-scope-lint: report -> {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
