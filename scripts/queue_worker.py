from __future__ import annotations

# Enable both `python scripts/foo.py` and `python -m scripts.foo`
import sys
from pathlib import Path
_root = str(Path(__file__).resolve().parents[1])
if _root not in sys.path:
    sys.path.insert(0, _root)

import logging
import time

from scripts.verdict_import import import_verdicts


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("queue_worker")

BASE_SLEEP_SECONDS = 2
MAX_SLEEP_SECONDS = 10


def main() -> None:
    logger.info("Starting queue worker... polling data/queue/verdicts/")
    backoff = BASE_SLEEP_SECONDS
    try:
        while True:
            iteration_start = time.monotonic()
            try:
                import_verdicts()
                backoff = BASE_SLEEP_SECONDS
            except Exception as exc:
                logger.error("import_verdicts() 실패: %s", exc, exc_info=True)
                backoff = min(backoff * 2, MAX_SLEEP_SECONDS)
            elapsed = time.monotonic() - iteration_start
            sleep_for = max(backoff - elapsed, 1)
            logger.debug("queue_worker sleep %.1fs (backoff=%s)", sleep_for, backoff)
            time.sleep(sleep_for)
    except KeyboardInterrupt:
        logger.info("Stopping queue worker...")

if __name__ == "__main__":
    main()
