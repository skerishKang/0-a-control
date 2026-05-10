# Work Queue Core Assignment Model
# Steps 1-3 from docs/20-work-queue-priority-board.md implementation order

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Queue(str, Enum):
    NOW = "NOW"
    NEXT = "NEXT"
    BLOCKED = "BLOCKED"
    LOCAL_NEEDED = "LOCAL_NEEDED"
    VALIDATION_NEEDED = "VALIDATION_NEEDED"
    REVIEW_NEEDED = "REVIEW_NEEDED"
    LATER = "LATER"
    DONE = "DONE"
    NO_ACTION = "NO_ACTION"


class Priority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class ExecutionContext(str, Enum):
    REMOTE_DOABLE = "REMOTE_DOABLE"
    GITHUB_WEB_MODEL_NEEDED = "GITHUB_WEB_MODEL_NEEDED"
    LOCAL_NEEDED = "LOCAL_NEEDED"
    MIXED_REMOTE_CODE_LOCAL_VALIDATION = "MIXED_REMOTE_CODE_LOCAL_VALIDATION"


QUEUE_ORDER = {
    Queue.NOW: 0,
    Queue.LOCAL_NEEDED: 1,
    Queue.VALIDATION_NEEDED: 2,
    Queue.REVIEW_NEEDED: 3,
    Queue.BLOCKED: 4,
    Queue.NEXT: 5,
    Queue.LATER: 6,
    Queue.DONE: 7,
    Queue.NO_ACTION: 8,
}

PRIORITY_ORDER = {
    Priority.P0: 0,
    Priority.P1: 1,
    Priority.P2: 2,
    Priority.P3: 3,
}

DONE_STATUSES = {"DONE", "NO_ACTION", "COMPLETED", "CLOSED", "MERGED"}
BLOCKED_STATUSES = {"BLOCKED", "WAITING", "ON_HOLD"}
VALIDATION_STATUSES = {"NEEDS_VALIDATION", "VALIDATION_REQUIRED", "VALIDATION_NEEDED"}
REVIEW_STATUSES = {"NEEDS_REVIEW", "REVIEW_REQUIRED", "REVIEW_NEEDED"}
LOCAL_GUARDS = {"LOCAL_REQUIRED", "LOCAL_NEEDED", "BROWSER_REQUIRED", "MANUAL_EXECUTION_REQUIRED"}
BLOCKING_GUARDS = {"BLOCKED", "WAITING_ON_DEPENDENCY", "ON_HOLD", "CANNOT_PROCEED"}


@dataclass
class WorkItem:
    id: str
    source: str
    source_type: str
    source_id: str
    title: str
    queue: Queue = Queue.NEXT
    priority: Priority = Priority.P2
    automatic_status: str | None = None
    manual_status: str | None = None
    effective_status: str | None = None
    reason: str | None = None
    next_action: str | None = None
    guards: list[str] = field(default_factory=list)
    is_local_needed: bool = False
    updated_at: str | None = None
    links: list[dict[str, str]] = field(default_factory=list)
    priority_reason: str | None = None
    execution_context: ExecutionContext = ExecutionContext.REMOTE_DOABLE

    @property
    def is_done(self) -> bool:
        if self.effective_status:
            return self.effective_status.upper() in DONE_STATUSES
        if self.automatic_status:
            return self.automatic_status.upper() in DONE_STATUSES
        return False

    @property
    def is_blocked(self) -> bool:
        if self.effective_status:
            return self.effective_status.upper() in BLOCKED_STATUSES
        if self.automatic_status:
            return self.automatic_status.upper() in BLOCKED_STATUSES
        return False

    @property
    def needs_validation(self) -> bool:
        if self.effective_status:
            return self.effective_status.upper() in VALIDATION_STATUSES
        if self.automatic_status:
            return self.automatic_status.upper() in VALIDATION_STATUSES
        return bool(set(self.guards) & VALIDATION_STATUSES)

    @property
    def needs_review(self) -> bool:
        if self.effective_status:
            return self.effective_status.upper() in REVIEW_STATUSES
        if self.automatic_status:
            return self.automatic_status.upper() in REVIEW_STATUSES
        return bool(set(self.guards) & REVIEW_STATUSES)

    @property
    def is_high_priority(self) -> bool:
        return self.priority in (Priority.P0, Priority.P1)

    @property
    def updated_timestamp(self) -> float:
        if self.updated_at:
            try:
                dt = datetime.fromisoformat(self.updated_at.replace("Z", "+00:00"))
                return dt.timestamp()
            except (ValueError, TypeError):
                pass
        return 0.0


