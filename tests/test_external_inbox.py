import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import scripts.db_base as db_base
import scripts.db_state as db_state
import scripts.telegram_cli as telegram_cli
import scripts.telegram_db as telegram_db


class ExternalInboxTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.data_dir = self.root / "data"
        self.db_path = self.data_dir / "control_tower.db"

        self.original_env = {
            key: os.environ.get(key)
            for key in ("CONTROL_TOWER_DATA_DIR", "CONTROL_TOWER_DB_PATH")
        }
        os.environ["CONTROL_TOWER_DATA_DIR"] = str(self.data_dir)
        os.environ["CONTROL_TOWER_DB_PATH"] = str(self.db_path)

        self.original_paths = {
            "db_data_dir": db_base.DATA_DIR,
            "db_db_path": db_base.DB_PATH,
            "telegram_db_path": telegram_db.DB_PATH,
        }

        db_base.DATA_DIR = self.data_dir
        db_base.DB_PATH = self.db_path
        telegram_db.DB_PATH = self.db_path

        db_base.init_db()
        telegram_db.init_db()

        with db_base.connect() as conn:
            conn.execute("DELETE FROM external_inbox")
            conn.execute("DELETE FROM telegram_sources")

            conn.execute(
                """
                INSERT INTO telegram_sources (source_id, source_name, chat_class, is_core)
                VALUES (?, ?, ?, ?)
                """,
                ("s1", "Local Chat", "local_chat", 1),
            )
            conn.execute(
                """
                INSERT INTO telegram_sources (source_id, source_name, chat_class, is_core)
                VALUES (?, ?, ?, ?)
                """,
                ("s2", "Stock Channel", "stock_curator_channel", 0),
            )
            conn.execute(
                """
                INSERT INTO telegram_sources (source_id, source_name, chat_class, is_core)
                VALUES (?, ?, ?, ?)
                """,
                ("s3", "News Channel", "news_channel", 0),
            )
            conn.execute(
                """
                INSERT INTO telegram_sources (source_id, source_name, chat_class, is_core)
                VALUES (?, ?, ?, ?)
                """,
                ("s4", "General Chat", "general_chat", 0),
            )

            messages = [
                ("telegram", "s1", "Local Chat", "101", "Core 1", "2026-03-10T09:00:00Z", "2026-03-10T10:00:00Z", "new"),
                ("telegram", "s2", "Stock Channel", "102", "Stock 1", "2026-03-09T09:00:00Z", "2026-03-10T10:01:00Z", "new"),
                ("telegram", "s3", "News Channel", "103", "News 1", "2026-03-10T11:00:00Z", "2026-03-10T09:59:00Z", "new"),
                ("telegram", "s4", "General Chat", "104", "General 1", None, "2026-03-10T10:03:00Z", "new"),
            ]
            for message in messages:
                conn.execute(
                    """
                    INSERT INTO external_inbox (
                        source_type, source_id, source_name, external_message_id, raw_content, item_timestamp, imported_at, status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    message,
                )

    def tearDown(self) -> None:
        db_base.DATA_DIR = self.original_paths["db_data_dir"]
        db_base.DB_PATH = self.original_paths["db_db_path"]
        telegram_db.DB_PATH = self.original_paths["telegram_db_path"]

        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

        self.temp_dir.cleanup()

    def test_categorization(self) -> None:
        result = db_state.get_external_inbox_overview(limit=10)
        items = result["items"]
        self.assertEqual(len(items), 4)

        categories = {item["source_id"]: item["category"] for item in items}
        self.assertEqual(categories["s1"], "핵심4개")
        self.assertEqual(categories["s2"], "주식큐레이터")
        self.assertEqual(categories["s3"], "뉴스")
        self.assertEqual(categories["s4"], "일반대화")

    def test_filtering(self) -> None:
        result = db_state.get_external_inbox_overview(limit=10, category="핵심4개")
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["source_id"], "s1")

        result = db_state.get_external_inbox_overview(limit=10, category="주식큐레이터")
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["source_id"], "s2")

    def test_status_filtering(self) -> None:
        with db_base.connect() as conn:
            conn.execute("UPDATE external_inbox SET status = 'reviewing' WHERE source_id = 's1'")

        result = db_state.get_external_inbox_overview(limit=10, status="reviewing")
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["source_id"], "s1")

    def test_overview_orders_by_item_timestamp_with_imported_fallback(self) -> None:
        result = db_state.get_external_inbox_overview(limit=10)
        ordered_sources = [item["source_id"] for item in result["items"]]
        self.assertEqual(ordered_sources, ["s3", "s4", "s1", "s2"])
        self.assertIsNone(result["items"][1]["item_timestamp"])

    def test_import_chat_prefers_original_message_timestamp(self) -> None:
        payload = [
            {"id": 201, "text": "older event", "date": "2025-01-02T03:04:05Z", "sender": "Alice"},
            {"id": 202, "text": "unix event", "date": 1735790645, "sender": "Bob"},
            {"id": 203, "text": "missing date", "sender": "Carol"},
        ]

        with patch("scripts.telegram_cli.fetch_messages", return_value=payload):
            result = telegram_cli.import_chat("s1")

        self.assertTrue(result["ok"])
        with db_base.connect() as conn:
            rows = conn.execute(
                """
                SELECT external_message_id, item_timestamp, imported_at
                FROM external_inbox
                WHERE source_id = 's1' AND external_message_id IN ('201', '202', '203')
                ORDER BY CAST(external_message_id AS INTEGER) ASC
                """
            ).fetchall()

        self.assertEqual(rows[0]["item_timestamp"], "2025-01-02T03:04:05Z")
        self.assertEqual(rows[1]["item_timestamp"], "2025-01-02T04:04:05+00:00")
        self.assertEqual(rows[2]["item_timestamp"], rows[2]["imported_at"])

    def test_import_chat_can_skip_attachment_downloads_but_keep_metadata(self) -> None:
        payload = [
            {
                "id": 301,
                "text": "photo message",
                "date": "2025-01-02T03:04:05Z",
                "sender": "Alice",
                "item_type": "image",
                "attachment_path": None,
                "attachment_name": "photo.jpg",
                "mime_type": "image/jpeg",
                "file_size": 12345,
            }
        ]

        with patch("scripts.telegram_cli.fetch_messages", return_value=payload) as mocked_fetch:
            result = telegram_cli.import_chat("s1", download_attachments=False)

        self.assertTrue(result["ok"])
        mocked_fetch.assert_called_once_with("s1", limit=200, max_id=None, download_attachments=False)
        with db_base.connect() as conn:
            row = conn.execute(
                """
                SELECT item_type, attachment_path, attachment_ref, metadata_json
                FROM external_inbox
                WHERE source_id = 's1' AND external_message_id = '301'
                """
            ).fetchone()

        metadata = json.loads(row["metadata_json"])
        self.assertEqual(row["item_type"], "image")
        self.assertIsNone(row["attachment_path"])
        self.assertEqual(row["attachment_ref"], "photo.jpg")
        self.assertEqual(metadata["attachment_name"], "photo.jpg")
        self.assertEqual(metadata["mime_type"], "image/jpeg")
        self.assertEqual(metadata["file_size"], 12345)

    def test_fill_missing_attachments_only_updates_existing_missing_rows(self) -> None:
        with db_base.connect() as conn:
            conn.execute(
                """
                INSERT INTO external_inbox (
                    source_type, source_id, source_name, external_message_id,
                    author, item_type, raw_content, attachment_path, attachment_ref,
                    item_timestamp, imported_at, status, metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "telegram",
                    "s1",
                    "Local Chat",
                    "401",
                    "Alice",
                    "image",
                    "needs file",
                    None,
                    "photo.jpg",
                    "2025-01-02T03:04:05Z",
                    "2026-03-10T00:00:00Z",
                    "new",
                    json.dumps({"attachment_name": "photo.jpg"}, ensure_ascii=False),
                ),
            )

        payload = [
            {
                "id": 401,
                "text": "needs file",
                "date": "2025-01-02T03:04:05Z",
                "sender": "Alice",
                "item_type": "image",
                "attachment_path": "/tmp/photo.jpg",
                "attachment_name": "photo.jpg",
                "mime_type": "image/jpeg",
                "file_size": 12345,
            }
        ]

        with patch("scripts.telegram_cli.fetch_messages", return_value=payload) as mocked_fetch:
            result = telegram_cli.fill_missing_attachments("s1", limit=10)

        self.assertTrue(result["ok"])
        self.assertEqual(result["processed_count"], 1)
        self.assertEqual(result["remaining_missing"], 0)
        mocked_fetch.assert_called_once_with("s1", limit=1, download_attachments=True, message_ids=[401])
        with db_base.connect() as conn:
            row = conn.execute(
                """
                SELECT attachment_path, attachment_ref
                FROM external_inbox
                WHERE source_id = 's1' AND external_message_id = '401'
                """
            ).fetchone()

        self.assertEqual(row["attachment_path"], "/tmp/photo.jpg")
        self.assertEqual(row["attachment_ref"], "photo.jpg")

    def test_source_messages_default_to_today_with_previous_day_marker(self) -> None:
        with db_base.connect() as conn:
            conn.execute(
                """
                INSERT INTO external_inbox (
                    source_type, source_id, source_name, external_message_id, raw_content, item_timestamp, imported_at, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                ("telegram", "s1", "Local Chat", "105", "Yesterday", "2026-03-09T08:30:00Z", "2026-03-10T11:10:00Z", "new"),
            )

        result = db_state.get_external_inbox_source_messages("s1", day="today", limit=50)
        self.assertEqual(result["day"], "2026-03-10")
        self.assertEqual([message["external_message_id"] for message in result["messages"]], ["101"])
        self.assertEqual(result["loaded_days"], ["2026-03-10"])
        self.assertTrue(result["has_more_before"])
        self.assertEqual(result["previous_day"], "2026-03-09")

    def test_source_messages_can_load_previous_day_by_before_marker(self) -> None:
        with db_base.connect() as conn:
            conn.execute(
                """
                INSERT INTO external_inbox (
                    source_type, source_id, source_name, external_message_id, raw_content, item_timestamp, imported_at, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                ("telegram", "s1", "Local Chat", "105", "Yesterday early", "2026-03-09T08:30:00Z", "2026-03-10T11:10:00Z", "new"),
            )
            conn.execute(
                """
                INSERT INTO external_inbox (
                    source_type, source_id, source_name, external_message_id, raw_content, item_timestamp, imported_at, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                ("telegram", "s1", "Local Chat", "106", "Older day", "2026-03-08T08:30:00Z", "2026-03-10T11:11:00Z", "new"),
            )

        result = db_state.get_external_inbox_source_messages("s1", before="2026-03-10", limit=50)
        self.assertEqual(result["day"], "2026-03-09")
        self.assertEqual([message["external_message_id"] for message in result["messages"]], ["105"])
        self.assertTrue(result["has_more_before"])
        self.assertEqual(result["previous_day"], "2026-03-08")

    def test_source_messages_use_imported_at_fallback_for_day_bucket(self) -> None:
        result = db_state.get_external_inbox_source_messages("s4", day="today", limit=50)
        self.assertEqual(result["day"], "2026-03-10")
        self.assertEqual(len(result["messages"]), 1)
        self.assertEqual(result["messages"][0]["external_message_id"], "104")
        self.assertEqual(result["messages"][0]["display_day"], "2026-03-10")


if __name__ == "__main__":
    unittest.main()
