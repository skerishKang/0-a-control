# Work Queue Assignment Unit Tests

import unittest
from scripts.work_queue import (
    Queue,
    Priority,
    ExecutionContext,
    WorkItem,
    assign_queue_priority,
)


class TestAssignQueuePriority(unittest.TestCase):
    def test_done_item_done_queue(self):
        item = WorkItem(
            id="done-1",
            source="github",
            source_type="pr",
            source_id="1",
            title="Done PR",
            automatic_status="DONE",
        )
        queue, priority, ctx = assign_queue_priority(item)
        self.assertEqual(queue, Queue.DONE)
        self.assertEqual(priority, Priority.P3)

    def test_completed_item_done_queue(self):
        item = WorkItem(
            id="completed-1",
            source="github",
            source_type="pr",
            source_id="1",
            title="Completed PR",
            automatic_status="COMPLETED",
        )
        queue, priority, ctx = assign_queue_priority(item)
        self.assertEqual(queue, Queue.DONE)

    def test_no_action_item_no_action_queue(self):
        item = WorkItem(
            id="noaction-1",
            source="github",
            source_type="issue",
            source_id="1",
            title="Wontfix Issue",
            automatic_status="NO_ACTION",
        )
        queue, priority, ctx = assign_queue_priority(item)
        self.assertEqual(queue, Queue.NO_ACTION)

    def test_ignore_item_no_action_queue(self):
        item = WorkItem(
            id="ignore-1",
            source="github",
            source_type="issue",
            source_id="1",
            title="Ignored Issue",
            automatic_status="IGNORE",
        )
        queue, priority, ctx = assign_queue_priority(item)
        self.assertEqual(queue, Queue.NO_ACTION)

    def test_later_item_later_queue(self):
        item = WorkItem(
            id="later-1",
            source="github",
            source_type="issue",
            source_id="1",
            title="Later Issue",
            automatic_status="LATER",
        )
        queue, priority, ctx = assign_queue_priority(item)
        self.assertEqual(queue, Queue.LATER)
        self.assertEqual(priority, Priority.P3)

    def test_watch_item_later_queue(self):
        item = WorkItem(
            id="watch-1",
            source="github",
            source_type="issue",
            source_id="1",
            title="Watch Issue",
            automatic_status="WATCH",
        )
        queue, priority, ctx = assign_queue_priority(item)
        self.assertEqual(queue, Queue.LATER)

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
        self.assertEqual(ctx, ExecutionContext.LOCAL_NEEDED)

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

    def test_p0_high_priority_now_preserved(self):
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
        self.assertEqual(priority, Priority.P0)

    def test_p1_high_priority_now_preserved(self):
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
        self.assertEqual(priority, Priority.P1)

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
        self.assertEqual(priority, Priority.P2)

    def test_github_web_guard_returns_github_web_context(self):
        item = WorkItem(
            id="web-1",
            source="github",
            source_type="issue",
            source_id="1",
            title="Web Model Issue",
            automatic_status="IN_PROGRESS",
            guards=["GITHUB_WEB_MODEL_NEEDED"],
        )
        queue, priority, ctx = assign_queue_priority(item)
        self.assertEqual(ctx, ExecutionContext.GITHUB_WEB_MODEL_NEEDED)

    def test_mixed_guard_returns_mixed_context(self):
        item = WorkItem(
            id="mixed-1",
            source="github",
            source_type="issue",
            source_id="1",
            title="Mixed Issue",
            automatic_status="IN_PROGRESS",
            guards=["MIXED_REMOTE_CODE_LOCAL_VALIDATION"],
        )
        queue, priority, ctx = assign_queue_priority(item)
        self.assertEqual(ctx, ExecutionContext.MIXED_REMOTE_CODE_LOCAL_VALIDATION)

    def test_local_guard_returns_local_context(self):
        item = WorkItem(
            id="local-ctx-1",
            source="github",
            source_type="issue",
            source_id="1",
            title="Local Issue",
            automatic_status="IN_PROGRESS",
            guards=["LOCAL_REQUIRED"],
        )
        queue, priority, ctx = assign_queue_priority(item)
        self.assertEqual(ctx, ExecutionContext.LOCAL_NEEDED)

    def test_default_context_is_remote_doable(self):
        item = WorkItem(
            id="default-1",
            source="github",
            source_type="issue",
            source_id="1",
            title="Default Issue",
            automatic_status="IN_PROGRESS",
            priority=Priority.P2,
        )
        queue, priority, ctx = assign_queue_priority(item)
        self.assertEqual(ctx, ExecutionContext.REMOTE_DOABLE)


