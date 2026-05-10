# Work Queue Sorting and Helpers Unit Tests

import unittest
from scripts.work_queue import (
    Queue,
    Priority,
    WorkItem,
    sort_work_items,
    group_by_queue,
    get_now_items,
    get_local_needed_items,
    get_blocked_items,
    get_validation_needed_items,
)


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