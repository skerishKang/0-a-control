# Dependency Installation

Refs #119.

## Runtime install

Use runtime dependencies when you only need to run the local server, CLI helpers, and runtime workflows.

```bash
python -m pip install -r requirements.txt
```

## Development install

Use development dependencies when you need tests, schema validation, or lint tooling.

```bash
python -m pip install -r requirements-dev.txt
```

## Dependency policy

- `requirements.txt` is for runtime dependencies only.
- `requirements-dev.txt` may include test, validation, and lint tooling.
- Dependencies should use explicit compatible version ranges.
- Avoid adding optional external-service packages to runtime dependencies unless they are required for normal operation.

## Current baseline

Runtime:

- `requests>=2.32,<3`
- `telethon>=1.40,<2`

Development:

- runtime dependencies through `-r requirements.txt`
- `pytest>=8,<9`
- `jsonschema>=4.23,<5`
- `ruff>=0.8,<1`

## Future lock strategy

A future PR can introduce a lockfile strategy, for example `pip-tools`, `uv`, or a project-level `pyproject.toml`. Until then, compatible version ranges are the baseline for reproducibility without overconstraining local development.
