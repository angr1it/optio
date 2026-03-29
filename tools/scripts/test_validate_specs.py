from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_specs


VALID_SPEC = """# Local Runtime Change

Status: Draft
Owner: platform
Issue: N/A (local pre-deploy planning)
Stage: Local pre-deploy

## Goal

Plan a substantial local-first change before cluster rollout.

## Why Now

The repository needs a design artifact before runtime-sensitive work starts.

## Scope

- Included:
  - Local workflow updates
- Non-goals:
  - Cluster rollout itself

## Plan

- [x] Update the process docs.
- [ ] Run the full local gate.

## Validation

- Local checks:
  - `make governance-check`
  - `make check`
- Manual validation:
  - Confirm the templates and validators stay aligned.
- Deferred validation for cluster rollout:
  - Re-run the same checks in CI.

## Rollout

- Cluster impact:
  - None yet.
- Rollout order:
  - Land the local changes first.
- Rollback notes:
  - Revert the governance slice in one change set if needed.

## Links

- Issue: N/A (local pre-deploy planning)
- PR: pending
- Related docs: `docs/process/feature-driven-development.md`
"""


class ValidateSpecsTests(unittest.TestCase):
    def _lint(self, content: str) -> list[str]:
        with tempfile.TemporaryDirectory(dir=validate_specs.ROOT / "var") as tmp:
            path = Path(tmp) / "spec.md"
            path.write_text(content, encoding="utf-8")
            return validate_specs.lint_spec(path)

    def test_lint_spec_passes_for_valid_spec(self) -> None:
        self.assertEqual([], self._lint(VALID_SPEC))

    def test_lint_spec_requires_allowed_status_values(self) -> None:
        issues = self._lint(VALID_SPEC.replace("Status: Draft", "Status: Done"))
        self.assertTrue(any("invalid Status" in issue for issue in issues))

    def test_lint_spec_requires_checklist_items_in_local_plan(self) -> None:
        issues = self._lint(
            VALID_SPEC.replace(
                "## Plan\n\n- [x] Update the process docs.\n- [ ] Run the full local gate.",
                "## Plan\n\n- Local change set:\n- Exit criteria before deploy:",
            )
        )
        self.assertTrue(any("must contain markdown checklist items" in issue for issue in issues))

    def test_implemented_specs_require_closed_local_plan(self) -> None:
        issues = self._lint(VALID_SPEC.replace("Status: Draft", "Status: Implemented"))
        self.assertTrue(any("requires all '## Plan' checklist items to be completed" in issue for issue in issues))

    def test_deferred_items_require_follow_up_issue(self) -> None:
        issues = self._lint(
            VALID_SPEC.replace(
                "- [ ] Run the full local gate.",
                "- [ ] Deferred to the next rollout window.",
            )
        )
        self.assertTrue(any("deferred/carry-over item" in issue for issue in issues))

    def test_links_issue_must_match_header_issue(self) -> None:
        issues = self._lint(
            VALID_SPEC.replace(
                "- Issue: N/A (local pre-deploy planning)",
                "- Issue: #123",
            )
        )
        self.assertTrue(any("issue must match the header Issue value exactly" in issue for issue in issues))

    def test_links_require_valid_pr_reference(self) -> None:
        issues = self._lint(VALID_SPEC.replace("- PR: pending", "- PR: to-be-added"))
        self.assertTrue(any("invalid PR link" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
