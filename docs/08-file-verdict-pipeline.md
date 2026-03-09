# 08. 파일 기반 퀘스트 판정 파이프라인

## 1. 목적과 전제
- CMD 세션과 UI는 **퀘스트 보고(report)** 를 JSON 파일로 저장한다.
- 외부 IDE/CMD 에이전트가 동일 보고서를 읽고 **판정(verdict)** JSON을 작성한다.
- 본체 서버는 verdict 파일을 감지하여 SQLite 상태를 갱신한다.
- 모델 호출은 내부 서버가 아닌 외부 커맨드로 위임해 벤더 종속을 최소화한다.

## 2. 파이프라인 단계
1. **보고 생성 (UI or CMD)**  
   - `/api/quests/report` 호출 또는 CLI 스크립트가 `data/queue/reports/`에 JSON을 드랍한다.  
   - 파일명: `{ts}-{questId}-{sessionId}.report.json` (sessionId 없으면 `_`).
2. **보고 고정**  
   - report 파일은 수정 금지. 필요한 보정은 새 report 생성으로 처리.
3. **외부 에이전트 판정**  
   - 에이전트 워커는 `data/queue/reports/`를 폴링/워치.  
   - 읽은 report는 동일 base name으로 `data/queue/verdicts/`에 verdict JSON을 기록한다.
4. **본체 수집 및 DB 반영**  
   - 서버 스케줄러가 `data/queue/verdicts/`를 스캔해 새 verdict를 `quests`/`plan_items`에 반영한다.  
   - 성공 시 report/verdict 세트를 `data/queue/processed/`로 이동한다.
5. **세션 내보내기**  
   - 필요한 경우 `session_exports/`에 요약 Markdown + JSON snapshot을 생성해 다른 에이전트가 재시작점을 공유한다.

## 3. 디렉토리 역할
| 디렉토리 | 역할 | 샘플 파일 | 보관 정책 |
| --- | --- | --- | --- |
| `data/queue/reports/` | 사용자가 제출한 진행 보고 원본. 수정 금지. | `20260309T053100Z-q123-s456.report.json` | 당일 + 2일 보유 후 `data/queue/processed/` 이동 |
| `data/queue/verdicts/` | 외부 에이전트가 작성한 판정 JSON. | `20260309T053145Z-q123-s456.verdict.json` | ingest 완료 시 `data/queue/processed/` 이동 |
| `session_exports/` | 특정 세션·퀘스트의 briefing, replay 데이터를 저장. 다른 에이전트 재진입용. | `20260309-q123-session.md` | 7일 보관 후 `archive/` 이동 |
| `data/queue/processed/` 또는 `archive/` | 이미 ingest된 report+verdict 묶음과 만료된 export를 장기 보관. | `data/queue/processed/2026/03/09/q123/` | 월 단위 rotate, 필요 시 `archive/`로 zip |

## 4. 파일 컨벤션
- **Base name**: `{ISO8601 basic}-{questId}-{sessionIdOr_}`.
- **확장자**: `.report.json`, `.verdict.json`, `.md` (export). 
- **메타데이터**: JSON 내부 `quest_id`, `session_id`, `report_id`로 상호 참조.
- **동시성**: verdict 작성자는 report 파일을 읽기 전 `*.lock` 파일 확인. 필요 시 자체 락을 만든 뒤 완료 후 제거.

## 5. 상태 플로우 예시
```mermaid
digraph G {
  report["report JSON 생성"] -> verdictAgent["외부 에이전트 판정"] -> ingest["서버 ingest"];
  ingest -> dbUpdate["quests.status & plan_items.status 갱신"];
  dbUpdate -> currentState["current_state 테이블 반영"];
  ingest -> processed["data/queue/processed/ 이동"];
}
```
- 자세한 상태 전이는 `docs/09-json-contracts.md` 참고.

## 6. 실패 및 재처리 전략 (운영 시나리오)

현재 `0-a-control`의 파이프라인은 아래와 같이 파일 상태와 워커 사이의 장애 모듈을 격리하며 무중단으로 동작합니다. 

| 케이스 | 감지 포인트 및 워커 처리 | 잔여 리스크 및 대응 (DB/UI) |
| --- | --- | --- |
| **JSON 파손 (Malformed)** | `json.loads` 실패 또는 필수 필드 누락 발생. 워커는 해당 파일을 `data/queue/verdicts/failed/`로 즉시 격리 | 퀘스트 상태는 여전히 `pending`으로 남아 있습니다. 사용자가 수동으로 원본 report를 지우고 UI에서 재보고하거나 에이전트를 수동 재호출해야 합니다. |
| **중복 처리 (Duplicate)** | 동일 `report_ref`, 같은 판정 결과, 동일한 `verdict_seq` 감지. 워커가 `DuplicateVerdict` 예외를 내고 `data/queue/processed/duplicates/`로 파일 이동 | DB 변화 없이 조용히 무시되며 추가 리스크는 없습니다. |
| **과거 판정 유입 (Stale)** | `report_ref`는 같으나 현재 DB보다 `verdict_seq`가 낮음. 워커가 이 또한 `code="stale_revision"`으로 분류해 `archive/revisions/`로 안전 보관 | 늦게 도착한 과거 판정이 최신 상태를 덮어쓰는 것을 원천 방어합니다. 조용히 무시됩니다. |
| **판정 파일 미수신 (Timeout)** | 퀘스트를 보고했으나 폴링 디렉토리에 `.verdict.json`이 오지 않음 | **[운영 리스크 완화]** 10분 이상 지연 시 UI의 `quest_status_summary` 필드에 `is_stale=True` 및 경고 메시지가 표시됩니다. 사용자는 이를 통해 에이전트 프로세스(queue_worker 등)의 구동 여부를 즉시 인지할 수 있습니다. |
| **워커가 꺼져있을 때** | `scripts/queue_worker.py` 프로세스가 다운되거나 PC가 꺼져 있는 상태 | 외부 에이전트가 생성한 `.verdict.json` 파일들은 파일시스템 디렉토리에 고스란히 쌓여있습니다. 유실되지 않으며, 다음 번 `.bat` 부팅 시 즉시 순차적으로 전부 흡수(Ingest)하여 DB를 최신화합니다. |

## 7. 기존 문서 연결
- 데이터베이스 반영 규칙은 `docs/05-data-schema.md`의 `quests`, `plan_items`, `decision_records` 스키마를 따른다.
- 세션 복기 프로세스는 `docs/07-cmd-session-workflow.md`와 연결되어 `session_exports/` 구조를 공유한다.
- 모델 커맨드 규칙은 `docs/06-implementation-handoff.md`의 `CONTROL_TOWER_VERDICT_COMMAND` 지침을 상속한다.
