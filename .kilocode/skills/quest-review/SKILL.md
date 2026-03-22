---
name: quest-review
description: "현재 퀘스트 결과를 done/partial/hold로 평가하고, 재시작 전략과 다음 퀘스트를 제안."
---

# quest-review

## 언제 쓰는지

- 퀘스트 작업 완료 후 ("평가해줘", "이거 done으로 마킹")
- 중간 점검 ("지금 어디까지 왔어?")
- 퀘스트를 보류해야 할 때 ("이거 hold로 넘겨줘")
- 사용자가 quest 보고를 요청할 때

## 입력으로 기대하는 정보

1. 현재 퀘스트 정보 (`current_state`의 `current_quest_id`)
   - `title`, `completion_criteria`, `why_now`
   - `metadata_json`의 `report` (이전 보고가 있다면)
2. 작업자가 제공하는 보고 내용:
   - `work_summary`: 한 일
   - `remaining_work`: 남은 일
   - `blocker`: 막힌 점
   - `self_assessment`: 자기 판단 (`done` / `partial` / `hold`)
3. 오늘 plans (다음 퀘스트 후보 탐색용)

## 실행 절차

### Step 1: 현재 퀘스트 확인

서버 기동 시:

```
GET http://localhost:4310/api/current-state
```

`current_quest_id`가 비어 있으면 "현재 퀘스트 없음. 먼저 퀘스트를 시작하세요" 안내 후 종료.

활성 퀘스트가 있으면 다음 정보를 확인:
- `current_quest_title`
- `current_quest_completion_criteria`
- `quest_status_summary` (pending/awaiting 판정 여부)

### Step 2: 보고 수집

사용자에게 다음을 요청한다 (이미 제공된 경우 생략):
1. 한 일을 한 줄로 요약
2. 아직 안 된 것
3. 막힌 점 (있다면)
4. 자기 평가 (`done` / `partial` / `hold`)

### Step 3: 보고서 제출

서버 기동 시 API로 제출한다:

```
POST http://localhost:4310/api/quests/report
Content-Type: application/json

{
  "quest_id": "{current_quest_id}",
  "work_summary": "...",
  "remaining_work": "...",
  "blocker": "...",
  "self_assessment": "partial",
  "session_id": "{optional}"
}
```

서버 미기동 시 직접 스크립트를 실행한다:

```bash
python -c "
from scripts.verdict_ops import report_quest_progress
result = report_quest_progress(
    quest_id='{quest_id}',
    work_summary='...',
    remaining_work='...',
    blocker='...',
    self_assessment='partial',
)
print(result)
"
```

이 단계가 끝나면 quest 상태가 `pending`으로 변경되고, preliminary AI verdict가 metadata에 저장된다.

### Step 4: Verdict 판단 기준

completion_criteria 대비 보고 내용을 분석한다:

| 상황 | 판정 |
|------|------|
| completion_criteria 모두 충족 | `done` |
| 핵심 산출물 일부 완료 | `partial` |
| 아직 착수 못했거나 막힘 | `hold` |

AI 판정 결과는 파일 기반 파이프라인(`data/queue/`)을 통해 자동으로 ingest된다.
또는 사용자가 직접 verdict를 확정할 수 있다.

Verdict 확정 시 API:

```
POST http://localhost:4310/api/verdicts/ingest
Content-Type: application/json

{
  "quest_id": "...",
  "verdict": "done",
  "reason": "...",
  "restart_point": "...",
  "next_quest_hint": "...",
  "plan_impact": "..."
}
```

### Step 5: 다음 퀘스트 제안

1. 현재 퀘스트의 `next_quest_hint` 확인
2. `GET http://localhost:4310/api/plans`에서 `today` 버킷의 남은 항목 탐색
3. `short_term`에서 가져올 항목 확인
4. 제안 이유를 반드시 설명한다

### Step 6: 결과 출력

```
퀘스트 평가 — {퀘스트 제목}

판정: {done|partial|hold}

왜 이 판정인가
- {completion_criteria 대비 분석}

남은 것
- {아직 안 된 것}

재시작 지점
- {다시 시작한다면 어디서부터}

제안하는 계획 변경
- {plans에 반영할 변경이 있다면}

---

다음 퀘스트 제안
> {다음 퀘스트 제목}
> 이유: {왜 이것이 지금 적절한가}
```

## 출력 형식

- 한국어로 출력한다.
- 현재 퀘스트 상태를 항상 맨 위에 표시한다.
- Verdict에는 반드시 포함한다: 왜 이 판정인가, 남은 것, 재시작 지점, 제안하는 계획 변경.

## 실패/누락 시 fallback

| 상황 | fallback |
|------|----------|
| `current_quest_id` 없음 | "활성 퀘스트 없음. ops-brief에서 메인 미션을 먼저 설정하세요" |
| 서버 미기동 | `scripts/verdict_ops.py` 직접 import하여 사용 |
| `completion_criteria` 없음 | 사용자의 `self_assessment`를 기준으로 판정 |
| 다음 퀘스트 후보 없음 | `short_term`에서 우선순위 높은 항목 추천, 없으면 "다음 퀘스트를 직접 정의하세요" |
| AI 판정 대기 중 | "판정 대기 중. `scripts/queue_worker.py`가 verdict를 처리 중입니다" 안내 |

## 관련 파일/스크립트

- `scripts/verdict_ops.py` — `report_quest_progress()`, `apply_verdict()`, `evaluate_quest()`
- `scripts/current_quest_ops.py` — `start_current_quest_from_main_mission()`
- `scripts/db_state.py` — `refresh_current_state()`
- `scripts/queue_worker.py` — 파일 기반 판정 큐 처리
- `public/app.js` — `handleQuestEvaluation()` (UI 참조)
- `.kilo/rules-ops-quest/01-quest-rules.md` — ops-quest 모드 세부 규칙
- `AGENTS.md` — Quest Model 섹션

## 제한 사항

- Verdict는 **제안만** 한다. 파일 기반 파이프라인의 AI 판정은 자동이지만, 사용자 확인이 우선이다.
- 메인 미션을 변경하지 않는다. 변경이 필요하면 대화로 제안한다.
- `hold` 판정 시 반드시 `restart_point`를 기록한다.
- 보고 내용은 `quests.metadata_json`에 저장된다. 직접 파일을 수정하지 않는다.