def normalize_work_item(raw: dict[str, Any]) -> WorkItem | None:
    if not raw or not raw.get("id"):
        return None

    item_id = str(raw.get("id", ""))
    title = str(raw.get("title", raw.get("name", "untitled")))
    source = str(raw.get("source", "unknown"))
    source_type = str(raw.get("source_type", raw.get("type", "unknown")))
    source_id = str(raw.get("source_id", raw.get("id", item_id)))

    automatic_status = raw.get("automatic_status") or raw.get("status") or raw.get("state")
    if automatic_status and not isinstance(automatic_status, str):
        automatic_status = str(automatic_status)

    manual_status = raw.get("manual_status")
    if manual_status and not isinstance(manual_status, str):
        manual_status = str(manual_status)

    effective_status = raw.get("effective_status") or manual_status or automatic_status
    if effective_status and not isinstance(effective_status, str):
        effective_status = str(effective_status)

    guards = raw.get("guards", [])
    if isinstance(guards, str):
        guards = [g.strip() for g in guards.split(",") if g.strip()]
    guards = [str(g) for g in guards]

    links = raw.get("links", [])
    if not isinstance(links, list):
        links = []

    normalized = WorkItem(
        id=item_id,
        source=source,
        source_type=source_type,
        source_id=source_id,
        title=title,
        automatic_status=automatic_status,
        manual_status=manual_status,
        effective_status=effective_status,
        reason=raw.get("reason"),
        next_action=raw.get("next_action"),
        guards=guards,
        is_local_needed=raw.get("is_local_needed", False),
        updated_at=raw.get("updated_at") or raw.get("created_at"),
        links=links,
    )

    queue, priority, execution_context = assign_queue_priority(normalized)
    normalized.queue = queue
    normalized.priority = priority
    normalized.execution_context = execution_context

    if not normalized.reason and normalized.effective_status:
        normalized.reason = f"Status: {normalized.effective_status}"

    return normalized


def assign_queue_priority(item: WorkItem) -> tuple[Queue, Priority, ExecutionContext]:
    if item.is_done:
        return Queue.NO_ACTION, Priority.P3, ExecutionContext.REMOTE_DOABLE

    if item.is_blocked:
        return Queue.BLOCKED, Priority.P2, ExecutionContext.REMOTE_DOABLE

    if item.is_local_needed or bool(set(item.guards) & LOCAL_GUARDS):
        return Queue.LOCAL_NEEDED, Priority.P1, ExecutionContext.LOCAL_NEEDED

    if item.needs_validation or bool(set(item.guards) & VALIDATION_STATUSES):
        return Queue.VALIDATION_NEEDED, Priority.P1, ExecutionContext.LOCAL_NEEDED

    if item.needs_review or bool(set(item.guards) & REVIEW_STATUSES):
        return Queue.REVIEW_NEEDED, Priority.P2, ExecutionContext.REMOTE_DOABLE

    if bool(set(item.guards) & BLOCKING_GUARDS):
        return Queue.BLOCKED, Priority.P2, ExecutionContext.REMOTE_DOABLE

    if item.is_high_priority:
        return Queue.NOW, Priority.P1, ExecutionContext.REMOTE_DOABLE

    return Queue.NEXT, Priority.P2, ExecutionContext.REMOTE_DOABLE


def sort_work_items(items: list[WorkItem]) -> list[WorkItem]:
    return sorted(
        items,
        key=lambda item: (
            QUEUE_ORDER.get(item.queue, 99),
            PRIORITY_ORDER.get(item.priority, 99),
            -item.updated_timestamp,
            item.source,
            item.id,
        ),
    )


def normalize_work_items(raw_items: list[dict[str, Any]]) -> list[WorkItem]:
    normalized = []
    for raw in raw_items:
        item = normalize_work_item(raw)
        if item:
            normalized.append(item)
    return sort_work_items(normalized)


def group_by_queue(items: list[WorkItem]) -> dict[Queue, list[WorkItem]]:
    groups: dict[Queue, list[WorkItem]] = {q: [] for q in Queue}
    for item in items:
        groups[item.queue].append(item)
    return groups


def get_now_items(items: list[WorkItem]) -> list[WorkItem]:
    return [i for i in items if i.queue == Queue.NOW][:3]


def get_local_needed_items(items: list[WorkItem]) -> list[WorkItem]:
    return [i for i in items if i.queue == Queue.LOCAL_NEEDED][:3]


def get_blocked_items(items: list[WorkItem]) -> list[WorkItem]:
    return [i for i in items if i.queue == Queue.BLOCKED][:3]


def get_validation_needed_items(items: list[WorkItem]) -> list[WorkItem]:
    return [i for i in items if i.queue == Queue.VALIDATION_NEEDED][:3]