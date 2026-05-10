# Work Queue Core Assignment Unit Tests
# Steps 1-3 from docs/20-work-queue-priority-board.md implementation order

import unittest
from scripts.work_queue import (
    Queue,
    Priority,
    ExecutionContext,
    WorkItem,
    normalize_work_item,
    assign_queue_priority,
    sort_work_items,
    normalize_work_items,
    group_by_queue,
    get_now_items,
    get_local_needed_items,
    get_blocked_items,
    get_validation_needed_items,
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

    def test_is_done_with_no_action_status(self):
        item = WorkItem(
            id="test-2",
            source="github",
            source_type="pr",
            source_id="2",
            title="Test PR",
            effective_status="NO_ACTION",
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

    def test_is_blocked_with_blocked_status(self):
        item = WorkItem(
            id="test-4",
            source="github",
            source_type="issue",
            source_id="4",
            title="Test Issue",
            automatic_status="BLOCKED",
        )
        self.assertTrue(item.is_blocked)

    def test_is_blocked_with_waiting_status(self):
        item = WorkItem(
            id="test-5",
            source="github",
            source_type="issue",
            source_id="5",
            title="Test Issue",
            effective_status="WAITING",
        )
        self.assertTrue(item.is_blocked)

    def test_needs_validation(self):
        item = WorkItem(
            id="test-6",
            source="github",
            source_type="pr",
            source_id="6",
            title="Test PR",
            automatic_status="NEEDS_VALIDATION",
        )
        self.assertTrue(item.needs_validation)

    def test_needs_review(self):
        item = WorkItem(
            id="test-7",
            source="github",
            source_type="pr",
            source_id="7",
            title="Test PR",
            effective_status="NEEDS_REVIEW",
        )
        self.assertTrue(item.needs_review)

    def test_is_high_priority_p0(self):
        item = WorkItem(
            id="test-8",
            source="github",
            source_type="issue",
            source_id="8",
            title="Test Issue",
            priority=Priority.P0,
        )
        self.assertTrue(item.is_high_priority)

    def test_is_high_priority_p1(self):
        item = WorkItem(
            id="test-9",
            source="github",
            source_type="issue",
            source_id="9",
            title="Test Issue",
            priority=Priority.P1,
        )
        self.assertTrue(item.is_high_priority)

    def test_is_not_high_priority_p2(self):
        item = WorkItem(
            id="test-10",
            source="github",
            source_type="issue",
            source_id="10",
            title="Test Issue",
            priority=Priority.P2,
        )
        self.assertFalse(item.is_high_priority)


class TestNormalizeWorkItem(unittest.TestCase):
    def test_basic_normalization(self):
        raw = {
            "id": "github-pr-1",
            "source": "github",
            "source_type": "pr",
            "source_id": "1",
            "title": "feat: add feature",
            "automatic_status": "IN_PROGRESS",
            "updated_at": "2026-05-10T02:00:00Z",
        }
        item = normalize_work_item(raw)
        self.assertIsNotNone(item)
        self.assertEqual(item.id, "github-pr-1")
        self.assertEqual(item.source, "github")
        self.assertEqual(item.title, "feat: add feature")
        self.assertEqual(item.automatic_status, "IN_PROGRESS")

    def test_missing_id_returns_none(self):
        raw = {"title": "No ID item"}
        item = normalize_work_item(raw)
        self.assertIsNone(item)

    def test_empty_dict_returns_none(self):
        item = normalize_work_item({})
        self.assertIsNone(item)

    def test_none_input_returns_none(self):
        item = normalize_work_item(None)
        self.assertIsNone(item)

    def test_guards_parsed_from_string(self):
        raw = {
            "id": "test-1",
            "title": "Test",
            "source": "github",
            "source_type": "issue",
            "source_id": "1",
            "guards": "LOCAL_REQUIRED, VALIDATION_NEEDED",
        }
        item = normalize_work_item(raw)
        self.assertIsNotNone(item)
        self.assertIn("LOCAL_REQUIRED", item.guards)
        self.assertIn("VALIDATION_NEEDED", item.guards)


class TestAssignQueuePriority(unittest.TestCase):
    def test_done_item_no_action(self):
        item = WorkItem(
            id="done-1",
            source="github",
            source_type="pr",
            source_id="1",
            title="Done PR",
            automatic_status="DONE",
        )
        queue, priority, ctx = assign_queue_priority(item)
        self.assertEqual(queue, Queue.NO_ACTION)
        self.assertEqual(priority, Priority.P3)

    def test_blocked_item_blocked_queue(self):
        item = WorkItem(
            id="blocked-1",
            source="github",
            source_type="issue",
            source_id="1",
            title="Blocked Issue",
            automatic_status="BLOCKED",
        )
        queue, priority, ctx = assign_queue_priority(item)
        self.assertEqual(queue, Queue.BLOCKED)

    def test_local_needed_flag(self):
        item = WorkItem(
            id="local-1",
            source="github",
            source_type="pr",
            source_id="1",
            title="Local PR",
            automatic_status="IN_PROGRESS",
            is_local_needed=True,
        )
        queue, priority, ctx = assign_queue_priority(item)
        self.assertEqual(queue, Queue.LOCAL_NEEDED)
        self.assertEqual(ctx, ExecutionContext.LOCAL_NEEDED)

    def test_local_guard(self):
        item = WorkItem(
            id="local-guard-1",
            source="github",
            source_type="pr",
            source_id="1",
            title="Local Guard PR",
            automatic_status="IN_PROGRESS",
            guards=["LOCAL_REQUIRED"],
        )
        queue, priority, ctx = assign_queue_priority(item)
        self.assertEqual(queue, Queue.LOCAL_NEEDED)

    def test_validation_needed_status(self):
        item = WorkItem(
            id="val-1",
            source="github",
            source_type="pr",
            source_id="1",
            title="Validation PR",
            automatic_status="NEEDS_VALIDATION",
        )
        queue, priority, ctx = assign_queue_priority(item)
        self.assertEqual(queue, Queue.VALIDATION_NEEDED)
        self.assertEqual(ctx, ExecutionContext.LOCAL_NEEDED)

    def test_review_needed_status(self):
        item = WorkItem(
            id="review-1",
            source="github",
            source_type="pr",
            source_id="1",
            title="Review PR",
            effective_status="NEEDS_REVIEW",
        )
        queue, priority, ctx = assign_queue_priority(item)
        self.assertEqual(queue, Queue.REVIEW_NEEDED)

    def test_p0_high_priority_now(self):
        item = WorkItem(
            id="p0-1",
            source="github",
            source_type="issue",
            source_id="1",
            title="P0 Issue",
            automatic_status="IN_PROGRESS",
            priority=Priority.P0,
        )
        queue, priority, ctx = assign_queue_priority(item)
        self.assertEqual(queue, Queue.NOW)
        self.assertEqual(priority, Priority.P1)

    def test_p1_high_priority_now(self):
        item = WorkItem(
            id="p1-1",
            source="github",
            source_type="issue",
            source_id="1",
            title="P1 Issue",
            automatic_status="IN_PROGRESS",
            priority=Priority.P1,
        )
        queue, priority, ctx = assign_queue_priority(item)
        self.assertEqual(queue, Queue.NOW)

    def test_p2_regular_priority_next(self):
        item = WorkItem(
            id="p2-1",
            source="github",
            source_type="issue",
            source_id="1",
            title="P2 Issue",
            automatic_status="IN_PROGRESS",
            priority=Priority.P2,
        )
        queue, priority, ctx = assign_queue_priority(item)
        self.assertEqual(queue, Queue.NEXT)


class TestSortWorkItems(unittest.TestCase):
    def test_stable_sort_same_input(self):
        items = [
            WorkItem(id="a", source="github", source_type="pr", source_id="1", title="A"),
            WorkItem(id="b", source="github", source_type="pr", source_id="2", title="B"),
            WorkItem(id="c", source="github", source_type="pr", source_id="3", title="C"),
        ]
        sorted_items = sort_work_items(items)
        ids = [i.id for i in sorted_items]
        self.assertEqual(ids, ["a", "b", "c"])

    def test_queue_priority_order(self):
        items = [
            WorkItem(
                id="later",
                source="github",
                source_type="issue",
                source_id="1",
                title="Later",
                priority=Priority.P3,
            ),
            WorkItem(
                id="now",
                source="github",
                source_type="issue",
                source_id="2",
                title="Now",
                priority=Priority.P0,
            ),
            WorkItem(
                id="next",
                source="github",
                source_type="issue",
                source_id="3",
                title="Next",
                priority=Priority.P2,
            ),
        ]
        items[0].queue = Queue.LATER
        items[1].queue = Queue.NOW
        items[2].queue = Queue.NEXT

        sorted_items = sort_work_items(items)
        ids = [i.id for i in sorted_items]
        self.assertEqual(ids, ["now", "next", "later"])


class TestNormalizeWorkItems(unittest.TestCase):
    def test_filters_none_items(self):
        raw_items = [
            {"id": "1", "title": "Item 1", "source": "github", "source_type": "pr", "source_id": "1"},
            {"title": "No ID"},
            {"id": "2", "title": "Item 2", "source": "github", "source_type": "pr", "source_id": "2"},
        ]
        normalized = normalize_work_items(raw_items)
        self.assertEqual(len(normalized), 2)


class TestGroupByQueue(unittest.TestCase):
    def test_groups_by_queue(self):
        items = [
            WorkItem(id="1", source="gh", source_type="pr", source_id="1", title="1", queue=Queue.NOW),
            WorkItem(id="2", source="gh", source_type="pr", source_id="2", title="2", queue=Queue.NOW),
            WorkItem(id="3", source="gh", source_type="pr", source_id="3", title="3", queue=Queue.NEXT),
        ]
        groups = group_by_queue(items)
        self.assertEqual(len(groups[Queue.NOW]), 2)
        self.assertEqual(len(groups[Queue.NEXT]), 1)
        self.assertEqual(len(groups[Queue.BLOCKED]), 0)


class TestQueueHelpers(unittest.TestCase):
    def test_get_now_items_limits_to_3(self):
        items = [
            WorkItem(id=str(i), source="gh", source_type="pr", source_id=str(i), title=str(i), queue=Queue.NOW)
            for i in range(5)
        ]
        now_items = get_now_items(items)
        self.assertEqual(len(now_items), 3)

    def test_get_local_needed_items(self):
        items = [
            WorkItem(id="1", source="gh", source_type="pr", source_id="1", title="1", queue=Queue.LOCAL_NEEDED),
            WorkItem(id="2", source="gh", source_type="pr", source_id="2", title="2", queue=Queue.NEXT),
        ]
        local_items = get_local_needed_items(items)
        self.assertEqual(len(local_items), 1)
        self.assertEqual(local_items[0].id, "1")

    def test_get_blocked_items(self):
        items = [
            WorkItem(id="1", source="gh", source_type="pr", source_id="1", title="1", queue=Queue.BLOCKED),
            WorkItem(id="2", source="gh", source_type="pr", source_id="2", title="2", queue=Queue.NEXT),
        ]
        blocked_items = get_blocked_items(items)
        self.assertEqual(len(blocked_items), 1)
        self.assertEqual(blocked_items[0].id, "1")

    def test_get_validation_needed_items(self):
        items = [
            WorkItem(id="1", source="gh", source_type="pr", source_id="1", title="1", queue=Queue.VALIDATION_NEEDED),
            WorkItem(id="2", source="gh", source_type="pr", source_id="2", title="2", queue=Queue.NEXT),
        ]
        val_items = get_validation_needed_items(items)
        self.assertEqual(len(val_items), 1)
        self.assertEqual(val_items[0].id, "1")


if __name__ == "__main__":
    unittest.main()