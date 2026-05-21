from __future__ import annotations

try:
    from scripts.services.request_validation import *  # noqa: F401,F403
except ModuleNotFoundError:
    from services.request_validation import *  # noqa: F401,F403
