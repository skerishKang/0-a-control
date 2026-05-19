from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Relationship:
    child_table: str
    child_column: str
    parent_table: str
    parent_column: str = "id"

    @property
    def key(self) -> str:
        return f"{self.child_table}.{self.child_column}->{self.parent_table}.{self.parent_column}"


HIGH_CONFIDENCE_RELATIONSHIPS: tuple[Relationship, ...] = (
    Relationship("source_records", "session_id", "sessions"),
    Relationship("plan_items", "related_session_id", "sessions"),
    Relationship("plan_items", "related_source_id", "source_records"),
    Relationship("quests", "plan_item_id", "plan_items"),
    Relationship("quests", "parent_quest_id", "quests"),
    Relationship("decision_records", "related_plan_item_id", "plan_items"),
    Relationship("decision_records", "related_quest_id", "quests"),
    Relationship("decision_records", "related_session_id", "sessions"),
    Relationship("brief_records", "related_plan_item_id", "plan_items"),
    Relationship("brief_records", "related_quest_id", "quests"),
    Relationship("brief_records", "related_session_id", "sessions"),
    Relationship("external_inbox", "session_id", "sessions"),
)


def _quote_identifier(value: str) -> str:
    if not value.replace("_", "").isalnum():
        raise ValueError(f"unsafe identifier: {value}")
    return f'"{value}"'


def audit_orphan_references(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return orphaned references for high-confidence relationships.

    This is an audit helper for the future FK migration. It does not mutate data.
    """
    findings: list[dict[str, Any]] = []
    for relationship in HIGH_CONFIDENCE_RELATIONSHIPS:
        child_table = _quote_identifier(relationship.child_table)
        child_column = _quote_identifier(relationship.child_column)
        parent_table = _quote_identifier(relationship.parent_table)
        parent_column = _quote_identifier(relationship.parent_column)
        query = f"""
            SELECT child.id AS child_id, child.{child_column} AS missing_parent_id
            FROM {child_table} AS child
            LEFT JOIN {parent_table} AS parent
              ON parent.{parent_column} = child.{child_column}
            WHERE child.{child_column} IS NOT NULL
              AND parent.{parent_column} IS NULL
            ORDER BY child.id
        """
        rows = conn.execute(query).fetchall()
        for row in rows:
            findings.append(
                {
                    "relationship": relationship.key,
                    "child_table": relationship.child_table,
                    "child_column": relationship.child_column,
                    "child_id": row["child_id"],
                    "missing_parent_id": row["missing_parent_id"],
                }
            )
    return findings


def has_orphan_references(conn: sqlite3.Connection) -> bool:
    return bool(audit_orphan_references(conn))
