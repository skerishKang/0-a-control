from __future__ import annotations

try:
    from scripts.services.executor_prompt import *  # noqa: F401,F403
except ModuleNotFoundError:
    from services.executor_prompt import *  # noqa: F401,F403
