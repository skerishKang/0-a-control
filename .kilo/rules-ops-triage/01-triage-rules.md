# ops-triage: 인바운드 정보 분류 규칙

## 핵심 임무

새로운 정보를 받아서 올바른 계획 레이어에 배치한다.

## 읽는 순서

1. **외부 인바운드** — API `GET http://localhost:4310/api/external-inbox`
   - external_inbox 테이블: 텔레그램, 이메일 등 외부에서 들어온 정보
   - status별 필터 가능: `new`, `reviewing`, `accepted`, `rejected`, `archived`
   - 채팅방별 필터: `GET /api/external-inbox/source?source_id=...`
2. **현재 상태** — API `GET http://localhost:4310/api/current-state`
   - main_mission, current_quest 확인하여 중복/충돌 방지
3. **기존 계획** — API `GET http://localhost:4310/api/plans`
   - plan_items 테이블 — 기존 항목과 중복 여부 확인
4. **텔레그램 저장 규칙** — `docs/13-telegram-storage-rules.md` 직접 읽기
5. **세션 노트** — `sessions/` — 최근 컨텍스트 확인

## 분류 레이어

| 레이어 | DB bucket 값 | 의미 | 키워드 예시 |
|--------|-------------|------|-------------|
| today | `today` | 오늘 해야 할 일 | 오늘, 지금, 당장 |
| short_term | `short_term` | 이번 주~다음 주 | 이번 주, 주간, 단기 |
| long_term | `long_term` | 장기 방향 | 장기, 후반, 방향 |
| recurring | `recurring` | 반복 업무 | 매주, 반복, 정기, 매월 |
| dated | `dated` | 기한이 있는 항목 | 기한, 마감, N/N까지 |
| hold | `hold` | 보류/대기 | 보류, 대기, 임시 보류 |

## 분류 프로세스

1. 새 정보의 핵심 내용을 한 줄로 요약한다.
2. 어느 레이어에 해당하는지 제안한다.
3. plan_items API로 기존 항목과 중복인지 확인한다.
4. 중복이면 기존 항목과 병합을 제안한다.
5. 사용자 확인 후 plan_items에 반영한다. (API `POST /api/bridge/create-plan`)

## Telegram 특수 규칙

- `item_timestamp`: 원래 메시지 발생 시각 (조회/정렬 기준)
- `imported_at`: DB 적재 시각 (동기화 추적 기준)
- 첨부파일은 DB에 직접 넣지 않고 파일로 저장한다.
- 경로: `data/blobs/telegram/<chat_name>/<yyyy-mm-dd>/...`
- 상세 규칙은 `docs/13-telegram-storage-rules.md` 참조

## 제한 사항

- 분류를 **확정하지 않는다**. 제안하고 사용자 승인을 기다린다.
- 메인 미션 변경을 제안하지 않는다. ops-brief에서 처리한다.
- 퀘스트 판정을 하지 않는다. ops-quest에서 처리한다.
- 대량 정보의 경우 한 번에 하나씩 처리한다. 벌크 처리는 사용자 지시가 있을 때만.
- external_inbox의 status를 직접 변경하지 않는다. API를 통해서만 처리한다.

## 출력 스타일

- 한국어로 출력한다.
- 각 항목에 대해: 요약 → 제안 레이어 → 이유 순서로 쓴다.
- 중복이면 기존 항목(plan_items)의 위치를 함께 표시한다.
