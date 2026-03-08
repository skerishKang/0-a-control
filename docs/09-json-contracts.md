# 09. Report & Verdict JSON 규약

## 1. 공통 메타데이터
```json
{
  "report_id": "20260309T053100Z-q123-s456",
  "quest_id": "q123",
  "session_id": "s456",
  "generated_at": "2026-03-09T05:31:00Z",
  "timezone": "Asia/Seoul",
  "agent_name": "windsurf"
}
```
- `report_id`: 파일명과 동일하게 ISO8601 basic + quest/session 조합.
- `session_id`: 세션 없는 수동 보고 시 `_` 사용.
- `agent_name`: 보고/판정을 수행한 에이전트 식별자.

## 2. Report JSON 스키마
```json
{
  "schema_version": "1.0",
  "report": {
    "quest_id": "q123",
    "quest_title": "데이터 모델 정리",
    "completion_criteria": "docs/05 데이터 스키마 설명 정리",
    "work_summary": "테이블 정의 보완 및 current_state 키 작성",
    "remaining_work": "데이터 릴레이션 도표 추가",
    "blocker": "diagram 템플릿 미정",
    "self_assessment": "partial",
    "plan_links": [
      { "bucket": "today", "plan_item_id": "p001" }
    ],
    "attachments": [
      { "type": "file", "path": "session_exports/20260309-q123.md" }
    ]
  }
}
```
필드 규칙:
- `plan_links`: 다중 계획 버킷과 연결. bucket 값은 `today|short_term|long_term|recurring|dated`.
- `attachments`: UI/CLI가 생성한 추가 자료 경로.
- `blocker`는 없으면 빈 문자열.

## 3. Verdict JSON 스키마
```json
{
  "schema_version": "1.0",
  "report_ref": "20260309T053100Z-q123-s456",
  "verdict": {
    "status": "partial",
    "reason": "진행은 있었으나 remaining_work가 명확함",
    "restart_point": "데이터 릴레이션 도표 작성 지점",
    "next_hint": "도표 템플릿 확정 후 첫 테이블부터 작성",
    "plan_impact": {
      "today": "퀘스트 유지",
      "short_term": "관련 계획 영향 없음",
      "long_term": "--",
      "recurring": "--",
      "dated": "--"
    },
    "ai_tags": ["data", "doc"],
    "confidence": 0.78
  },
  "judge": {
    "provider": "cli",
    "model": "gemini-2.5-flash",
    "prompt_hash": "sha256:...",
    "latency_ms": 5210
  }
}
```
필드 규칙:
- `status`: `done|partial|hold` (소문자).
- `plan_impact`: 각 버킷별 영향 코멘트. 사용하지 않으면 `"--"`.
- `ai_tags`: 판정이 감지한 키워드.
- `confidence`: 0.0~1.0 float.
- `prompt_hash`: 보고 + 프롬프트 요약 해시로 재현성 확보.

## 4. 상태 전이 규칙

### 4.1 active/pending/hold/partial 전이 테이블
| 입력 상태 | 이벤트 | 결과 quests.status | plan_items.status | current_state 반영 | UI 노출 방식 |
| --- | --- | --- | --- | --- | --- |
| `active` | **보고 제출** → pending | `pending` | 그대로 (`active`) | `current_state.current_quest`는 동일 퀘스트이지만 `recommended_next_quest`는 비움. pending 상태 메타를 `current_state.restart_point`에 표시 | 메인 카드 유지 + "판정 대기" 배지 추가 |
| `active` | verdict=`done` | `done` | `done` | `current_state.recent_verdict` 갱신, `current_quest`는 다음 후보 탐색 | 메인 카드 교체, 완료 표시 |
| `active` | verdict=`partial` | `partial` | `partial` | `current_state.restart_point`, `next_quest_hint` 업데이트 | 메인 카드 유지, 진척 배지 |
| `active` | verdict=`hold` | `hold` | `hold` | `current_state.current_quest`가 hold로 표시되고 `recommended_next_quest`에 대체 후보 요청 | 메인 카드 유지+"정지" 배지 |
| `pending` | verdict=`done` | `done` | `done` | pending 배지 제거, recent verdict 업데이트 | 메인 카드 완료 표시 |
| `pending` | verdict=`partial` | `partial` | `partial` | pending 플래그 해제, `current_state.restart_point` 반영 | 메인 카드 그대로, "진행 중" 배지 |
| `pending` | verdict=`hold` | `hold` | `hold` | pending 플래그 해제, `recommended_next_quest`에 대체 힌트 | 메인 카드 그대로, hold 배지 |
| `hold` | **재보고** | `pending` | `hold` 유지 | `current_state.current_quest`는 동일하지만 pending 배지를 덧붙임 | 메인 카드 hold+pending 보조 배지 |
| `partial` | **재보고** | `pending` | `partial` 유지 | `current_state.restart_point` 업데이트, pending 배지 | 메인 카드 partial+pending 보조 배지 |

