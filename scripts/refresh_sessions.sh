#!/bin/bash
# Session refresh script - exports sessions from DB to sessions/ folder

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR" || exit 1

echo "=== Session Refresh ==="
echo "Project: $PROJECT_DIR"
echo ""

# Run export script
echo "1. Export sessions from DB..."
python scripts/export_sessions.py
if [ $? -ne 0 ]; then
    echo "ERROR: export_sessions.py failed"
    exit 1
fi

echo ""
echo "2. Generate HTML view..."
python scripts/generate_session_html.py
if [ $? -ne 0 ]; then
    echo "ERROR: generate_session_html.py failed"
    exit 1
fi

echo ""
echo "=== Done ==="
echo "Sessions exported to: sessions/"
echo "HTML view generated to: sessions_html/"
echo ""
echo "To view:"
echo "  - Markdown: sessions/INDEX.md"
echo "  - HTML: sessions_html/index.html"
