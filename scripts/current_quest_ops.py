from __future__ import annotations

try:
    from scripts.services.current_quest_ops import *  # noqa: F401,F403
except ModuleNotFoundError:
    from services.current_quest_ops import *  # noqa: F401,F403
