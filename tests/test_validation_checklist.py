"""Tests for validation_checklist module."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.validation_checklist import (
    STORAGE_REL,
    _read_all,
    _write_all,
    _now_iso,
    create_checklist,
    list_checklists,
    get_checklist,
    update_result_item,
    recompute_overall_status,
)


class TestValidationChecklist(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.fake_storage = self.tmp / STORAGE_REL
        # Patch _storage_path() to return our temp path
        self._patcher = patch("scripts.validation_checklist._storage_path", return_value=self.fake_storage)
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()
        # Clean up temp dir
        for root, dirs, files in os.walk(self.tmp, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.tmp)

    # ---- create_checklist ----

    def test_create_checklist_returns_checklist_with_id(self):
        result = create_checklist({"target_type": "pr", "target_id": "42"})
        self.assertIn("id", result)
        self.assertEqual(result["target_type"], "pr")
        self.assertEqual(result["target_id"], "42")
        self.assertIn("created_at", result)
        self.assertIn("updated_at", result)

    def test_create_checklist_has_items(self):
        result = create_checklist({"target_type": "pr", "target_id": "42"})
        self.assertIn("items", result)
        self.assertGreater(len(result["items"]), 0)
        expected_keys = {"unit_test", "api_smoke", "manual_review"}
        actual_keys = {i["key"] for i in result["items"]}
        self.assertEqual(actual_keys, expected_keys)

    def test_create_checklist_default_items_by_type(self):
        docs = create_checklist({"target_type": "docs", "target_id": "1"})
        docs_keys = {i["key"] for i in docs["items"]}
        self.assertEqual(docs_keys, {"docs_review", "manual_review"})

    def test_create_checklist_with_custom_required_items(self):
        result = create_checklist({
            "target_type": "pr",
            "target_id": "7",
            "required_items": ["lint", "unit_test"],
        })
        keys = {i["key"] for i in result["items"]}
        self.assertEqual(keys, {"lint", "unit_test"})

    def test_create_checklist_raises_on_missing_fields(self):
        with self.assertRaises(ValueError):
            create_checklist({"target_type": "", "target_id": ""})

    def test_create_checklist_stores_persistently(self):
        c1 = create_checklist({"target_type": "pr", "target_id": "1"})
        c2 = create_checklist({"target_type": "pr", "target_id": "2"})
        all_c = list_checklists()
        self.assertEqual(len(all_c), 2)
        ids = {c["id"] for c in all_c}
        self.assertIn(c1["id"], ids)
        self.assertIn(c2["id"], ids)

    # ---- list_checklists ----

    def test_list_checklists_empty_when_no_data(self):
        result = list_checklists()
        self.assertEqual(result, [])

    def test_list_checklists_returns_all(self):
        create_checklist({"target_type": "issue", "target_id": "1"})
        create_checklist({"target_type": "issue", "target_id": "2"})
        result = list_checklists()
        self.assertEqual(len(result), 2)

    # ---- get_checklist ----

    def test_get_checklist_returns_none_for_missing(self):
        result = get_checklist("nonexistent")
        self.assertIsNone(result)

    def test_get_checklist_returns_checklist(self):
        created = create_checklist({"target_type": "plan", "target_id": "p1"})
        fetched = get_checklist(created["id"])
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["id"], created["id"])

    # ---- update_result_item ----

    def test_update_result_item_updates_status(self):
        created = create_checklist({"target_type": "pr", "target_id": "1"})
        item_key = created["items"][0]["key"]
        result = update_result_item(created["id"], item_key, {"status": "passed"})
        updated_item = next(i for i in result["items"] if i["key"] == item_key)
        self.assertEqual(updated_item["status"], "passed")

    def test_update_result_item_sets_run_at_for_passed(self):
        created = create_checklist({"target_type": "pr", "target_id": "1"})
        item_key = created["items"][0]["key"]
        result = update_result_item(created["id"], item_key, {"status": "passed"})
        updated_item = next(i for i in result["items"] if i["key"] == item_key)
        self.assertIsNotNone(updated_item["run_at"])

    def test_update_result_item_sets_run_at_for_failed(self):
        created = create_checklist({"target_type": "pr", "target_id": "1"})
        item_key = created["items"][0]["key"]
        result = update_result_item(created["id"], item_key, {"status": "failed", "summary": "test failure"})
        updated_item = next(i for i in result["items"] if i["key"] == item_key)
        self.assertIsNotNone(updated_item["run_at"])

    def test_update_result_item_updates_summary(self):
        created = create_checklist({"target_type": "pr", "target_id": "1"})
        item_key = created["items"][0]["key"]
        result = update_result_item(created["id"], item_key, {"summary": "all good"})
        updated_item = next(i for i in result["items"] if i["key"] == item_key)
        self.assertEqual(updated_item["summary"], "all good")

    def test_update_result_item_updates_command(self):
        created = create_checklist({"target_type": "pr", "target_id": "1"})
        item_key = created["items"][0]["key"]
        result = update_result_item(created["id"], item_key, {"command": "pytest"})
        updated_item = next(i for i in result["items"] if i["key"] == item_key)
        self.assertEqual(updated_item["command"], "pytest")

    def test_update_result_item_raises_on_bad_id(self):
        with self.assertRaises(ValueError):
            update_result_item("bad-id", "unit_test", {"status": "passed"})

    def test_update_result_item_raises_on_bad_key(self):
        created = create_checklist({"target_type": "pr", "target_id": "1"})
        with self.assertRaises(ValueError):
            update_result_item(created["id"], "nonexistent_key", {"status": "passed"})

    def test_update_result_item_recomputes_overall(self):
        created = create_checklist({"target_type": "pr", "target_id": "1"})
        # Initially all not_started → overall not_started
        self.assertEqual(created["overall_status"], "not_started")
        # Pass all items
        for item in created["items"]:
            update_result_item(created["id"], item["key"], {"status": "passed"})
        final = get_checklist(created["id"])
        self.assertEqual(final["overall_status"], "passed")

    # ---- recompute_overall_status ----

    def test_recompute_all_passed(self):
        status = recompute_overall_status({
            "items": [
                {"key": "a", "status": "passed"},
                {"key": "b", "status": "not_applicable"},
            ]
        })
        self.assertEqual(status, "passed")

    def test_recompute_any_failed(self):
        status = recompute_overall_status({
            "items": [
                {"key": "a", "status": "passed"},
                {"key": "b", "status": "failed"},
            ]
        })
        self.assertEqual(status, "failed")

    def test_recompute_any_blocked(self):
        status = recompute_overall_status({
            "items": [
                {"key": "a", "status": "passed"},
                {"key": "b", "status": "blocked"},
            ]
        })
        self.assertEqual(status, "blocked")

    def test_recompute_any_not_started(self):
        status = recompute_overall_status({
            "items": [
                {"key": "a", "status": "passed"},
                {"key": "b", "status": "not_started"},
            ]
        })
        self.assertEqual(status, "not_started")

    def test_recompute_all_skipped(self):
        status = recompute_overall_status({
            "items": [
                {"key": "a", "status": "skipped"},
                {"key": "b", "status": "skipped"},
            ]
        })
        self.assertEqual(status, "skipped")

    def test_recompute_empty_items(self):
        status = recompute_overall_status({"items": []})
        self.assertEqual(status, "not_started")

    def test_update_result_item_updated_at_changes(self):
        created = create_checklist({"target_type": "pr", "target_id": "1"})
        original_updated = created["updated_at"]
        item_key = created["items"][0]["key"]
        result = update_result_item(created["id"], item_key, {"status": "passed"})
        self.assertNotEqual(result["updated_at"], original_updated)

    def test_storage_file_created(self):
        create_checklist({"target_type": "pr", "target_id": "1"})
        self.assertTrue(self.fake_storage.exists())
        data = json.loads(self.fake_storage.read_text(encoding="utf-8"))
        self.assertEqual(len(data), 1)


if __name__ == "__main__":
    unittest.main()
