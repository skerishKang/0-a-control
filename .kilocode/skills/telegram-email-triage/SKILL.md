---
name: telegram-email-triage
description: "새 외부 입력(telegram, email, 수동 입력)을 today/dated/hold/short_term 관점으로 분류하고 배치를 제안."
---

# telegram-email-triage

## 언제 쓰는지

- Telegram 동기화 후 새 메시지가 쌓였을 때
- 사용자가 "이거 정리해줘", "어디에 넣을까"라고 요청할 때
- `external_inbox`에 `status='new'` 항목이 있을 때
- 이메일이나 외부 노트를 수동으로 붙여넣었을 때

## 입력으로 기대하는 정보

1. `external_inbox` 테이블의 새 항목 (`status = 'new'` 또는 `'reviewing'`)
   - `source_name`, `author`, `raw_content`, `item_timestamp`
   - `item_type` (text, image, file 등)
   - `chat_class` (핵심4개, 주식큐레이터, 뉴스, 일반대화)
2. 현재 plans (중복 확인용)
3. `current_state` (메인 미션, 현재 퀘스트 맥락)

## 실행 절차

### Step 1: 새 항목 수집

먼저 Telegram 동기화가 필요한지 확인한다:

```bash
python scripts/telegram_cli.py sync-core
```

그 다음 새 항목을 가져온다:

```
GET http://localhost:4310/api/external-inbox?status=new&limit=50
```

서버 미기동 시 직접 쿼리:

```bash
python -c "
from scripts.telegram_db import get_db_connection
conn = get_db_connection()
rows = conn.execute('''
    SELECT id, source_name, author, raw_content, item_timestamp, item_type, chat_class
    FROM external_inbox
    WHERE status = \"new\"
    ORDER BY COALESCE(NULLIF(item_timestamp, \"\"), imported_at) DESC
    LIMIT 50
''').fetchall()
for r in rows:
    print(f'[{r[\"id\"]}] {r[\"source_name\"]}: {r[\"raw_content\"][:80]}')
conn.close()
"
```

항목이 없으면 "새 항목 없음. 동기화를 먼저 실행하세요" 안내 후 종료.

### Step 2: 항목 분류

각 항목에 대해 아래 기준으로 분류한다:

| 레이어 | 기준 |
|--------|------|
| **today** | 오늘 당장 처리 필요 |
| **dated** | 특정 기한이 있음 |
| **short_term** | 이번 주~다음 주 |
| **long_term** | 장기 방향 |
| **recurring** | 반복 항목 |
| **hold** | 보류/대기 |

분류 우선순위: `today` > `dated` > `short_term` > `long_term` > `recurring` > `hold`

### Step 3: 중복 확인

```
GET http://localhost:4310/api/plans
```

plan_items에서 제목/내용 유사 항목을 확인한다:
- 이미 존재하면 → "기존 항목과 병합 제안"
- 없으면 → "새 plan_item 생성 제안"

### Step 4: Telegram 특수 처리

`docs/13-telegram-storage-rules.md` 규칙을 준수한다:
- `item_timestamp`: 원래 메시지 시각 (정렬 기준)
- `imported_at`: DB 적재 시각 (추적 기준)
- 첨부파일: `attachment_path`로 파일 참조. DB에 직접 저장하지 않음
- 첨부 경로 규칙: `data/blobs/telegram/<chat_name>/<yyyy-mm-dd>/...`

### Step 5: 분류 결과 출력

```
인바운드 분류 — {날짜}

분류 결과 (총 {N}건)

today ({n}건)
1. {제목/요약}
   - 출처: {source_name} / {author}
   - 시간: {item_timestamp}
   - 제안: plan_item (today) 생성
   - 이유: {분류 이유}

dated ({n}건)
...

short_term ({n}건)
...

hold ({n}건)
...

중복 항목
- "{제목}" → 기존 plan_item "{기존 제목}"과 유사. 병합 제안

처리 완료
- 총 {N}건 분류 완료
```

분류 후 사용자 확인을 거쳐 plan_items에 반영한다:

```
POST http://localhost:4310/api/plans/approve
Content-Type: application/json

{
  "candidates": [
    {
      "bucket": "today",
      "title": "...",
      "description": "...",
      "priority_score": 80,
      "related_source_id": "..."
    }
  ]
}
```

## 출력 형식

- 한국어로 출력한다.
- 각 항목에 대해: 요약 → 제안 레이어 → 이유 순서로 쓴다.
- 중복이면 기존 항목 위치를 함께 표시한다.

## 실패/누락 시 fallback

| 상황 | fallback |
|------|----------|
| `external_inbox` 비어 있음 | "새 항목 없음. Telegram 동기화를 먼저 실행하세요" 안내 |
| 서버 미기동 | `scripts/telegram_db.py`로 직접 DB 쿼리 |
| 항목이 너무 많음 (>50건) | 상위 10건만 처리, 나머지는 "추가 분류 필요"로 표시 |
| 분류가 애매한 항목 | 사용자에게 직접 분류 요청 ("이건 어디에 넣을까요?") |
| 첨부파일 누락 | `python scripts/telegram_cli.py attachment-status {source_id}`로 확인 |

## 관련 파일/스크립트

- `scripts/telegram_cli.py` — `sync-core`, `import-chat`, `list-sources`, `attachment-status`
- `scripts/telegram_db.py` — `get_db_connection()`, `init_db()`
- `scripts/plan_ops.py` — `approve_plan_candidates()`, `get_plans()`
- `scripts/db_state.py` — `get_external_inbox_overview()`
- `docs/13-telegram-storage-rules.md` — Telegram 저장 규칙
- `public/app-support.js` — `renderExternalContextPanel()` (UI 참조)
- `.kilo/rules-ops-triage/01-triage-rules.md` — ops-triage 모드 세부 규칙

## 제한 사항

- 분류는 **제안만** 한다. 사용자가 확정한 후 plan_items에 반영한다.
- 대량 정보의 경우 한 번에 하나씩 처리한다. 벌크 처리는 사용자 지시가 있을 때만.
- 메인 미션 변경을 제안하지 않는다. ops-brief에서 처리한다.
- 퀘스트 판정을 하지 않는다. ops-quest에서 처리한다.
- Telegram 동기화는 이 skill의 사전 단계일 수 있다. 동기화 없이 분류하면 빈 결과가 나올 수 있다.
