from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import validate_features


class ValidateFeaturesTests(unittest.TestCase):
    def test_lint_feature_valid_file(self) -> None:
        with tempfile.TemporaryDirectory(dir=validate_features.ROOT / "var") as tmp:
            path = Path(tmp) / "feature-valid.md"
            path.write_text(
                """# Feature X

Status: Draft
Owner: platform
Backlog: BLG-123

## Goal

## Scope

## Acceptance Criteria

## Test Plan

            ## Links
- Iteration: docs/roadmap/iterations/ITR-001/iteration.md
""",
                encoding="utf-8",
            )
            issues = validate_features.lint_feature(path, known_backlog_ids={"BLG-123"})
            self.assertEqual([], issues)

    def test_lint_feature_missing_required_section(self) -> None:
        with tempfile.TemporaryDirectory(dir=validate_features.ROOT / "var") as tmp:
            path = Path(tmp) / "feature-invalid.md"
            path.write_text(
                """# Feature X

Status: Draft
Owner: platform
Backlog: BLG-123

## Goal

## Scope

## Test Plan

            ## Links
- Iteration: docs/roadmap/iterations/ITR-001/iteration.md
""",
                encoding="utf-8",
            )
            issues = validate_features.lint_feature(path, known_backlog_ids={"BLG-123"})
            self.assertTrue(any("Acceptance Criteria" in issue for issue in issues))

    def test_lint_feature_unknown_backlog_id(self) -> None:
        with tempfile.TemporaryDirectory(dir=validate_features.ROOT / "var") as tmp:
            path = Path(tmp) / "feature-unknown-backlog.md"
            path.write_text(
                """# Feature X

Status: Draft
Owner: platform
Backlog: BLG-999

## Goal

## Scope

## Acceptance Criteria

## Test Plan

## Links
- Iteration: docs/roadmap/iterations/ITR-001/iteration.md
""",
                encoding="utf-8",
            )
            issues = validate_features.lint_feature(path, known_backlog_ids={"BLG-123"})
            self.assertTrue(any("does not exist" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
