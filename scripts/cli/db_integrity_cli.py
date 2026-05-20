from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.db_base import connect, init_db
from scripts.db_integrity import audit_orphan_references


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit high-confidence relational references before FK migration.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print findings as JSON.",
    )
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialize the database schema before auditing.",
    )
    return parser


def _print_text(findings: list[dict]) -> None:
    print("Relational integrity audit")
    print(f"orphan references: {len(findings)}")
    if not findings:
        print("RESULT: PASS")
        return

    print("\nFindings:")
    for item in findings:
        print(
            "  "
            f"{item['relationship']} "
            f"child_id={item['child_id']} "
            f"missing_parent_id={item['missing_parent_id']}"
        )
    print("\nRESULT: FAIL")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.init_db:
        init_db()

    with connect() as conn:
        findings = audit_orphan_references(conn)

    if args.json:
        print(json.dumps({"ok": not findings, "findings": findings}, ensure_ascii=False, indent=2))
    else:
        _print_text(findings)

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
