from __future__ import annotations

try:
    from scripts.services.verdict_ops import *  # noqa: F401,F403
except ModuleNotFoundError:
    from services.verdict_ops import *  # noqa: F401,F403