### 4.2 today/short/long/recurring/dated 규칙
- pending 중에는 today 버킷 우선순위는 유지하되, `current_state.recommended_next_quest`는 비워둔다.
- verdict 결과가 `done`이면 해당 버킷에서도 `done`으로 마킹해 다음 후보를 자동 선택한다.
- hold 상태는 today에서 대체 퀘스트 추천을 강제하고, dated 버킷에는 "hold 사유"를 기입해 압박 메시지를 갱신한다.

### 4.3 상태 전이 예시
```
이전 상태: quests.status=active, plan_items.status=active
이벤트: 보고 제출 → pending
=> quests.status=pending, plan_items.status=active
=> current_state.current_quest = 동일 ID + pending flag
=> UI: 메인 카드 유지 + "판정 대기" 배지

pending 상태에서 verdict.status=partial
=> quests.status=partial, plan_items.status=partial
=> current_state.restart_point/next_quest_hint 갱신
=> pending 배지 제거, partial 배지로 교체
```

## 5. 교차 참조 규칙
- `report.report_id` == `verdict.report_ref`.
- DB ingest 시 `quests.metadata_json.report_id`에 저장해 추적 가능.
- `session_exports/`의 Markdown Brief는 같은 `report_id`를 Front Matter에 기입하여 링크 유지.

## 6. Validation 체크리스트
1. JSON Schema (정적)  
   - `schema_version` 문자열.
   - required 필드: report(`quest_id`, `quest_title`, `completion_criteria`, `work_summary`). verdict(`report_ref`, `verdict.status`, `reason`).
2. 논리 검증 (ingest 단계)  
   - `quest_id` 존재 및 active 여부.
   - `verdict.status`가 허용 값인지 확인.
   - `plan_links`가 실제 plan_items에 존재하는지 확인. 
3. 중복 방지  
   - `report_id`+`verdict.status` 조합으로 unique key를 만들어 최초 성공 판정만 DB 반영.

## 7. 테스트 케이스
| 케이스 | 초기 상태 | 이벤트 | 기대 결과 (quests / plan_items) | current_state | UI |
| --- | --- | --- | --- | --- | --- |
| pending만 있을 때 | today 버킷에 pending 퀘스트 1개 | 없음 | quests/plan_items 모두 pending/active | `current_quest`=pending 퀘스트, `recommended_next_quest` 비움, `restart_point`는 pending 배지 문구 | 메인 카드 유지 + 노란색 판정 대기 배지 |
| hold만 있을 때 | today 버킷 hold 1개 | 없음 | quests=hold, plan_items=hold | `current_quest`=hold, `recommended_next_quest`에 대체 필요 힌트, `recent_verdict` hold 반영 | 메인 카드 유지 + 붉은 hold 배지, pending 없음 |
| pending → partial verdict | active→pending 후 verdict=partial | 보고 제출 + 외부 partial | quests=partial, plan_items=partial | `restart_point`,`next_quest_hint` 업데이트, pending 플래그 제거 | 메인 카드 유지 + 초록 진행 배지 |
| pending → done verdict | active→pending 후 verdict=done | 보고 제출 + 외부 done | quests=done, plan_items=done | `recent_verdict` 최신, `current_quest` 다음 후보로 이동 | 메인 카드 완료 처리 후 다음 카드로 교체 |
| pending → hold verdict | active→pending 후 verdict=hold | 보고 제출 + 외부 hold | quests=hold, plan_items=hold | pending 제거, `recommended_next_quest`에 대체 후보, `restart_point` hold 사유 명시 | 메인 카드 유지 + hold 배지 + 대체 권고 |

## 8. UI 팀 가이드
- pending 상태는 메인 카드 자체를 바꾸지 말고 보조 배지(예: "판정 대기")로만 노출한다.
- 주 임무 카드와 현재 퀘스트 카드는 항상 1개씩 유지하고, pending 여부는 카드 내 보조 텍스트로 표시한다.

## 9. 기타
- JSON은 UTF-8, LF 사용.
- 500줄 제한을 고려해 구조화된 섹션 유지.
- 확장 필드는 `metadata` 오브젝트에 자유롭게 추가하되, ingest 전에 화이트리스트 검사.
