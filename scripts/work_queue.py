from __future__ import annotations

try:
    from scripts.services.work_queue import *  # noqa: F401,F403
except ModuleNotFoundError:
    from services.work_queue import *  # noqa: F401,F403
