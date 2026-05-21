from __future__ import annotations

try:
    from scripts.cli.db_search import *  # noqa: F401,F403
    from scripts.cli.db_search import main
except ModuleNotFoundError:
    from cli.db_search import *  # noqa: F401,F403
    from cli.db_search import main


if __name__ == "__main__":
    main()
