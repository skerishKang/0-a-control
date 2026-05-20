from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def format_error_path(error) -> str:
    path = ".".join(str(part) for part in error.absolute_path)
    return path or "<root>"


def validate_payload(schema_path: Path, payload_path: Path) -> list[str]:
    schema = load_json(schema_path)
    payload = load_json(payload_path)

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.absolute_path))

    return [f"{format_error_path(error)}: {error.message}" for error in errors]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a JSON payload against a JSON Schema contract."
    )
    parser.add_argument("schema", type=Path)
    parser.add_argument("payload", type=Path)
    args = parser.parse_args(argv)

    try:
        errors = validate_payload(args.schema, args.payload)
    except FileNotFoundError as exc:
        print(f"file not found: {exc.filename}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"invalid JSON: {exc}", file=sys.stderr)
        return 2

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
