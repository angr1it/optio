#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parent / "spec_to_issue.py"
SPEC = importlib.util.spec_from_file_location("spec_to_issue", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class SpecToIssueTests(unittest.TestCase):
    def write_spec(self, name: str, content: str) -> Path:
        tmpdir = tempfile.TemporaryDirectory(dir=MODULE.ROOT / "var")
        self.addCleanup(tmpdir.cleanup)
        path = Path(tmpdir.name) / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_build_issue_draft_from_spec(self) -> None:
        spec_path = self.write_spec(
            "runtime-queue-hardening.md",
            """# Runtime Queue Hardening

Status: Draft
Owner: platform
Issue: N/A (local pre-deploy planning)
Stage: Cross-cutting change
Priority: P0

## Goal

Harden queue retry behavior across worker restarts.

## Why Now

Retry state can drift during worker restarts and needs a documented local-first fix before cluster rollout.

## Scope

- Included:
  - persist retry state before worker handoff
  - restore retry state during worker resume
- Non-goals:
  - redesigning the task schema

## Sequencing

- Blocked by:
  - none
- Blocks:
  - #456
- Parallelizable with:
  - none

## Plan

- [ ] Persist retry state before worker handoff.
- [ ] Restore retry state during worker resume.
- [ ] Run `make governance-check`.
- [ ] Run `make check`.
- [ ] Carry over to #456: observe one live recovery cycle in cluster.

## Validation

- Local checks:
  - `make governance-check`
  - `make check`
- Manual validation:
  - inspect retry logs after a forced worker restart
- Deferred validation for cluster rollout:
  - observe one live recovery cycle in cluster

## Rollout

- Cluster impact:
  - low; restart behavior changes only
- Rollout order:
  - land the local implementation
  - verify retry logs locally
- Rollback notes:
  - revert worker resume changes if retries fan out unexpectedly

## Links

- Issue: N/A (local pre-deploy planning)
- PR: pending
- Related docs: `AGENTS.md`, `docs/process/feature-driven-development.md`
""",
        )

        spec = MODULE.parse_spec(spec_path)
        draft = MODULE.build_issue_draft(spec)

        self.assertEqual("Runtime Queue Hardening", draft.title)
        self.assertIn("## Acceptance Criteria", draft.body)
        self.assertIn("- Persist retry state before worker handoff.", draft.body)
        self.assertIn("- Restore retry state during worker resume.", draft.body)
        self.assertIn("- Carry-over items already called out in the spec:", draft.body)
        self.assertIn("- Spec priority: `P0`", draft.body)
        self.assertIn("- Blocks:", draft.body)
        self.assertIn("- Checks:", draft.body)
        self.assertIn("`make governance-check`", draft.body)
        self.assertIn("Primary spec:", draft.body)

    def test_parse_spec_fails_on_missing_sections(self) -> None:
        spec_path = self.write_spec(
            "broken.md",
            """# Broken Spec

Status: Draft
Owner: platform
Issue: #123
Stage: Local pre-deploy

## Goal

Something.
""",
        )

        with self.assertRaisesRegex(ValueError, "missing required fields/sections"):
            MODULE.parse_spec(spec_path)


if __name__ == "__main__":
    unittest.main()
