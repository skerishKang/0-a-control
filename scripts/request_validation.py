from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator, validators

STRING_SHORT = {"type": "string", "maxLength": 200}
STRING_MEDIUM = {"type": "string", "maxLength": 5000}
METADATA = {"type": "object"}

SESSION_START_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["agent_name", "source_type"],
    "additionalProperties": True,
    "properties": {
        "agent_name": {"type": "string", "minLength": 1, "maxLength": 200},
        "source_type": {"type": "string", "minLength": 1, "maxLength": 50},
        "model_name": STRING_SHORT,
        "project_key": STRING_SHORT,
        "working_dir": {"type": "string", "maxLength": 500},
        "title": {"type": "string", "maxLength": 500},
        "metadata": METADATA,
    },
}

SESSION_LOG_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["session_id", "source_name", "source_type", "content"],
    "additionalProperties": True,
    "properties": {
        "session_id": {"type": "string", "minLength": 1, "maxLength": 200},
        "source_name": {"type": "string", "minLength": 1, "maxLength": 200},
        "source_type": {"type": "string", "minLength": 1, "maxLength": 50},
        "content": {"type": "string", "minLength": 1, "maxLength": 200000},
        "role": {"type": "string", "maxLength": 50, "default": "user"},
        "project_key": STRING_SHORT,
        "working_dir": {"type": "string", "maxLength": 500},
        "metadata": METADATA,
    },
}

SESSION_END_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["session_id"],
    "additionalProperties": True,
    "properties": {
        "session_id": {"type": "string", "minLength": 1, "maxLength": 200},
        "summary_md": {"type": "string", "maxLength": 50000},
        "status": {"type": "string", "maxLength": 50, "default": "closed"},
        "files_touched": {
            "type": "array",
            "items": {"type": "string", "maxLength": 500},
            "maxItems": 200,
        },
        "actions": {
            "type": "array",
            "items": {"type": "string", "maxLength": 500},
            "maxItems": 200,
        },
        "metadata": METADATA,
    },
}

QUEST_EVALUATE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["quest_id", "verdict"],
    "additionalProperties": True,
    "properties": {
        "quest_id": {"type": "string", "minLength": 1, "maxLength": 200},
        "verdict": {"type": "string", "enum": ["done", "partial", "hold"]},
        "reason": {"type": "string", "maxLength": 10000},
        "restart_point": STRING_MEDIUM,
        "next_quest_hint": STRING_MEDIUM,
        "plan_impact": STRING_MEDIUM,
    },
}

QUEST_REPORT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["quest_id"],
    "additionalProperties": True,
    "properties": {
        "quest_id": {"type": "string", "minLength": 1, "maxLength": 200},
        "work_summary": {"type": "string", "maxLength": 20000},
        "remaining_work": {"type": "string", "maxLength": 10000},
        "blocker": {"type": "string", "maxLength": 10000},
        "self_assessment": {"type": "string", "maxLength": 10000},
        "session_id": STRING_SHORT,
    },
}

ROUTE_SCHEMAS: dict[str, dict[str, Any]] = {
    "/api/sessions/start": SESSION_START_SCHEMA,
    "/api/sessions/log": SESSION_LOG_SCHEMA,
    "/api/sessions/end": SESSION_END_SCHEMA,
    "/api/quests/evaluate": QUEST_EVALUATE_SCHEMA,
    "/api/quests/report": QUEST_REPORT_SCHEMA,
}


def _validator_with_defaults(schema: dict[str, Any]) -> Draft202012Validator:
    validate_properties = Draft202012Validator.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        if isinstance(instance, dict):
            for prop, subschema in properties.items():
                if "default" in subschema:
                    instance.setdefault(prop, subschema["default"])
        yield from validate_properties(validator, properties, instance, schema)

    default_validator = validators.extend(
        Draft202012Validator,
        {"properties": set_defaults},
    )
    return default_validator(schema)


def validate(body: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = _validator_with_defaults(schema)
    errors: list[str] = []
    for error in validator.iter_errors(body):
        path = ".".join(str(part) for part in error.absolute_path) if error.absolute_path else "(root)"
        errors.append(f"{path}: {error.message}")
    return errors


def validate_mutation_body(path: str, body: dict[str, Any]) -> dict[str, Any] | None:
    schema = ROUTE_SCHEMAS.get(path)
    if schema is None:
        return None
    if not isinstance(body, dict):
        return {"error": "invalid request body", "detail": ["(root): request body must be an object"]}
    errors = validate(body, schema)
    if not errors:
        return None
    return {"error": "invalid request body", "detail": errors}
