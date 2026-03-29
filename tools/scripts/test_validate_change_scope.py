from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_change_scope


class ValidateChangeScopeTests(unittest.TestCase):
    def test_non_sensitive_changes_do_not_require_spec(self) -> None:
        issues = validate_change_scope.lint_change_scope(["README.md"])
        self.assertEqual([], issues)

    def test_local_sensitive_change_requires_spec_or_override(self) -> None:
        issues = validate_change_scope.lint_change_scope(["apps/api/src/routes/issues.ts"])
        self.assertTrue(any("sensitive paths changed without a local spec reference" in issue for issue in issues))

    def test_local_sensitive_change_passes_when_spec_doc_changes(self) -> None:
        issues = validate_change_scope.lint_change_scope(
            ["apps/api/src/routes/issues.ts", "docs/specs/runtime-change.md"]
        )
        self.assertEqual([], issues)

    def test_pr_context_requires_pr_spec_reference(self) -> None:
        issues = validate_change_scope.lint_change_scope(
            ["apps/api/src/workers/pr-watcher-worker.ts"],
            in_pr_context=True,
        )
        self.assertTrue(any("fill '- Spec:' in the PR template" in issue for issue in issues))

    def test_override_spec_ref_must_exist_when_it_points_to_a_doc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            issues = validate_change_scope.lint_change_scope(
                ["apps/api/src/db/schema.ts"],
                override_spec_ref="docs/specs/missing.md",
                root=root,
            )
            self.assertTrue(any("referenced spec doc does not exist" in issue for issue in issues))

    def test_override_spec_ref_passes_when_doc_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = root / "docs" / "specs" / "runtime-change.md"
            spec_path.parent.mkdir(parents=True, exist_ok=True)
            spec_path.write_text("# Runtime Change\n", encoding="utf-8")

            issues = validate_change_scope.lint_change_scope(
                ["helm/optio/values.yaml"],
                override_spec_ref="docs/specs/runtime-change.md",
                root=root,
            )
            self.assertEqual([], issues)

    def test_extract_spec_ref_from_pr_body(self) -> None:
        spec_ref = validate_change_scope.extract_spec_ref_from_pr_body(
            "## Artifact Chain\n\n- Issue: `#123`\n- Spec: `docs/specs/runtime-change.md`\n"
        )
        self.assertEqual("docs/specs/runtime-change.md", spec_ref)


if __name__ == "__main__":
    unittest.main()
