from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.validate_contract import validate_payload


ROOT = Path(__file__).resolve().parents[1]
REPORT_SCHEMA = ROOT / "schemas" / "report.schema.json"
VERDICT_SCHEMA = ROOT / "schemas" / "verdict.schema.json"


def write_json(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def valid_report() -> dict:
    return {
        "schema_version": "1.0",
        "report": {
            "quest_id": "q-1",
            "quest_title": "Test quest",
            "completion_criteria": ["done"],
            "work_summary": "Implemented the requested change"
        }
    }


def valid_verdict() -> dict:
    return {
        "schema_version": "1.0",
        "report_ref": "report-1",
        "verdict": {
            "status": "done",
            "reason": "Meets criteria",
            "plan_impact": {
                "today": [],
                "short_term": [],
                "long_term": [],
                "recurring": [],
                "dated": []
            }
        }
    }


def test_valid_report_passes(tmp_path):
    payload = write_json(tmp_path, "report.json", valid_report())
    assert validate_payload(REPORT_SCHEMA, payload) == []


def test_report_missing_quest_id_fails(tmp_path):
    data = valid_report()
    del data["report"]["quest_id"]
    payload = write_json(tmp_path, "report.json", data)
    errors = validate_payload(REPORT_SCHEMA, payload)
    assert any("quest_id" in error for error in errors)


def test_valid_verdict_passes(tmp_path):
    payload = write_json(tmp_path, "verdict.json", valid_verdict())
    assert validate_payload(VERDICT_SCHEMA, payload) == []


@pytest.mark.parametrize("field", ["report_ref"])
def test_verdict_missing_root_field_fails(tmp_path, field):
    data = valid_verdict()
    del data[field]
    payload = write_json(tmp_path, "verdict.json", data)
    errors = validate_payload(VERDICT_SCHEMA, payload)
    assert any(field in error for error in errors)


def test_verdict_invalid_status_fails(tmp_path):
    data = valid_verdict()
    data["verdict"]["status"] = "unknown"
    payload = write_json(tmp_path, "verdict.json", data)
    errors = validate_payload(VERDICT_SCHEMA, payload)
    assert any("status" in error or "unknown" in error for error in errors)


def test_verdict_missing_plan_impact_bucket_fails(tmp_path):
    data = valid_verdict()
    del data["verdict"]["plan_impact"]["today"]
    payload = write_json(tmp_path, "verdict.json", data)
    errors = validate_payload(VERDICT_SCHEMA, payload)
    assert any("today" in error for error in errors)
