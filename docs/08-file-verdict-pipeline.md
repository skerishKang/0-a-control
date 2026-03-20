# 08. 파일 기반 퀘스트 판정 파이프라인

## 1. 목적과 전제
- CMD 세션과 UI는 **퀘스트 보고(report)** 를 JSON 파일로 저장한다.
- 외부 IDE/CMD 에이전트가 동일 보고서를 읽고 **판정(verdict)** JSON을 작성한다.
- `scripts/queue_worker.py`가 verdict 파일을 읽어 SQLite 상태를 갱신한다.
- 모델 호출은 내부 서버가 아닌 외부 커맨드로 위임해 벤더 종속을 최소화한다.

## 2. 파이프라인 단계
1. **보고 생성 (UI or CMD)**
   - `/api/quests/report` 호출 또는 CLI 스크립트가 `data/queue/reports/`에 JSON을 드랍한다.
   - 파일명: `{ts}-{questId}-{sessionId}.report.json` (sessionId 없으면 `_`).
2. **보고 고정**
   - report 파일은 수정 금지. 필요한 보정은 새 report 생성으로 처리.
3. **외부 에이전트 판정**
   - 외부 에이전트나 스크립트가 `data/queue/reports/`를 읽어 판정 JSON을 작성한다.
   - 읽은 report는 동일 base name으로 `data/queue/verdicts/`에 verdict JSON을 기록한다.
4. **본체 수집 및 DB 반영**
   - `scripts/queue_worker.py`가 `data/queue/verdicts/`를 폴링해 새 verdict를 `quests`/`plan_items`에 반영한다.
   - 성공 시 verdict 파일은 `data/queue/processed/verdicts/`로 이동한다.
5. **세션 내보내기**
   - 필요한 경우 `session_exports/`에 요약 Markdown + JSON snapshot을 생성해 다른 에이전트가 재시작점을 공유한다.

## 3. 현재 디렉토리 역할
| 디렉토리 | 현재 역할 | 샘플 파일 | 현재 구현 상태 |
| --- | --- | --- | --- |
| `data/queue/reports/` | 사용자가 제출한 진행 보고 원본. | `20260309T053100Z-q123-s456.report.json` | 보고 생성 시 파일이 추가된다. 자동 정리/이동 정책은 아직 없다. |
| `data/queue/verdicts/` | 외부 에이전트가 작성한 판정 JSON 입력 큐. | `20260309T053145Z-q123-s456.verdict.json` | `queue_worker.py`가 이 디렉토리를 폴링한다. |
| `data/queue/processed/verdicts/` | 성공적으로 ingest된 verdict 보관. | `20260309T053145Z-q123-s456.verdict.json` | 현재 verdict 파일만 이동한다. report 파일 자동 이동은 구현돼 있지 않다. |
| `data/queue/processed/duplicates/verdicts/` | 중복 verdict 보관. | `20260309T053145Z-q123-s456.verdict.json` | 현재 구현됨. |
| `data/queue/failed/verdicts/` | JSON 파손 또는 필수 필드 오류 verdict 격리. | `20260309T053145Z-q123-s456.verdict.json` | 현재 구현됨. |
| `data/queue/archive/revisions/` | stale revision verdict 보관. | `20260309T053145Z-q123-s456.ab12cd34.verdict.json` | 현재 구현됨. |
| `session_exports/` | 특정 세션·퀘스트의 export 산출물 저장 위치. | `20260309-q123-session.md` | 필요 시 생성된다. 자동 보관 정책은 아직 문서 수준이다. |

## 4. 파일 컨벤션
- **Base name**: `{ISO8601 basic}-{questId}-{sessionIdOr_}`.
- **확장자**: `.report.json`, `.verdict.json`, `.md` (export).
- **메타데이터**: JSON 내부 `quest_id`, `session_id`, `report_id`로 상호 참조.
- **동시성**: 현재 구현에는 공용 `*.lock` 프로토콜이 없다. 다중 작성자/다중 워커 충돌 방지는 향후 과제다.

## 5. 상태 플로우 예시
```mermaid
digraph G {
  report["report JSON 생성"] -> verdictAgent["외부 에이전트 판정"] -> ingest["queue_worker ingest"];
  ingest -> dbUpdate["quests.status & plan_items.status 갱신"];
  dbUpdate -> currentState["current_state 테이블 반영"];
  ingest -> processed["data/queue/processed/ 이동"];
}
```
- 자세한 상태 전이는 `docs/09-json-contracts.md` 참고.

## 6. 현재 보장 범위

현재 코드가 실제로 보장하는 범위는 아래와 같다.

