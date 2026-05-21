from __future__ import annotations

try:
    from scripts.cli.repair_stale_pending import *  # noqa: F401,F403
    from scripts.cli.repair_stale_pending import main
except ModuleNotFoundError:
    from cli.repair_stale_pending import *  # noqa: F401,F403
    from cli.repair_stale_pending import main


if __name__ == "__main__":
    main()
