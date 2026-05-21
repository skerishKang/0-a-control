from __future__ import annotations

try:
    from scripts.services.ai_verdict import *  # noqa: F401,F403
except ModuleNotFoundError:
    from services.ai_verdict import *  # noqa: F401,F403
