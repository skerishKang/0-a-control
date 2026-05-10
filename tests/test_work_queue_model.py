# Work Queue Model Unit Tests

import unittest
from scripts.work_queue import (
    Queue,
    Priority,
    ExecutionContext,
    WorkItem,
)


class TestWorkItem(unittest.TestCase):
    def test_is_done_with_done_status(self):
        item = WorkItem(
            id="test-1",
            source="github",
            source_type="pr",
            source_id="1",
            title="Test PR",
            automatic_status="DONE",
        )
        self.assertTrue(item.is_done)

    def test_is_done_with_completed_status(self):
        item = WorkItem(
            id="test-2",
            source="github",
            source_type="pr",
            source_id="2",
            title="Test PR",
            automatic_status="COMPLETED",
        )
        self.assertTrue(item.is_done)

    def test_is_done_with_merged_status(self):
        item = WorkItem(
            id="test-3",
            source="github",
            source_type="pr",
            source_id="3",
            title="Test PR",
            automatic_status="MERGED",
        )
        self.assertTrue(item.is_done)

    def test_is_no_action_with_no_action_status(self):
        item = WorkItem(
            id="test-4",
            source="github",
            source_type="pr",
            source_id="4",
            title="Test PR",
            effective_status="NO_ACTION",
        )
        self.assertTrue(item.is_no_action)

    def test_is_no_action_with_ignore_status(self):
        item = WorkItem(
            id="test-5",
            source="github",
            source_type="pr",
            source_id="5",
            title="Test PR",
            effective_status="IGNORE",
        )
        self.assertTrue(item.is_no_action)

    def test_is_no_action_with_wontfix_status(self):
        item = WorkItem(
            id="test-6",
            source="github",
            source_type="issue",
            source_id="6",
            title="Test Issue",
            effective_status="WONTFIX",
        )
        self.assertTrue(item.is_no_action)

    def test_is_later_with_later_status(self):
        item = WorkItem(
            id="test-7",
            source="github",
            source_type="issue",
            source_id="7",
            title="Test Issue",
            automatic_status="LATER",
        )
        self.assertTrue(item.is_later)

    def test_is_later_with_watch_status(self):
        item = WorkItem(
            id="test-8",
            source="github",
            source_type="issue",
            source_id="8",
            title="Test Issue",
            automatic_status="WATCH",
        )
        self.assertTrue(item.is_later)

    def test_is_later_with_deferred_status(self):
        item = WorkItem(
            id="test-9",
            source="github",
            source_type="issue",
            source_id="9",
            title="Test Issue",
            automatic_status="DEFERRED",
        )
        self.assertTrue(item.is_later)

    def test_is_blocked_with_blocked_status(self):
        item = WorkItem(
            id="test-10",
            source="github",
            source_type="issue",
            source_id="10",
            title="Test Issue",
            automatic_status="BLOCKED",
        )
        self.assertTrue(item.is_blocked)

    def test_is_blocked_with_waiting_status(self):
        item = WorkItem(
            id="test-11",
            source="github",
            source_type="issue",
            source_id="11",
            title="Test Issue",
            effective_status="WAITING",
        )
        self.assertTrue(item.is_blocked)

    def test_needs_validation(self):
        item = WorkItem(
            id="test-12",
            source="github",
            source_type="pr",
            source_id="12",
            title="Test PR",
            automatic_status="NEEDS_VALIDATION",
        )
        self.assertTrue(item.needs_validation)

    def test_needs_review(self):
        item = WorkItem(
            id="test-13",
            source="github",
            source_type="pr",
            source_id="13",
            title="Test PR",
            effective_status="NEEDS_REVIEW",
        )
        self.assertTrue(item.needs_review)

    def test_is_high_priority_p0(self):
        item = WorkItem(
            id="test-14",
            source="github",
            source_type="issue",
            source_id="14",
            title="Test Issue",
            priority=Priority.P0,
        )
        self.assertTrue(item.is_high_priority)

    def test_is_high_priority_p1(self):
        item = WorkItem(
            id="test-15",
            source="github",
            source_type="issue",
            source_id="15",
            title="Test Issue",
            priority=Priority.P1,
        )
        self.assertTrue(item.is_high_priority)

    def test_is_not_high_priority_p2(self):
        item = WorkItem(
            id="test-16",
            source="github",
            source_type="issue",
            source_id="16",
            title="Test Issue",
            priority=Priority.P2,
        )
        self.assertFalse(item.is_high_priority)

    def test_upper_guards_converts_to_uppercase(self):
        item = WorkItem(
            id="test-17",
            source="github",
            source_type="issue",
            source_id="17",
            title="Test Issue",
            guards=["local_required", "Needs_Validation"],
        )
        self.assertIn("LOCAL_REQUIRED", item.upper_guards)
        self.assertIn("NEEDS_VALIDATION", item.upper_guards)


if __name__ == "__main__":
    unittest.main()
