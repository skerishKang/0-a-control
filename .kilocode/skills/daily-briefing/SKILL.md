---
name: daily-briefing
description: "current_state + plans + recent sessions를 읽고 아침 브리핑을 생성한다. 메인 미션 1개와 즉시 시작 액션 1개를 제안."
---

# daily-briefing

## 언제 쓰는지

- 아침 작업 시작 시 ("브리핑해줘", "오늘 뭐하지")
- 세션 시작 후 첫 지시
- `day_phase`가 `morning`일 때 자동 제안 가능
- 사용자가 "오늘 메인 미션 정해줘"라고 요청

## 입력으로 기대하는 정보

1. 서버 기동 상태 (`http://localhost:4310`)
2. `current_state` API 결과 (main_mission, current_quest, day_phase, unfinished, due_items)
3. `plans` API 결과 (today, dated, short_term 버킷)
4. `sessions/` 폴더의 최근 3일 노트

## 실행 절차

### Step 1: 현재 상태 읽기

서버가 기동 중이면 API를 사용한다:

```
GET http://localhost:4310/api/current-state
```

서버 미기동이면 직접 스크립트를 실행한다:

```bash
python -c "
from scripts.db_state import refresh_current_state
from scripts.db_base import connect
with connect() as conn:
    state = refresh_current_state(conn)
    import json
    print(json.dumps(state, ensure_ascii=False, indent=2, default=str))
"
```

확인 항목:
- `main_mission_title` — 현재 메인 미션이 있는가
- `current_quest_title` — 활성 퀘스트가 있는가
- `day_phase` — morning/in-progress/end-of-day
- `dated_pressure_summary` — 기한 임박 항목
- `top_unfinished_summary` — 미완료 항목
- `restart_point` — 재시작 지점이 있는가

### Step 2: Plans 읽기

```
GET http://localhost:4310/api/plans
```

확인 항목:
- `bucket = 'today'` 항목: 메인 미션 후보
- `bucket = 'dated'` 항목 중 `due_at`이 가까운 것 (상위 3개)
- `bucket = 'short_term'` 항목: 이번 주 맥락

### Step 3: 최근 세션 확인

```bash
ls -lt sessions/ | head -3
```

최근 3일 폴더에서 마지막 세션의 결정 사항을 확인한다.
- 어제 미완료 퀘스트가 있었는가
- 마지막 verdict 상태는 무엇인가

### Step 4: 메인 미션 선정

AGENTS.md의 3가지 기준을 적용한다:
- **urgent**: 지금 안 하면 문제 되는가?
- **easy to avoid**: 회피하기 쉬운가? (회피하기 쉬운 것을 먼저 잡아라)
- **still mandatory**: 여전히 해야 하는가?

세 조건이 겹치는 하나를 메인 미션으로 제안한다.
여러 후보가 있으면 `dated_pressure_summary`의 첫 번째를 우선한다.

### Step 5: 브리핑 출력

아래 형식으로 출력한다:

```
## 아침 브리핑 — {날짜} ({요일})

### 메인 미션
> **{메인 미션 제목}**
> 이유: {urgent / easy-to-avoid / still-mandatory 기준}

### 즉시 시작 액션
- {작고 바로 실행 가능한 한 가지 행동}

### 긴급 / 마감 임박
- {dated_pressure_summary 상위 3개}

### 어제 미완료
- {top_unfinished_summary 중 yesterday에 해당하는 것}
  - 재시작 지점: {restart_point}

### 참고사항
- {새 정보, 단기/장기 계획 맥락, 최근 세션 결정}
```

## 출력 형식

- 한국어로 출력한다.
- 불필요한 서론/결론 없이 바로 핵심부터 쓴다.
- 숫자와 날짜는 구체적으로 쓴다 ("곧"이 아니라 "3/25까지").

## 실패/누락 시 fallback

| 상황 | fallback |
|------|----------|
| 서버 미기동 | 직접 DB 스크립트로 current_state 조회 |
| current_state 없음 | "상태 없음. 먼저 메인 미션을 설정하세요" 안내 |
| plans가 비어 있음 | `scripts/db_state.py`의 `get_workdiary_priority_candidates()`로 workdiary에서 추천 |
| sessions 없음 | "최근 세션 기록 없음. 브리핑에 제한적 맥락만 제공" |
| day_phase가 morning 아님 | 현재 phase에 맞는 안내 (in-progress면 ops-quest 모드로 전환 제안) |

## 관련 파일/스크립트

- `scripts/db_state.py` — `refresh_current_state()`, `generate_morning_brief()`
- `scripts/plan_ops.py` — `get_plans()`
- `public/app-hero.js` — `renderHeroCard()` (UI 참조)
- `.kilo/rules-ops-brief/01-briefing-rules.md` — ops-brief 모드 세부 규칙
- `AGENTS.md` — Daily Operating Loop / Morning 섹션

## 제한 사항

- 메인 미션은 **제안만** 한다. 사용자가 확정한다.
- 코드를 수정하지 않는다. 운영 데이터만 읽는다.
- `plans/` 파일이 아닌, DB의 plan_items 테이블과 API를 기준으로 한다.
