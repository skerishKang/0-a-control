#!/usr/bin/env bash
set -euo pipefail

# Create temp dir
TEMP_DIR=$(mktemp -d)
export CONTROL_TOWER_DATA_DIR="$TEMP_DIR/data"
export CONTROL_TOWER_DB_PATH="$CONTROL_TOWER_DATA_DIR/control_tower.db"
export CONTROL_TOWER_QUEUE_DIR="$CONTROL_TOWER_DATA_DIR/queue"

echo "Running tests in: $TEMP_DIR"

# Initialize DB in temp dir
python -c "from scripts.db_base import init_db; init_db()"

# Run tests
python -m unittest tests/test_01_pipeline_flow.py

# Cleanup
rm -rf "$TEMP_DIR"
