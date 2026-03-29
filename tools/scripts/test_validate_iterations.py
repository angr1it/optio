from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import validate_iterations


class ValidateIterationsTests(unittest.TestCase):
    def test_iteration_dir_valid(self) -> None:
        with tempfile.TemporaryDirectory(dir=validate_iterations.ROOT / "var") as tmp:
            itr_dir = Path(tmp) / "ITR-999"
            itr_dir.mkdir(parents=True)
            (itr_dir / "iteration.md").write_text(
                """# Iteration ITR-999
**Status:** Planned

Related backlog items:
- BLG-123

## Scope

## Definition Of Done (DoD)

## Carry-over

## Closure
""",
                encoding="utf-8",
            )
            (itr_dir / "execution-plan.md").write_text(
                """# Execution Plan: ITR-999

## Steps
- [x] Confirm scope against backlog items.
- [ ] Execute tasks in small vertical slices.
- [ ] Run `make check` before closure.
""",
                encoding="utf-8",
            )
            (itr_dir / "status-report.md").write_text("# status\n", encoding="utf-8")

            issues = validate_iterations.lint_iteration_dir(itr_dir, known_backlog_ids={"BLG-123"})
            self.assertEqual([], issues)

    def test_iteration_dir_missing_required_file(self) -> None:
        with tempfile.TemporaryDirectory(dir=validate_iterations.ROOT / "var") as tmp:
            itr_dir = Path(tmp) / "ITR-999"
            itr_dir.mkdir(parents=True)
            (itr_dir / "iteration.md").write_text(
                """# Iteration ITR-999
**Status:** Planned

Related backlog items:
- BLG-123

## Scope

## Definition Of Done (DoD)

## Carry-over

## Closure
""",
                encoding="utf-8",
            )
            (itr_dir / "execution-plan.md").write_text(
                """# Execution Plan: ITR-999

## Steps
- [ ] Confirm scope against backlog items.
""",
                encoding="utf-8",
            )

            issues = validate_iterations.lint_iteration_dir(itr_dir, known_backlog_ids={"BLG-123"})
            self.assertTrue(any("status-report.md" in issue for issue in issues))

    def test_iteration_dir_unknown_backlog_id(self) -> None:
        with tempfile.TemporaryDirectory(dir=validate_iterations.ROOT / "var") as tmp:
            itr_dir = Path(tmp) / "ITR-999"
            itr_dir.mkdir(parents=True)
            (itr_dir / "iteration.md").write_text(
                """# Iteration ITR-999
**Status:** Planned

Related backlog items:
- BLG-999

## Scope

## Definition Of Done (DoD)

## Carry-over

## Closure
""",
                encoding="utf-8",
            )
            (itr_dir / "execution-plan.md").write_text(
                """# Execution Plan: ITR-999

## Steps
- [ ] Confirm scope against backlog items.
""",
                encoding="utf-8",
            )
            (itr_dir / "status-report.md").write_text("# status\n", encoding="utf-8")

            issues = validate_iterations.lint_iteration_dir(itr_dir, known_backlog_ids={"BLG-123"})
            self.assertTrue(any("does not exist" in issue for issue in issues))

    def test_steps_must_use_checkboxes(self) -> None:
        with tempfile.TemporaryDirectory(dir=validate_iterations.ROOT / "var") as tmp:
            itr_dir = Path(tmp) / "ITR-999"
            itr_dir.mkdir(parents=True)
            (itr_dir / "iteration.md").write_text(
                """# Iteration ITR-999
**Status:** In Progress

Related backlog items:
- BLG-123

## Scope

## Definition Of Done (DoD)

## Carry-over

## Closure
""",
                encoding="utf-8",
            )
            (itr_dir / "execution-plan.md").write_text(
                """# Execution Plan: ITR-999

## Steps
1. Confirm scope against backlog items.
""",
                encoding="utf-8",
            )
            (itr_dir / "status-report.md").write_text("# status\n", encoding="utf-8")

            issues = validate_iterations.lint_iteration_dir(itr_dir, known_backlog_ids={"BLG-123"})
            self.assertTrue(any("must use Markdown checkboxes" in issue for issue in issues))

    def test_closed_iteration_cannot_leave_open_checkboxes(self) -> None:
        with tempfile.TemporaryDirectory(dir=validate_iterations.ROOT / "var") as tmp:
            itr_dir = Path(tmp) / "ITR-999"
            itr_dir.mkdir(parents=True)
            (itr_dir / "iteration.md").write_text(
                """# Iteration ITR-999
**Status:** Closed

Related backlog items:
- BLG-123

## Scope

## Definition Of Done (DoD)

## Carry-over

## Closure
""",
                encoding="utf-8",
            )
            (itr_dir / "execution-plan.md").write_text(
                """# Execution Plan: ITR-999

## Steps
- [x] Confirm scope against backlog items.
- [ ] Finish the remaining validator work.
""",
                encoding="utf-8",
            )
            (itr_dir / "status-report.md").write_text("# status\n", encoding="utf-8")

            issues = validate_iterations.lint_iteration_dir(itr_dir, known_backlog_ids={"BLG-123"})
            self.assertTrue(any("cannot leave open checklist items" in issue for issue in issues))

    def test_deferred_item_requires_follow_up_backlog_id(self) -> None:
        with tempfile.TemporaryDirectory(dir=validate_iterations.ROOT / "var") as tmp:
            itr_dir = Path(tmp) / "ITR-999"
            itr_dir.mkdir(parents=True)
            (itr_dir / "iteration.md").write_text(
                """# Iteration ITR-999
**Status:** Closed with follow-ups

Related backlog items:
- BLG-123

## Scope

## Definition Of Done (DoD)

## Carry-over

## Closure
""",
                encoding="utf-8",
            )
            (itr_dir / "execution-plan.md").write_text(
                """# Execution Plan: ITR-999

## Steps
- [x] Confirm scope against backlog items.
- [x] Deferred: finish the remaining validator work.
""",
                encoding="utf-8",
            )
            (itr_dir / "status-report.md").write_text("# status\n", encoding="utf-8")

            issues = validate_iterations.lint_iteration_dir(itr_dir, known_backlog_ids={"BLG-123"})
            self.assertTrue(any("follow-up backlog id" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
