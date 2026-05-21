"""Queue read services for dashboard GET handlers."""

from __future__ import annotations

from scripts import db as _db
from scripts.work_queue import group_by_queue, normalize_work_items


def _serialize_item(item) -> dict:
    return {
        "id": item.id,
        "title": item.title,
        "source": item.source,
        "priority": item.priority.value,
        "queue": item.queue.value,
        "status": item.effective_status,
        "updated_at": item.updated_at,
    }


def get_queue_payload(limit: int, queue_filter: str | None = None) -> dict:
    raw_items = _db.get_work_queue_raw(limit)
    items = normalize_work_items(raw_items)

    if queue_filter:
        selected_queue = queue_filter.upper()
        items = [item for item in items if item.queue.value == selected_queue]

    grouped = group_by_queue(items)
    queues = {}
    for queue, queue_items in grouped.items():
        queues[queue.value] = [_serialize_item(item) for item in queue_items]

    return {
        "queues": queues,
        "items": [_serialize_item(item) for item in items],
    }
