from scripts.db_base import connect
import json

QUEST_ID = "16161e10-b254-4183-8613-09777c97eccc"

with connect() as conn:
    row = conn.execute(
        "SELECT id, title, status, verdict_reason, restart_point, next_quest_hint, metadata_json FROM quests WHERE id = ?",
        (QUEST_ID,),
    ).fetchone()
    data = dict(row) if row else None
    if data and data.get("metadata_json"):
        data["metadata_json"] = json.loads(data["metadata_json"])
    print(data)
