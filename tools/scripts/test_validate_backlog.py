from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import validate_backlog


class ValidateBacklogTests(unittest.TestCase):
    def test_parse_entries_valid_block(self) -> None:
        with tempfile.TemporaryDirectory(dir=validate_backlog.ROOT / "var") as tmp:
            path = Path(tmp) / "BACKLOG.md"
            path.write_text(
                """## BLG-123: Sample item
**State:** Ready
**Priority:** Medium
**Target iteration:** `ITR-001`
**Owner:** `platform`
""",
                encoding="utf-8",
            )

            entries, issues = validate_backlog.parse_entries(path)
            self.assertEqual([], issues)
            self.assertEqual(1, len(entries))
            self.assertEqual("BLG-123", entries[0].item_id)
            self.assertEqual("Ready", entries[0].state)

    def test_active_done_is_rejected(self) -> None:
        entry = validate_backlog.BacklogEntry(
            item_id="BLG-123",
            state="Done",
            priority="High",
            target_iteration="ITR-001",
            owner="platform",
            source=validate_backlog.ACTIVE_BACKLOG,
            line=2,
        )
        issues = validate_backlog.validate_entries([entry], [])
        self.assertTrue(any("must be moved to archive" in i for i in issues))

    def test_archive_non_done_is_rejected(self) -> None:
        entry = validate_backlog.BacklogEntry(
            item_id="BLG-123",
            state="Ready",
            priority="High",
            target_iteration="ITR-001",
            owner="platform",
            source=validate_backlog.ARCHIVE_BACKLOG,
            line=2,
        )
        issues = validate_backlog.validate_entries([], [entry])
        self.assertTrue(any("must have State Done" in i for i in issues))

    def test_invalid_target_iteration_is_rejected(self) -> None:
        entry = validate_backlog.BacklogEntry(
            item_id="BLG-123",
            state="Ready",
            priority="High",
            target_iteration="Sprint-1",
            owner="platform",
            source=validate_backlog.ACTIVE_BACKLOG,
            line=2,
        )
        issues = validate_backlog.validate_entries([entry], [])
        self.assertTrue(any("invalid target iteration" in i for i in issues))


if __name__ == "__main__":
    unittest.main()
