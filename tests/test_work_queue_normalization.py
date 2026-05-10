# Work Queue Normalization Unit Tests

import unittest
from scripts.work_queue import (
    Queue,
    Priority,
    WorkItem,
    normalize_work_item,
    normalize_work_items,
)


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

    def test_priority_parsed_from_raw_p0(self):
        raw = {
            "id": "test-priority",
            "title": "Test",
            "source": "github",
            "source_type": "issue",
            "source_id": "1",
            "priority": "P0",
        }
        item = normalize_work_item(raw)
        self.assertIsNotNone(item)
        self.assertEqual(item.priority, Priority.P0)

    def test_priority_parsed_from_raw_lowercase(self):
        raw = {
            "id": "test-priority",
            "title": "Test",
            "source": "github",
            "source_type": "issue",
            "source_id": "1",
            "priority": "p1",
        }
        item = normalize_work_item(raw)
        self.assertIsNotNone(item)
        self.assertEqual(item.priority, Priority.P1)

    def test_priority_parsed_from_raw_mixed_case(self):
        raw = {
            "id": "test-priority",
            "title": "Test",
            "source": "github",
            "source_type": "issue",
            "source_id": "1",
            "priority": "p2",
        }
        item = normalize_work_item(raw)
        self.assertIsNotNone(item)
        self.assertEqual(item.priority, Priority.P2)

    def test_priority_default_to_p2_for_unknown(self):
        raw = {
            "id": "test-priority",
            "title": "Test",
            "source": "github",
            "source_type": "issue",
            "source_id": "1",
            "priority": "INVALID",
        }
        item = normalize_work_item(raw)
        self.assertIsNotNone(item)
        self.assertEqual(item.priority, Priority.P2)

    def test_priority_default_to_p2_for_missing(self):
        raw = {
            "id": "test-priority",
            "title": "Test",
            "source": "github",
            "source_type": "issue",
            "source_id": "1",
        }
        item = normalize_work_item(raw)
        self.assertIsNotNone(item)
        self.assertEqual(item.priority, Priority.P2)

    def test_lowercase_guards_matched_case_insensitive(self):
        raw = {
            "id": "test-guard-case",
            "title": "Test",
            "source": "github",
            "source_type": "issue",
            "source_id": "1",
            "guards": ["local_required", "needs_review"],
        }
        item = normalize_work_item(raw)
        self.assertIsNotNone(item)
        self.assertIn("local_required", item.guards)
        self.assertTrue(item.needs_review)


class TestNormalizeWorkItems(unittest.TestCase):
    def test_filters_none_items(self):
        raw_items = [
            {"id": "1", "title": "Item 1", "source": "github", "source_type": "pr", "source_id": "1"},
            {"title": "No ID"},
            {"id": "2", "title": "Item 2", "source": "github", "source_type": "pr", "source_id": "2"},
        ]
        normalized = normalize_work_items(raw_items)
        self.assertEqual(len(normalized), 2)


if __name__ == "__main__":
    unittest.main()