import sys
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts import manual_overrides


class ManualOverridesTests(unittest.TestCase):
    def test_create_and_list_manual_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "ops_overrides.json"
            created = manual_overrides.create_manual_override(
                {
                    "target_type": "issue",
                    "target_id": "31",
                    "manual_status": "PINNED",
                    "reason": "Needs to stay visible during queue planning.",
                    "priority": "P1",
                    "created_by": "test",
                },
                path=store,
            )
            records = manual_overrides.list_manual_overrides(path=store)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], created["id"])
        self.assertEqual(records[0]["target_type"], "issue")
        self.assertEqual(records[0]["manual_status"], "PINNED")
        self.assertTrue(records[0]["is_active"])

    def test_create_requires_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "ops_overrides.json"
            with self.assertRaisesRegex(ValueError, "reason is required"):
                manual_overrides.create_manual_override(
                    {
                        "target_type": "issue",
                        "target_id": "31",
                        "manual_status": "WATCH",
                        "reason": "",
                    },
                    path=store,
                )

    def test_update_and_deactivate_manual_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "ops_overrides.json"
            created = manual_overrides.create_manual_override(
                {
                    "target_type": "pr",
                    "target_id": "51",
                    "manual_status": "WATCH",
                    "reason": "Awaiting local verification.",
                },
                path=store,
            )
            updated = manual_overrides.update_manual_override(
                created["id"],
                {"manual_status": "NEEDS_VALIDATION", "reason": "Route smoke required."},
                path=store,
            )
            deactivated = manual_overrides.deactivate_manual_override(created["id"], path=store)
            active_records = manual_overrides.list_manual_overrides(path=store)
            all_records = manual_overrides.list_manual_overrides(path=store, include_inactive=True)

        self.assertEqual(updated["manual_status"], "NEEDS_VALIDATION")
        self.assertEqual(updated["reason"], "Route smoke required.")
        self.assertFalse(deactivated["is_active"])
        self.assertEqual(active_records, [])
        self.assertEqual(len(all_records), 1)

    def test_filter_by_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "ops_overrides.json"
            manual_overrides.create_manual_override(
                {
                    "target_type": "issue",
                    "target_id": "31",
                    "manual_status": "WATCH",
                    "reason": "Observe issue.",
                },
                path=store,
            )
            manual_overrides.create_manual_override(
                {
                    "target_type": "pr",
                    "target_id": "51",
                    "manual_status": "DO_NOT_MERGE",
                    "reason": "Clean diff required.",
                },
                path=store,
            )
            records = manual_overrides.list_manual_overrides(path=store, target_type="pr")

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["target_id"], "51")
        self.assertEqual(records[0]["manual_status"], "DO_NOT_MERGE")

    def test_rejects_invalid_status_and_priority(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "ops_overrides.json"
            with self.assertRaisesRegex(ValueError, "manual_status is invalid"):
                manual_overrides.create_manual_override(
                    {
                        "target_type": "issue",
                        "target_id": "1",
                        "manual_status": "INVALID",
                        "reason": "bad status",
                    },
                    path=store,
                )
            with self.assertRaisesRegex(ValueError, "priority is invalid"):
                manual_overrides.create_manual_override(
                    {
                        "target_type": "issue",
                        "target_id": "1",
                        "manual_status": "WATCH",
                        "reason": "bad priority",
                        "priority": "P9",
                    },
                    path=store,
                )

    def test_stale_detection(self):
        now = datetime(2026, 5, 9, tzinfo=timezone.utc)
        stale_by_age = {
            "updated_at": (now - timedelta(days=15)).isoformat().replace("+00:00", "Z"),
            "expires_at": "",
        }
        fresh = {
            "updated_at": (now - timedelta(days=2)).isoformat().replace("+00:00", "Z"),
            "expires_at": "",
        }
        expired = {
            "updated_at": (now - timedelta(days=1)).isoformat().replace("+00:00", "Z"),
            "expires_at": (now - timedelta(days=1)).isoformat().replace("+00:00", "Z"),
        }

        self.assertTrue(manual_overrides.is_stale_manual_override(stale_by_age, now=now))
        self.assertFalse(manual_overrides.is_stale_manual_override(fresh, now=now))
        self.assertTrue(manual_overrides.is_stale_manual_override(expired, now=now))


if __name__ == "__main__":
    unittest.main()
