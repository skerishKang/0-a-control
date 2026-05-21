from __future__ import annotations

try:
    from scripts.services.planning_input import *  # noqa: F401,F403
except ModuleNotFoundError:
    from services.planning_input import *  # noqa: F401,F403
