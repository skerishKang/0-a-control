# ops-brief: 아침 브리핑 규칙

## 읽는 순서 (Memory Hierarchy)

0-a-control은 DB + API + 파일 하이브리드 구조다. 파일이 아닌 데이터는 API 서버를 통해 읽는다.

1. **현재 상태** — API `GET http://localhost:4310/api/current-state`
   - `main_mission`: 오늘 주 임무 (plan_items 테이블, bucket='today')
   - `current_quest`: 현재 진행 중인 퀘스트
   - `recent_verdict`: 최근 판정 결과
   - `due_items`: 기한 임박 항목 (plan_items, bucket='dated')
   - `unfinished_items`: 미완료 항목
   - `day_phase`: 현재 운영 단계 (morning / in-progress / verdict-pending / end-of-day)
   - `quest_status_summary`: 퀘스트 상태 상세
2. **계획 목록** — API `GET http://localhost:4310/api/plans`
   - plan_items 테이블 전체를 bucket별로 정렬해서 반환
3. **최근 세션 노트** — `sessions/` 디렉토리 직접 읽기
   - `sessions/YYYY-MM-DD/*.md` 파일 (Intent/Actions/Decisions/Artifacts 구조)
   - `sessions/INDEX.md` — 전체 세션 인덱스
4. **최근 브리프** — API `GET http://localhost:4310/api/briefs/latest`
5. **워크다이어리 후보** — API `GET http://localhost:4310/api/workdiary/priority-candidates`
   - 상위 폴더에서 자동 추천하는 프로젝트 후보

## 출력 형식

아침 브리핑은 다음 구조로 출력한다:

```
## 🌅 아침 브리핑 — {날짜}

### 메인 미션
> {하나의 메인 미션}
> 이유: {왜 이게 오늘의 메인 미션인지 — urgent/easy-to-avoid/still-mandatory 기준}

### 즉시 시작 액션
- {작고 바로 실행 가능한 한 가지 행동}

### 긴급 / 마감 임박
- {기한이 가까운 항목 (due_items)}

### 어제 미완료
- {끝내지 못한 것 → 재시작 지점 (restart_point)}

### 참고사항
- {새 정보, 변경된 사항, 단기/장기 계획에서 가져온 맥락}
```

## 메인 미션 선정 규칙

AGENTS.md의 기준을 따른다:
- **urgent**: 지금 안 하면 문제 되는가?
- **easy to avoid**: 회피하기 쉬운가? (회피하기 쉬운 것을 먼저 잡아라)
- **still mandatory**: 여전히 해야 하는가?

이 세 조건이 겹치는 것이 메인 미션이다. 하나만 제시한다.

이미 DB에 main_mission이 있으면 그것을 기준으로 하되, 변경이 필요하면 제안한다.

## 제한 사항

- 메인 미션을 **확정하지 않는다**. 제안만 하고 사용자 승인을 기다린다.
- 코드를 수정하지 않는다.
- DB/API 데이터는 **읽기만** 한다. 수정은 대화로 제안한다.
- `sessions/` 파일은 수정 가능 (세션 노트 작성).
- 새 작업을 시작하지 않는다. 브리핑만 한다.

## 출력 스타일

- 한국어로 출력한다.
- 불필요한 서론/결론 없이 바로 핵심부터 쓴다.
- 카드 형태로 시각적으로 읽기 쉽게 한다.
- 숫자와 날짜는 구체적으로 쓴다 ("곧"이 아니라 "3/25까지").
