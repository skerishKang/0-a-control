---
name: 0-a-control-ops
description: "0-a-control(http://localhost:4310) 반복 운영: 현재 상태 요약, 완료 탭 확인, quick input 제출."
---

# 0-a-control-ops

## 개요

로컬 운영 대시보드 `0-a-control` (`http://localhost:4310`)의 반복 워크플로우를 수행한다.
이 스킬은 **반복 운영 전용**이다. 첫 탐색이나 UI 구조 파악에는 사용하지 않는다.

## 트리거 조건

아래 요청이 들어오면 **자동으로 이 스킬을 사용한다**:

- `0-a-control 열어줘`
- `0-a-control 현재 상태`
- `메인 미션 알려줘` / `현재 미션 확인`
- `현재 퀘스트 확인` / `퀘스트 상태`
- `완료 탭 요약` / `오늘 뭐 완료했어`
- `quick input 넣어줘` / `퀵 인풋에 ~라고 입력`
- `0-a-control screenshot`

## 사용하지 않는 경우

| 상황 | 대응 |
|------|------|
| 서버 미기동 | 서버 기동 안내 후 중단 |
| 0-a-control이 아닌 사이트 | 이 스킬 미사용 |
| UI 구조 변경 의심 | 재탐색 안내 후 중단 |
| 첫 방문 / 셀렉터 불명 | MCP 또는 수동 탐색 안내 |

## 타겟

- **site_name**: 0-a-control
- **url**: `http://localhost:4310`
- **board**: `http://localhost:4310/board-v2.html`
- **환경**: 로컬 서버, 항상 동일 머신

## 실행 전 확인

서버가 살아있는지 먼저 확인한다:

```bash
curl -sf http://localhost:4310/api/current-state > /dev/null 2>&1
```

응답 없으면:
> 0-a-control 서버가 꺼져 있습니다.
> 실행: `python scripts/youtube_brief_server.py` 또는 `start-youtube-brief.bat`
> 그런 뒤 다시 요청해주세요.

## 워크플로우 1: 현재 상태 요약

### 트리거
`0-a-control 현재 상태`, `메인 미션 확인`, `현재 퀘스트 알려줘`

### 실행

**1단계: API로 상태 조회**

```bash
curl -s http://localhost:4310/api/current-state
```

**2단계: 핵심 필드 추출**

응답의 `current_state` 객체에서:

| 필드 | 의미 |
|------|------|
| `main_mission_title` | 메인 미션 제목 |
| `main_mission_reason` | 메인 미션 선정 이유 |
| `current_quest_title` | 현재 퀘스트 제목 |
| `current_quest_completion_criteria` | 퀘스트 완료 기준 |
| `day_phase` | 현재 단계 (morning / in-progress / end-of-day) |
| `dated_pressure_summary` | 마감 임박 항목 |
| `top_unfinished_summary` | 미완료 항목 |
| `restart_point` | 재시작 지점 |

**3단계: 시각적 검증 (선택)**

```bash
playwright screenshot --wait-for-timeout 2000 http://localhost:4310/board-v2.html temp/0-a-control-state.png
```

### 출력 형식

```
## 0-a-control 현재 상태

**메인 미션:** {main_mission_title}
**선정 이유:** {main_mission_reason}

**현재 퀘스트:** {current_quest_title 또는 "없음"}
**완료 기준:** {current_quest_completion_criteria 또는 "-"}

**단계:** {day_phase}
**마감 임박:** {dated_pressure_summary 또는 "없음"}
**미완료:** {top_unfinished_summary 또는 "없음"}
```

## 워크플로우 2: 완료 탭 요약

### 트리거
`완료 탭 확인`, `오늘 뭐 완료했어`, `최근 완료 요약`

### 실행

**1단계: API로 현재 상태 조회 (완료 데이터 포함)**

```bash
curl -s http://localhost:4310/api/current-state
```

**2단계: 완료 관련 필드 추출**

| 필드 | 의미 |
|------|------|
| `today_done_quests` | 오늘 완료된 퀘스트 목록 |
| `day_progress_summary` | 오늘 진행 요약 |
| `recent_verdict` | 최근 판정 결과 |
| `quest_status_summary` | 퀘스트 상태 요약 |

**3단계: plans API로 추가 확인 (필요 시)**

```bash
curl -s http://localhost:4310/api/plans
```

**4단계: 시각적 검증 (선택)**

```bash
playwright screenshot --wait-for-timeout 2000 http://localhost:4310/board-v2.html temp/0-a-control-completed.png
```

