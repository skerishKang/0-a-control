import sys
from pathlib import Path

_root = str(Path(__file__).resolve().parents[1])
if _root not in sys.path:
    sys.path.insert(0, _root)

from scripts.telegram_cli import show_attachment_status


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python scripts/telegram_attachment_status.py <source_id> [max_file_size_mb]")
        return 1

    source_id = sys.argv[1]
    max_file_size_mb = None
    if len(sys.argv) >= 3:
        try:
            max_file_size_mb = float(sys.argv[2])
        except ValueError:
            print("invalid max_file_size_mb")
            return 1

    show_attachment_status(source_id, max_file_size_mb)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
