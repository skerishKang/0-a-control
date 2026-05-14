#!/usr/bin/env bash

# Set working directory strictly to where the script is located
cd "$(dirname "$0")"

IS_WSL=0
if grep -qiE "microsoft|wsl" /proc/version 2>/dev/null; then
    IS_WSL=1
fi

case "$(pwd -P)" in
    /mnt/*)
        if [ "$IS_WSL" -eq 1 ]; then
            echo "[0-a-control] Refusing to start the dashboard server from a WSL-mounted Windows path."
            echo ""
            echo "Reason: running the Python server from /mnt/* makes SQLite/workdiary I/O cross the WSL<->Windows filesystem boundary."
            echo "Use the Windows launcher from PowerShell instead:"
            echo "  .\\start-control-tower.ps1"
            echo ""
            echo "Hermes/WSL should edit and review code, not start this local dashboard server against a Windows-mounted repo."
            exit 1
        fi
        ;;
esac

if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[0-a-control] Python executable not found in PATH."
    echo "Please install Python or add it to PATH, then run again."
    exit 1
fi

PYTHON_CMD=$(command -v python3 || command -v python)

echo "[0-a-control] Starting local server..."
echo ""
echo "Browser URL:"
echo "  http://localhost:4310"
echo ""
echo "Telegram:"
echo "  If TELEGRAM_API_ID / TELEGRAM_API_HASH are configured, sync works directly in 0-a-control."
echo ""

$PYTHON_CMD scripts/server.py

echo ""
echo "[0-a-control] Server stopped."