### 출력 형식

```
## 0-a-control 완료 현황

**오늘 완료:**
- {항목 1}
- {항목 2}
또는 "오늘 완료 항목 없음"

**최근 판정:** {recent_verdict}

**진행 요약:** {day_progress_summary}
```

## 워크플로우 3: Quick Input 제출

### 트리거
`quick input 넣어줘`, `0-a-control에 ~라고 입력`, `퀵 인풋에 ~`

### 실행

**1단계: API로 제출**

```bash
curl -s -X POST http://localhost:4310/api/bridge/quick-input \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"{입력 텍스트}\"}"
```

**2단계: 응답 확인**

- HTTP 200 = 성공
- 그 외 = 실패 (응답 본문 출력)

**3단계: 반영 확인 (선택)**

제출 후 현재 상태를 다시 조회하여 반영 여부 확인:

```bash
curl -s http://localhost:4310/api/current-state | python -c "
import sys, json
d = json.load(sys.stdin)
cs = d.get('current_state', {})
print(cs.get('top_unfinished_summary', '확인 불가'))
"
```

**4단계: 시각적 검증 (선택)**

```bash
playwright screenshot --wait-for-timeout 2000 http://localhost:4310/board-v2.html temp/0-a-control-input.png
```

### 출력 형식

```
## Quick Input 제출 결과

**입력 내용:** {텍스트}
**제출 결과:** 성공 / 실패
**서버 응답:** {요약}
```

## 출력 공통 규칙

1. **언어**: 항상 한국어
2. **스타일**: 서론/결론 없이 바로 핵심
3. **구체성**: "곧"이 아니라 "오늘 오후" / "3/27까지"
4. **길이**: 10줄 이내 (스크린샷 경로 제외)
5. **불필요한 데이터 금지**: 원본 JSON이나 API 응답을 그대로 출력하지 않는다

## 실패 규칙

| 상황 | 대응 |
|------|------|
| 서버 미기동 | "서버 꺼짐. `python scripts/youtube_brief_server.py` 실행 후 재요청" 안내 후 **즉시 중단** |
| API 응답 없음 (타임아웃) | "서버 응답 없음. 서버 상태를 확인해주세요" 출력 후 중단 |
| API 응답에 핵심 필드 없음 | 있는 필드만 요약. "구조 변경 의심" 안내 |
| quick input 제출 실패 | "제출 실패 (HTTP {status}). 서버 로그를 확인해주세요" 출력 |
| `day_phase`가 예상과 다름 | 해당 phase에 맞는 안내 (morning이면 "아직 브리핑 단계입니다") |
| 셀렉터/UI 변경 의심 | **추측하지 않는다.** "UI 구조가 예상과 다릅니다. 수동 확인이 필요합니다" 출력 후 중단 |
| Playwright 실행 불가 | API 결과만으로 진행. "시각적 검증 생략" 표시 |

## 아티팩트 정책

- **기본**: 텍스트 요약만 출력 (screenshot 없음)
- **요청 시**: screenshot 저장
- **디버깅**: video는 별도 요청 시에만
- 저장 경로: `temp/0-a-control-{workflow}-{timestamp}.png`

## 관련 리소스

- **API 엔드포인트**:
  - `GET /api/current-state` — 전체 상태 조회
  - `GET /api/plans` — 플랜 조회
  - `POST /api/bridge/quick-input` — quick input 제출
- **UI 소스**: `public/board-v2.js`, `public/board-v2-render.js`
- **DB 스크립트**: `scripts/db_state.py`
- **서버**: `scripts/youtube_brief_server.py`
- **AGENTS.md**: 프로젝트 운영 규칙 (Daily Operating Loop)

## Kilo와 Antigravity의 차이

| 구분 | Antigravity | Kilo |
|------|-------------|------|
| 기본 방식 | Playwright 브라우저 자동화 | API 호출 (curl) |
| DOM 접근 | CSS 셀렉터 직접 지정 | API JSON 응답 파싱 |
| 탭 전환 | `.v2-phase-tab` 클릭 | API 파라미터 변경 |
| Quick Input | `textarea#v2QuickInput` 입력 | `POST /api/bridge/quick-input` |
| 검증 | 브라우저 실시간 확인 | 선택적 Playwright screenshot |
| 속도 | 느림 (브라우저 렌더링 대기) | 빠름 (API 직접 호출) |

**핵심**: Kilo는 API 우선, Antigravity는 브라우저 우선.
둘 다 같은 데이터를 읽지만 접근 방식이 다르다.
