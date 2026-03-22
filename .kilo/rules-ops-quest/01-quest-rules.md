# ops-quest: 퀘스트 실행 규칙

## 핵심 임무

현재 퀘스트에 집중하고, 진행 상황을 추적하며, 결과를 평가한다.

## 읽는 순서

1. **현재 상태** — API `GET http://localhost:4310/api/current-state`
   - `current_quest`: 현재 퀘스트 (quests 테이블)
   - `main_mission`: 소속 메인 미션 (plan_items 테이블)
   - `quest_status_summary`: 퀘스트 상태 상세 (pending/awaiting verdict/stale 여부)
   - `recommended_next_quest`: 다음 퀘스트 힌트
   - `restart_point`: 재시작 지점
2. **퀘스트 목록** — API `GET http://localhost:4310/api/quests`
3. **최근 세션 노트** — `sessions/` 디렉토리 직접 읽기
   - 오늘 날짜의 세션 파일 확인
4. **판정 대기 중인 보고서** — `data/queue/*.report.json` 파일 읽기
5. 필요 시 관련 코드/파일

## Quest Model (AGENTS.md 준수)

모든 퀘스트는 다음을 포함해야 한다:
- **title**: 퀘스트 제목
- **parent mission**: 어떤 메인 미션에 속하는가 (plan_item_id)
- **why now**: 왜 지금 이것을 하는가
- **completion criteria**: 끝났다고 판단하는 기준
- **next quest candidates**: 다음에 올 수 있는 퀘스트 후보 (next_quest_hint)

## Verdict 형식

퀘스트 평가는 반드시 다음 중 하나로 반환한다:
- `done` — 완료
- `partial` — 부분 완료
- `hold` — 보류

각 verdict에는 반드시 포함한다:
```
## Verdict: {done|partial|hold}

- **왜 이 판정인가**: {이유}
- **남은 것**: {아직 안 된 것}
- **재시작 지점**: {다시 시작한다면 어디서}
- **제안하는 계획 변경**: {plan_items에 반영할 변경}
```

## 판정 프로세스 (실제 코드 흐름 반영)

퀘스트 보고/판정은 파일 기반 파이프라인을 따른다:
1. 사용자가 퀘스트 진행 보고 → API `POST /api/quests/report`
   - 보고서가 `data/queue/`에 JSON으로 저장됨
   - AI가 예비 판정(preliminary_verdict)을 생성
2. 외부 에이전트가 보고서를 읽고 최종 판정 생성
3. 판정 적용 → API `POST /api/quests/evaluate`
   - quests 테이블 status 업데이트
   - decision_records 테이블에 기록
   - current_state 테이블 갱신

ops-quest 모드에서는 이 중 "제안" 단계를 수행한다. 실제 API 호출은 사용자/시스템이 한다.

## 다음 퀘스트 제안

진행 후 다음 퀘스트를 제안할 때:
1. 현재 퀘스트의 completion criteria가 충족되었는가?
2. current_state의 `unfinished_items`에서 남은 항목
3. plan_items에서 bucket='short_term'인 항목 중 다음 후보
4. `recommended_next_quest` 필드의 기존 힌트 활용
5. 제안 이유를 반드시 설명한다

## 제한 사항

- 퀘스트 판정은 **제안만** 한다. 사용자가 확정한다. (API 호출은 사용자/시스템이 수행)
- 메인 미션을 변경하지 않는다. 변경이 필요하면 대화로 제안한다.
- 코드 수정은 퀘스트 목표와 직접 관련된 경우만 한다.
- `data/queue/`의 보고서 파일은 수정하지 않는다.

## 출력 스타일

- 한국어로 출력한다.
- 현재 퀘스트 상태를 항상 맨 위에 표시한다.
- 진행률/상태를 시각적으로 표현한다.
- `quest_status_summary.is_stale`이 true면 경고를 표시한다.
