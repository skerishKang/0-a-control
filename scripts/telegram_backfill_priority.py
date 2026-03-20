import json
from datetime import datetime
from pathlib import Path

from telegram_cli import backfill_chat


ROOT_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT_DIR / "data" / "runtime"
LOG_FILE = LOG_DIR / "telegram_backfill_priority.log"


def log(message: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def backfill_source(source_id: str, label: str, batch_limit: int, max_rounds: int) -> None:
    round_no = 0
    last_oldest = None

    log(f"START {label} ({source_id})")
    while round_no < max_rounds:
        round_no += 1
        payload = backfill_chat(
            source_id,
            batch_limit=batch_limit,
            max_batches=1,
            download_attachments=True,
        )

        ok = bool(payload.get("ok"))
        processed = payload.get("processed_count", 0)
        changed = payload.get("changed_rows", 0)
        oldest = payload.get("oldest_message_id")

        log(
            f"ROUND {label} round={round_no} processed={processed} "
            f"changed={changed} oldest={oldest}"
        )

        if not ok:
            log(f"STOP  {label} round={round_no} not-ok payload={json.dumps(payload, ensure_ascii=False)}")
            break

        if not processed:
            log(f"DONE  {label} no-more-history")
            break

        if last_oldest is not None and oldest == last_oldest:
            log(f"DONE  {label} oldest-id-stalled={oldest}")
            break

        last_oldest = oldest

    log(f"END   {label}")


def main() -> None:
    import os

    batch_limit = int(os.environ.get("BATCH_LIMIT", "50"))
    max_rounds = int(os.environ.get("MAX_ROUNDS", "200"))

    log(f"BACKFILL START batch_limit={batch_limit} max_rounds={max_rounds}")
    backfill_source("5666389128", "강혜림", batch_limit, max_rounds)
    backfill_source("889584794", "내텔레", batch_limit, max_rounds)
    log("BACKFILL END")


if __name__ == "__main__":
    main()