- 손상된 verdict JSON 또는 필수 필드 누락 verdict는 `data/queue/failed/verdicts/`로 격리된다.
- 동일 `report_ref`와 동일 판정, 동일 `verdict_seq`의 중복 verdict는 DB에 재반영되지 않고 `data/queue/processed/duplicates/verdicts/`로 이동한다.
- 더 오래된 `verdict_seq`가 뒤늦게 도착하면 최신 상태를 덮어쓰지 않고 `data/queue/archive/revisions/`로 이동한다.
- 워커가 꺼져 있는 동안 들어온 verdict 파일은 `data/queue/verdicts/`에 남아 있고, 워커 재시작 뒤 다시 스캔 대상이 된다.
- 퀘스트가 `pending` 상태로 오래 머물면 `current_state.quest_status_summary.is_stale`와 경고 문구가 계산된다.

## 7. 검증 및 테스트 도구

이 파이프라인의 무결성을 검증하기 위해 다음 도구들을 사용한다.

- **자동 단위 테스트**: `tests/test_01_pipeline_flow.py` 등. `tempfile` 기반 환경에서 파일 큐-워커-DB 반영 흐름을 자동 검증한다. (CI 범위)
- **수동 파이프라인 시뮬레이션**: `tests/manual/run_pipeline_test.sh`. 로컬 환경에서 전체 흐름을 수동으로 재현한다.
- **DB 상태 직접 확인**: `tests/manual/db_verify/` 아래 스크립트들. ingestion 후 실제 DB 반영 내역을 수동으로 검사할 때 사용한다.

## 8. 현재 비보장 범위

아래 항목은 아직 구현되지 않았거나, 수동 운영에 의존한다.

- GitHub Actions나 다른 CI 환경에서의 자동 실행 보장
- report 파일의 자동 아카이브/회전 정책
- verdict/report 쌍 단위의 완전한 원자적 처리
- 공용 락 파일 기반 다중 작성자 조정
- failed verdict의 자동 재처리 또는 재시도 큐
- 운영자용 재처리 CLI와 문제 해결 절차의 표준화

## 8. 실패 및 재처리 전략 (운영 시나리오)

현재 `0-a-control`의 파이프라인은 파일 기반 큐를 통해 장애 지점을 분리합니다. 워커 프로세스가 중단되어도 파일은 보존되며, 워커 재시작 시 디렉토리에 남은 파일들을 순차적으로 읽어 들입니다. 이는 고가용성(High-Availability)이나 자동 복구를 보장하는 구조는 아닙니다.

| 케이스 | 감지 포인트 및 워커 처리 | 잔여 리스크 및 대응 (DB/UI) |
| --- | --- | --- |
| **JSON 파손 (Malformed)** | `json.loads` 실패 또는 필수 필드 누락 발생. 워커는 해당 파일을 `data/queue/failed/verdicts/`로 즉시 격리 | 퀘스트 상태는 여전히 `pending`으로 남아 있다. 현재는 자동 재처리 대신 수동 재보고 또는 수동 재생성이 필요하다. |
| **중복 처리 (Duplicate)** | 동일 `report_ref`, 같은 판정 결과, 동일한 `verdict_seq` 감지. 워커가 `DuplicateVerdict` 예외를 내고 `data/queue/processed/duplicates/verdicts/`로 파일 이동 | DB 변화 없이 무시된다. 중복 verdict를 자동 병합하거나 통계화하는 기능은 아직 없다. |
| **과거 판정 유입 (Stale)** | `report_ref`는 같으나 현재 DB보다 `verdict_seq`가 낮음. 워커가 이 또한 `code="stale_revision"`으로 분류해 `data/queue/archive/revisions/`로 보관 | 늦게 도착한 과거 판정이 최신 상태를 덮어쓰지 못하게 막는다. |
| **판정 파일 미수신 (Timeout)** | 퀘스트를 보고했으나 폴링 디렉토리에 `.verdict.json`이 오지 않음 | **[운영 리스크 완화]** 10분 이상 지연 시 UI의 `quest_status_summary` 필드에 `is_stale=True` 및 경고 메시지가 표시됩니다. 사용자는 이를 통해 에이전트 프로세스(queue_worker 등)의 구동 여부를 즉시 인지할 수 있습니다. |
| **워커가 꺼져있을 때** | `scripts/queue_worker.py` 프로세스가 중단된 상태 | 외부 에이전트가 생성한 `.verdict.json` 파일들은 디렉토리에 유지됩니다. 이후 워커가 다시 구동될 때 해당 파일들을 스캔하여 DB에 반영을 시도합니다. |

## 9. 기존 문서 연결
- 데이터베이스 반영 규칙은 `docs/05-data-schema.md`의 `quests`, `plan_items`, `decision_records` 스키마를 따른다.
- 세션 복기 프로세스는 `docs/07-cmd-session-workflow.md`와 연결되어 `session_exports/` 구조를 공유한다.
- 모델 커맨드 규칙은 `docs/06-implementation-handoff.md`의 `CONTROL_TOWER_VERDICT_COMMAND` 지침을 상속한다.
