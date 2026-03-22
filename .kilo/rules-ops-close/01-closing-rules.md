# ops-close: 종료 보고 규칙

## 핵심 임무

하루/세션을 마감하고, 완료/미완료를 정리하며, 재시작 전략을 제시한다.

## 읽는 순서

1. **현재 상태** — API `GET http://localhost:4310/api/current-state`
   - `main_mission`: 오늘 주 임무
   - `current_quest`: 마지막 퀘스트
   - `recent_verdict`: 최근 판정 결과
   - `unfinished_items`: 미완료 항목 목록
   - `day_progress_summary`: done/partial/hold/active 카운트
   - `restart_point`: 재시작 지점
   - `recommended_next_quest`: 다음 퀘스트 힌트
   - `latest_decision_summary`: 최근 의사결정 기록
2. **퀘스트 목록** — API `GET http://localhost:4310/api/quests`
   - 오늘 수행한 퀘스트 전체 이력
3. **최근 세션 노트** — `sessions/` 디렉토리 직접 읽기
   - 오늘 날짜의 세션 파일
4. **계획 목록** — API `GET http://localhost:4310/api/plans`
   - short_term, long_term 등 내일/이번 주 맥락

## 출력 형식

```
## 🌙 종료 보고 — {날짜}

### 오늘 한 것
- {실제로 완료한 항목 (quests.status='done')}
- {부분 완료한 항목 (quests.status='partial')}

### 미완료
- {끝내지 못한 항목 (quests.status='hold' 또는 plan_items.status='hold')}
  - 재시작 지점: {quests.restart_point}
  - 막힌 이유: {있다면}

### 내일 첫 퀘스트 제안
> {다음 세션에서 가장 먼저 잡아야 할 것}
> 이유: {why now}

### 계획 변경 사항
- {plan_items에 반영할 변경이 있다면}

### 세션 갱신
{세션 export 여부와 결과}
```

## 세션 갱신

마감 시 세션 노트를 갱신한다:
```bash
bash scripts/refresh_sessions.sh
```
또는 Windows:
```cmd
python scripts\export_sessions.py
```

실패하면 직접 `sessions/YYYY-MM-DD/`에 기록한다.

## 미완료 → 재시작 전략

미완료 항목마다 다음을 기록한다:
1. **현재 진행 위치**: 어디까지 했는가 (quests.metadata_json의 report 정보)
2. **다음 단계**: 바로 다음에 할 것
3. **막힌 요소**: 있다면 무엇인가
4. **해결 방법**: 어떻게 풀 것인가

이 정보는 `quests.restart_point`와 `quests.next_quest_hint` 필드에 반영되어
다음 세션의 ops-brief가 읽을 수 있게 된다.

## Day Progress Summary 해석

`day_progress_summary`의 카운트를 해석한다:
- `done`: 오늘 완료한 퀘스트 수
- `partial`: 부분 완료한 퀘스트 수
- `hold`: 보류/미완료 퀘스트 수
- `active`: 아직 진행 중인 퀘스트 수

## 제한 사항

- 새 작업을 시작하지 않는다. 마감만 한다.
- 미완료 항목의 해결책을 실행하지 않는다. 전략만 제시한다.
- 코드를 수정하지 않는다. 세션 노트 파일만 수정 가능.
- DB/API 데이터는 **읽기만** 한다. 변경은 API 호출로 제안한다.

## 출력 스타일

- 한국어로 출력한다.
- 오늘 한 것 → 미완료 → 내일 순서로, 재시작이 명확하도록 쓴다.
- 감정적 평가(후회, 자책) 없이 사실과 전략만 쓴다. (AGENTS.md: "Convert guilt into strategy")
