"""Route-level JSON schema validation for mutation APIs.

Validates POST/PATCH request bodies before they reach handler logic.
Focuses on high-risk/high-volume routes: session and quest mutations.

Schemas use jsonschema Draft202012Validator (from requirements.txt).
"""

from __future__ import annotations

from http import HTTPStatus
from typing import Any

from jsonschema import Draft202012Validator, ValidationError, validators

# ── Schema definitions ─────────────────────────────────────────────────

SESSION_START_SCHEMA = {
    "type": "object",
    "required": ["agent_name", "source_type"],
    "additionalProperties": False,
    "properties": {
        "agent_name": {"type": "string", "minLength": 1, "maxLength": 200},
        "source_type": {"type": "string", "minLength": 1, "maxLength": 50},
        "model_name": {"type": "string", "maxLength": 200},
        "project_key": {"type": "string", "maxLength": 200},
        "working_dir": {"type": "string", "maxLength": 500},
        "title": {"type": "string", "maxLength": 500},
        "metadata": {"type": "object"},
    },
}

SESSION_LOG_SCHEMA = {
    "type": "object",
    "required": ["session_id", "source_name", "source_type", "content"],
    "additionalProperties": False,
    "properties": {
        "session_id": {"type": "string", "minLength": 1, "maxLength": 200},
        "source_name": {"type": "string", "minLength": 1, "maxLength": 200},
        "source_type": {"type": "string", "minLength": 1, "maxLength": 50},
        "content": {"type": "string", "minLength": 1, "maxLength": 200000},
        "role": {
            "type": "string",
            "maxLength": 50,
            "default": "user",
        },
        "project_key": {"type": "string", "maxLength": 200},
        "working_dir": {"type": "string", "maxLength": 500},
        "metadata": {"type": "object"},
    },
}

SESSION_END_SCHEMA = {
    "type": "object",
    "required": ["session_id"],
    "additionalProperties": False,
    "properties": {
        "session_id": {"type": "string", "minLength": 1, "maxLength": 200},
        "summary_md": {"type": "string", "maxLength": 50000},
        "status": {
            "type": "string",
            "maxLength": 50,
            "default": "closed",
        },
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
        "metadata": {"type": "object"},
    },
}

QUEST_EVALUATE_SCHEMA = {
    "type": "object",
    "required": ["quest_id", "verdict"],
    "additionalProperties": False,
    "properties": {
        "quest_id": {"type": "string", "minLength": 1, "maxLength": 200},
        "verdict": {
            "type": "string",
            "enum": ["done", "partial", "hold"],
        },
        "reason": {"type": "string", "maxLength": 10000},
        "restart_point": {"type": "string", "maxLength": 5000},
        "next_quest_hint": {"type": "string", "maxLength": 5000},
        "plan_impact": {"type": "string", "maxLength": 5000},
    },
}

QUEST_REPORT_SCHEMA = {
    "type": "object",
    "required": ["quest_id"],
    "additionalProperties": False,
    "properties": {
        "quest_id": {"type": "string", "minLength": 1, "maxLength": 200},
        "work_summary": {"type": "string", "maxLength": 20000},
        "remaining_work": {"type": "string", "maxLength": 10000},
        "blocker": {"type": "string", "maxLength": 10000},
        "self_assessment": {"type": "string", "maxLength": 10000},
        "session_id": {"type": "string", "maxLength": 200},
    },
}

# ── Route-to-schema registry ──────────────────────────────────────────

ROUTE_SCHEMAS: dict[str, dict[str, Any]] = {
    "/api/sessions/start": SESSION_START_SCHEMA,
    "/api/sessions/log": SESSION_LOG_SCHEMA,
    "/api/sessions/end": SESSION_END_SCHEMA,
    "/api/quests/evaluate": QUEST_EVALUATE_SCHEMA,
    "/api/quests/report": QUEST_REPORT_SCHEMA,
}


# ── Validator ──────────────────────────────────────────────────────────

def _validator_with_defaults(schema: dict) -> Draft202012Validator:
    """Create a Draft202012Validator that fills in default values."""
    def extend_with_default(validator_class):
        validate_properties = validator_class.VALIDATORS["properties"]

        def set_defaults(validator_instance, properties, instance, schema):
            for prop, subschema in properties.items():
                if "default" in subschema and isinstance(instance, dict):
                    instance.setdefault(prop, subschema["default"])
            yield from validate_properties(
                validator_instance, properties, instance, schema,
            )

        return validators.extend(
            validator_class,
            {"properties": set_defaults},
        )

    DefaultValidator = extend_with_default(Draft202012Validator)
    return DefaultValidator(schema)


# Expose a pre-configured validate function
def validate(body: dict, schema: dict) -> list[str]:
    """Validate body against schema. Returns list of error messages (empty = valid)."""
    validator = _validator_with_defaults(schema)
    errors: list[str] = []
    for error in validator.iter_errors(body):
        path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "(root)"
        errors.append(f"{path}: {error.message}")
    return errors


def validate_mutation_body(path: str, body: dict) -> dict | None:
    """Validate a mutation request body against its registered schema.

    Args:
        path: API route path (e.g. '/api/sessions/start')
        body: Parsed request body dict.

    Returns:
        None if valid, or a dict with 'error'/'detail' for the 400 response.
    """
    schema = ROUTE_SCHEMAS.get(path)
    if schema is None:
        return None  # No schema registered for this route — allow

    errors = validate(body, schema)
    if errors:
        return {
            "error": "invalid request body",
            "detail": errors,
        }
    return None
