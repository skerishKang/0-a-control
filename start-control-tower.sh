#!/usr/bin/env bash

# Set working directory strictly to where the script is located
cd "$(dirname "$0")"

if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[0-a-control] Python executable not found in PATH."
    echo "Please install Python or add it to PATH, then run again."
    exit 1
fi

PYTHON_CMD=$(command -v python3 || command -v python)

echo "[0-a-control] Starting local server..."
echo ""
echo "Browser URL:"
echo "  Default: http://localhost:4310"
echo "  If 4310 is unavailable, check the actual URL printed by the server below."
echo ""
echo "Telegram:"
echo "  If TELEGRAM_API_ID / TELEGRAM_API_HASH are configured, sync works directly in 0-a-control."
echo ""

$PYTHON_CMD scripts/server.py

echo ""
echo "[0-a-control] Server stopped."
