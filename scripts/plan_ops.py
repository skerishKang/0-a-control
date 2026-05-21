from __future__ import annotations

try:
    from scripts.services.plan_ops import *  # noqa: F401,F403
except ModuleNotFoundError:
    from services.plan_ops import *  # noqa: F401,F403
