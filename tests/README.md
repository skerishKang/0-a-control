# Tests and Verification

This directory contains automated tests and manual verification scripts for the `0-a-control` project.

## Directory Structure

- `test_*.py`: **Automated Tests**. These are run automatically by GitHub Actions on every push and PR. They use temporary databases and environments to ensure no side effects on production data.
- `seed/`: **Seeding Scripts**. Used to populate the database with sample data for development or manual testing.
    - `seed_diverse_inbox.py`: Creates a complex inbox state.
    - `seed_dummy_inbox.py`: Creates a basic dummy inbox.
    - `seed_telegram_sources.py`: Populates Telegram-related source tables.
- `manual/`: **Manual Verification Scripts**. These require manual execution and observation.
    - `run_pipeline_test.sh`: A shell script to manually trigger and observe the file-based pipeline flow.
    - `db_verify/`: Scripts to manually inspect and verify database integrity.

## Execution

### Automated Tests (CI Scope)
Run all automated tests using:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

### Seeding (Manual)
To seed the database with dummy data:
```bash
python tests/seed/seed_dummy_inbox.py
```

### Manual Verification
To run the manual pipeline test:
```bash
bash tests/manual/run_pipeline_test.sh
```