class TestAllQueueValues(unittest.TestCase):
    def test_queue_now(self):
        item = WorkItem(
            id="q-now",
            source="github",
            source_type="issue",
            source_id="1",
            title="Now Issue",
            priority=Priority.P0,
        )
        queue, _, _ = assign_queue_priority(item)
        self.assertEqual(queue, Queue.NOW)

    def test_queue_next(self):
        item = WorkItem(
            id="q-next",
            source="github",
            source_type="issue",
            source_id="1",
            title="Next Issue",
            automatic_status="IN_PROGRESS",
            priority=Priority.P2,
        )
        queue, _, _ = assign_queue_priority(item)
        self.assertEqual(queue, Queue.NEXT)

    def test_queue_blocked(self):
        item = WorkItem(
            id="q-blocked",
            source="github",
            source_type="issue",
            source_id="1",
            title="Blocked Issue",
            automatic_status="BLOCKED",
        )
        queue, _, _ = assign_queue_priority(item)
        self.assertEqual(queue, Queue.BLOCKED)

    def test_queue_local_needed(self):
        item = WorkItem(
            id="q-local",
            source="github",
            source_type="pr",
            source_id="1",
            title="Local PR",
            automatic_status="IN_PROGRESS",
            is_local_needed=True,
        )
        queue, _, _ = assign_queue_priority(item)
        self.assertEqual(queue, Queue.LOCAL_NEEDED)

    def test_queue_validation_needed(self):
        item = WorkItem(
            id="q-val",
            source="github",
            source_type="pr",
            source_id="1",
            title="Validation PR",
            automatic_status="NEEDS_VALIDATION",
        )
        queue, _, _ = assign_queue_priority(item)
        self.assertEqual(queue, Queue.VALIDATION_NEEDED)

    def test_queue_review_needed(self):
        item = WorkItem(
            id="q-review",
            source="github",
            source_type="pr",
            source_id="1",
            title="Review PR",
            effective_status="NEEDS_REVIEW",
        )
        queue, _, _ = assign_queue_priority(item)
        self.assertEqual(queue, Queue.REVIEW_NEEDED)

    def test_queue_later(self):
        item = WorkItem(
            id="q-later",
            source="github",
            source_type="issue",
            source_id="1",
            title="Later Issue",
            automatic_status="LATER",
        )
        queue, _, _ = assign_queue_priority(item)
        self.assertEqual(queue, Queue.LATER)

    def test_queue_done(self):
        item = WorkItem(
            id="q-done",
            source="github",
            source_type="pr",
            source_id="1",
            title="Done PR",
            automatic_status="DONE",
        )
        queue, _, _ = assign_queue_priority(item)
        self.assertEqual(queue, Queue.DONE)

    def test_queue_no_action(self):
        item = WorkItem(
            id="q-noaction",
            source="github",
            source_type="issue",
            source_id="1",
            title="NoAction Issue",
            automatic_status="NO_ACTION",
        )
        queue, _, _ = assign_queue_priority(item)
        self.assertEqual(queue, Queue.NO_ACTION)


class TestAllExecutionContextValues(unittest.TestCase):
    def test_context_remote_doable(self):
        item = WorkItem(
            id="ctx-remote",
            source="github",
            source_type="issue",
            source_id="1",
            title="Remote Issue",
            automatic_status="IN_PROGRESS",
            priority=Priority.P2,
        )
        _, _, ctx = assign_queue_priority(item)
        self.assertEqual(ctx, ExecutionContext.REMOTE_DOABLE)

    def test_context_local_needed(self):
        item = WorkItem(
            id="ctx-local",
            source="github",
            source_type="issue",
            source_id="1",
            title="Local Issue",
            automatic_status="IN_PROGRESS",
            guards=["LOCAL_REQUIRED"],
        )
        _, _, ctx = assign_queue_priority(item)
        self.assertEqual(ctx, ExecutionContext.LOCAL_NEEDED)

    def test_context_github_web_model_needed(self):
        item = WorkItem(
            id="ctx-web",
            source="github",
            source_type="issue",
            source_id="1",
            title="Web Issue",
            automatic_status="IN_PROGRESS",
            guards=["GITHUB_WEB_MODEL_NEEDED"],
        )
        _, _, ctx = assign_queue_priority(item)
        self.assertEqual(ctx, ExecutionContext.GITHUB_WEB_MODEL_NEEDED)

    def test_context_mixed_remote_code_local_validation(self):
        item = WorkItem(
            id="ctx-mixed",
            source="github",
            source_type="issue",
            source_id="1",
            title="Mixed Issue",
            automatic_status="IN_PROGRESS",
            guards=["MIXED_REMOTE_CODE_LOCAL_VALIDATION"],
        )
        _, _, ctx = assign_queue_priority(item)
        self.assertEqual(ctx, ExecutionContext.MIXED_REMOTE_CODE_LOCAL_VALIDATION)


if __name__ == "__main__":
    unittest.main()
