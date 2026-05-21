from __future__ import annotations

try:
    from scripts.services.manual_overrides import *  # noqa: F401,F403
except ModuleNotFoundError:
    from services.manual_overrides import *  # noqa: F401,F403
