# 08. 파일 기반 퀘스트 판정 파이프라인

## 1. 목적과 전제
- CMD 세션과 UI는 **퀘스트 보고(report)** 를 JSON 파일로 저장한다.
- 외부 IDE/CMD 에이전트가 동일 보고서를 읽고 **판정(verdict)** JSON을 작성한다.
- 본체 서버는 verdict 파일을 감지하여 SQLite 상태를 갱신한다.
- 모델 호출은 내부 서버가 아닌 외부 커맨드로 위임해 벤더 종속을 최소화한다.

## 2. 파이프라인 단계
1. **보고 생성 (UI or CMD)**  
   - `/api/quests/report` 호출 또는 CLI 스크립트가 `quest_reports/`에 JSON을 드랍한다.  
   - 파일명: `{ts}-{questId}-{sessionId}.report.json` (sessionId 없으면 `_`).
2. **보고 고정**  
   - report 파일은 수정 금지. 필요한 보정은 새 report 생성으로 처리.
3. **외부 에이전트 판정**  
   - 에이전트 워커는 `quest_reports/`를 폴링/워치.  
   - 읽은 report는 동일 base name으로 `quest_verdicts/`에 verdict JSON을 기록한다.
4. **본체 수집 및 DB 반영**  
   - 서버 스케줄러가 `quest_verdicts/`를 스캔해 새 verdict를 `quests`/`plan_items`에 반영한다.  
   - 성공 시 report/verdict 세트를 `processed/`로 이동한다.
5. **세션 내보내기**  
   - 필요한 경우 `session_exports/`에 요약 Markdown + JSON snapshot을 생성해 다른 에이전트가 재시작점을 공유한다.

## 3. 디렉토리 역할
| 디렉토리 | 역할 | 샘플 파일 | 보관 정책 |
| --- | --- | --- | --- |
| `quest_reports/` | 사용자가 제출한 진행 보고 원본. 수정 금지. | `20260309T053100Z-q123-s456.report.json` | 당일 + 2일 보유 후 `processed/` 이동 |
| `quest_verdicts/` | 외부 에이전트가 작성한 판정 JSON. | `20260309T053145Z-q123-s456.verdict.json` | ingest 완료 시 `processed/` 이동 |
| `session_exports/` | 특정 세션·퀘스트의 briefing, replay 데이터를 저장. 다른 에이전트 재진입용. | `20260309-q123-session.md` | 7일 보관 후 `archive/` 이동 |
| `processed/` 또는 `archive/` | 이미 ingest된 report+verdict 묶음과 만료된 export를 장기 보관. | `processed/2026/03/09/q123/` | 월 단위 rotate, 필요 시 `archive/`로 zip |

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
  ingest -> processed["processed/ 이동"];
}
```
- 자세한 상태 전이는 `docs/09-json-contracts.md` 참고.

## 6. 실패 및 재처리 전략
| 케이스 | 감지 포인트 | 대응 |
| --- | --- | --- |
| verdict 없음 (타임아웃) | report 생성 후 `VERDICT_TIMEOUT_MIN` 초 경과 | 서버가 alert 로그 남기고 동일 report를 `pending` 큐로 재등록. 외부 에이전트는 `quest_reports/pending/` 우선 처리 |
| JSON 파손 | ingest 시 `json.loads` 실패 | 해당 verdict 파일을 `quest_verdicts/failed/`로 이동, 오류 상세를 `session_exports/` 로그에 기록. Report는 그대로 유지해 재판정 가능 |
| 중복 처리 | 동일 `report_id`로 여러 verdict 감지 | 최초 성공 verdict만 적용. 이후 파일은 `processed/duplicates/` 이동 및 로그 남김 |
| 동일 report 재판정 | 사용자가 명시적으로 재판정 요청해 새 verdict가 들어온 경우 | `verdict_seq` 증가 값을 확인해 최근 판정만 활성화. 이전 verdict는 `archive/revisions/`에 보관 |

## 7. 기존 문서 연결
- 데이터베이스 반영 규칙은 `docs/05-data-schema.md`의 `quests`, `plan_items`, `decision_records` 스키마를 따른다.
- 세션 복기 프로세스는 `docs/07-cmd-session-workflow.md`와 연결되어 `session_exports/` 구조를 공유한다.
- 모델 커맨드 규칙은 `docs/06-implementation-handoff.md`의 `CONTROL_TOWER_VERDICT_COMMAND` 지침을 상속한다.
