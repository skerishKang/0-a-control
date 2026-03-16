#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

LOG_DIR="$ROOT_DIR/data/runtime"
LOG_FILE="$LOG_DIR/telegram_backfill_priority.log"
mkdir -p "$LOG_DIR"

BATCH_LIMIT="${BATCH_LIMIT:-50}"
MAX_ROUNDS="${MAX_ROUNDS:-200}"

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$LOG_FILE"
}

run_backfill_round() {
  local source_id="$1"
  python3 scripts/telegram_cli.py backfill-chat "$source_id" --batch-limit "$BATCH_LIMIT" --max-batches 1
}

extract_json_field() {
  local field="$1"
  python3 -c 'import json,sys; data=json.load(sys.stdin); print(data.get(sys.argv[1], ""))' "$field"
}

backfill_source() {
  local source_id="$1"
  local label="$2"
  local round=0
  local last_oldest=""

  log "START $label ($source_id)"
  while (( round < MAX_ROUNDS )); do
    round=$((round + 1))
    local payload
    if ! payload="$(run_backfill_round "$source_id")"; then
      log "FAIL  $label round=$round"
      return 1
    fi

    local ok processed changed oldest
    ok="$(printf '%s' "$payload" | extract_json_field ok)"
    processed="$(printf '%s' "$payload" | extract_json_field processed_count)"
    changed="$(printf '%s' "$payload" | extract_json_field changed_rows)"
    oldest="$(printf '%s' "$payload" | extract_json_field oldest_message_id)"

    log "ROUND $label round=$round processed=$processed changed=$changed oldest=$oldest"

    if [[ "$ok" != "True" && "$ok" != "true" ]]; then
      log "STOP  $label round=$round not-ok payload=$payload"
      break
    fi

    if [[ -z "$processed" || "$processed" == "0" ]]; then
      log "DONE  $label no-more-history"
      break
    fi

    if [[ -n "$last_oldest" && "$oldest" == "$last_oldest" ]]; then
      log "DONE  $label oldest-id-stalled=$oldest"
      break
    fi

    last_oldest="$oldest"
  done
  log "END   $label"
}

log "BACKFILL START batch_limit=$BATCH_LIMIT max_rounds=$MAX_ROUNDS"
backfill_source "5666389128" "강혜림"
backfill_source "889584794" "내텔레"
log "BACKFILL END"
