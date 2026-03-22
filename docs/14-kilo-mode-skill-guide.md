# 14. Kilo Mode-Skill 운영 가이드

## 목적

이 문서는 0-a-control에서 Kilo custom mode와 skill이 어떻게 연결되어 쓰이는지 정리한다.
사용자가 "지금 어떤 모드로 들어가고, 어떤 skill을 호출해야 하는지" 바로 알 수 있도록 한다.

## Mode ↔ Skill 매핑

| Kilo Mode | Kilo Skill | 호출 시점 | 핵심 동작 |
|-----------|-----------|----------|----------|
| `/ops-brief` | `daily-briefing` | 아침, 세션 시작 | current_state + plans + sessions → 메인 미션 1개 + 즉시 시작 액션 1개 |
| `/ops-quest` | `quest-review` | 퀘스트 완료/중간 점검 | 현재 퀘스트 → done/partial/hold 판정 + 다음 퀘스트 제안 |
| `/ops-triage` | `telegram-email-triage` | 새 정보 도착 | external_inbox → today/dated/short_term/hold 분류 |
| `/ops-close` | `session-refresh` | 하루/세션 마감 | 완료 정리 + 미완료→재시작 전략 + 세션 export |

**규칙**: 모드는 "어떤 역할로 대화할지"를 정하고, skill은 "구체적으로 무엇을 실행할지"를 정한다.
각 모드에는 권장 skill이 하나씩 있으나, 실행 여부는 사용자가 결정한다.

## 일일 운영 루프와 Mode/Skill 사용

### 🌅 아침 (Day Start)

```
사용자: /ops-brief
       ↓
[Kilo가 ops-brief 모드로 전환]
       ↓
기본 동작: skill "daily-briefing" 사용
       ↓
출력: 아침 브리핑 (메인 미션 1개 + 즉시 시작 액션 1개)
       ↓
사용자: "좋아, 이걸로 가자" (승인)
       또는: "아니, 오늘은 이거 먼저" (오버라이드)
```

**읽는 데이터**:
- `GET /api/current-state` — main_mission, current_quest, day_phase, unfinished, due_items
- `GET /api/plans` — today/dated/short_term 버킷
- `sessions/` — 최근 3일 세션 노트

**기대 출력**:
```
## 아침 브리핑 — 3/23 (일)

### 메인 미션
> **프로젝트 X 배포 준비**
> 이유: 마감이 3/25이고, 회피하기 쉬우며, 아직 완료되지 않음

### 즉시 시작 액션
- 배포 체크리스트 최종 확인
```

### ⚔️ 진행 중 (Mid-Session)

```
사용자: 작업 수행 중...
       ↓
사용자: /ops-quest
       ↓
[Kilo가 ops-quest 모드로 전환]
       ↓
기본 동작: skill "quest-review" 사용
       ↓
사용자: "이 부분은 done, 나머지는 partial"
       ↓
출력: Verdict (done/partial/hold) + 다음 퀘스트 제안
```

**읽는 데이터**:
- `GET /api/current-state` — current_quest, completion_criteria, quest_status_summary
- `GET /api/quests` — 퀘스트 이력
- `data/queue/*.report.json` — 판정 대기 중인 보고서

**기대 출력**:
```
퀘스트 평가 — 프로젝트 X 배포 준비

판정: partial

왜 이 판정인가
- 배포 체크리스트는 완료했으나, 테스트 환경 미설정

남은 것
- staging 서버 배포 테스트

재시작 지점
- staging 환경 설정부터

다음 퀘스트 제안
> staging 서버 배포 테스트
> 이유: 체크리스트 완료 후 자연스러운 다음 단계
```

### 📬 분류 (Inbound Triage)

```
텔레그램 동기화 완료 후...
       ↓
사용자: /ops-triage
       ↓
[Kilo가 ops-triage 모드로 전환]
       ↓
기본 동작: skill "telegram-email-triage" 사용
       ↓
출력: 새 항목 N건 분류 결과
       ↓
사용자: "1번은 today, 2번은 short_term, 3번은 보류"
       ↓
plan_items에 반영 (API /api/plans/approve)
```

**읽는 데이터**:
- `GET /api/external-inbox?status=new` — 새 외부 입력
- `GET /api/plans` — 기존 계획 (중복 확인)
- `GET /api/current-state` — 메인 미션 맥락

**기대 출력**:
```
인바운드 분류 — 3/23

분류 결과 (총 5건)

today (2건)
1. 강혜림: 내일 회의 자료 요청
   - 출처: 강혜림 / 강혜림
   - 제안: plan_item (today) 생성

2. 김주석: 배포 일정 확인 요청
   - 출처: 김주석 / 김주석
   - 제안: plan_item (today) 생성

short_term (2건)
...

보류 (1건)
...
```

### 🌙 마감 (End of Day)

```
사용자: /ops-close
       ↓
[Kilo가 ops-close 모드로 전환]
       ↓
기본 동작: skill "session-refresh" 사용
       ↓
출력: 종료 보고 + 세션 갱신 결과
       ↓
출력: 내일 첫 퀘스트 제안
```

**읽는 데이터**:
- `GET /api/current-state` — main_mission, recent_verdict, unfinished, day_progress_summary
- `GET /api/quests` — 오늘 수행한 퀘스트 전체
- `GET /api/plans` — 내일/이번 주 맥락
- `sessions/` — 오늘 세션 노트

**기대 출력**:
```
## 종료 보고 — 3/23

### 오늘 한 것
- 프로젝트 X 배포 체크리스트 완료 (done)
- staging 환경 절반 설정 (partial)

### 미완료
- staging 서버 배포 테스트
  - 재시작 지점: docker-compose 설정 수정부터
  - 막힌 이유: 서버 접근 권한 대기

### 내일 첫 퀘스트 제안
> staging 서버 배포 테스트
> 이유: 오늘 partial로 남긴 것 중 가장 즉시 재개 가능한 항목

### 세션 갱신
Export된 세션: 3개
INDEX.md 갱신: 완료
```

## 빠른 참조 카드

```
┌─────────────────────────────────────────────────────┐
│  0-a-control Kilo 운영 빠른 참조                     │
├──────────┬──────────────┬───────────────────────────┤
│ 시점     │ 명령어       │ 동작                      │
├──────────┼──────────────┼───────────────────────────┤
│ 아침     │ /ops-brief   │ → daily-briefing          │
│          │              │ 메인 미션 1개 + 시작 액션   │
├──────────┼──────────────┼───────────────────────────┤
│ 작업 중  │ /ops-quest   │ → quest-review            │
│          │              │ verdict + 다음 퀘스트       │
├──────────┼──────────────┼───────────────────────────┤
│ 정보 도착 │ /ops-triage  │ → telegram-email-triage   │
│          │              │ 분류 + 배치 제안            │
├──────────┼──────────────┼───────────────────────────┤
│ 마감     │ /ops-close   │ → session-refresh         │
│          │              │ 종료 보고 + 세션 export     │
└──────────┴──────────────┴───────────────────────────┘
```

## Mode와 Skill의 관계 설명

### Mode (역할 정의)

Mode는 Kilo의 "페르소나"를 바꾼다:
- **ops-brief**: 전략 보좌관 (읽기 중심, 제안만)
- **ops-quest**: 실행 추적자 (진행 추적, 판정 제안)
- **ops-triage**: 분류 담당자 (새 정보 분류, 배치 제안)
- **ops-close**: 마감 담당자 (정리, 재시작 전략)

Mode가 결정하는 것:
- 어떤 파일을 읽고 쓸 수 있는지 (fileRegex)
- 어떤 도구를 사용할 수 있는지 (read, edit, command, browser, mcp)
- 대화의 기본 톤과 제한 사항

### Skill (실행 정의)

Skill은 구체적인 "작업 절차"를 정의한다:
- **daily-briefing**: 아침 브리핑 생성 절차
- **quest-review**: 퀘스트 평가 절차
- **telegram-email-triage**: 인바운드 분류 절차
- **session-refresh**: 세션 export 절차

Skill이 결정하는 것:
- 어떤 API를 어떤 순서로 호출하는지
- 어떤 스크립트를 실행하는지
- 출력 형식과 fallback 전략

### 연결 규칙

1. **각 모드에는 권장 skill이 있다.**
   - `/ops-brief` → 권장 skill: `daily-briefing`
   - `/ops-quest` → 권장 skill: `quest-review`

2. **skill은 모드 없이도 호출 가능하다.**
   - 다른 모드에서 "daily-briefing 실행해줘" 가능
   - 단, 해당 모드의 fileRegex 제한은 유지됨

3. **하나의 모드에서 여러 skill을 쓸 수 있다.**
   - `/ops-triage`에서 telegram-email-triage 후 바로 daily-briefing 호출 가능
   - 모드의 역할 범위 안에서 자유롭게 조합

## 데이터 흐름 요약

```
                     ┌──────────────┐
                     │ external_inbox│ (Telegram, Email)
                     └──────┬───────┘
                            │ /ops-triage
                            ▼
┌──────────┐    ┌────────────────────┐    ┌──────────────┐
│ current  │◄───│    plan_items      │───▶│    quests    │
│ _state   │    │ (today/short_term/ │    │ (active/done/│
│ (DB)     │    │  dated/long_term/  │    │  partial/hold│
└────┬─────┘    │  recurring/hold)   │    │  /pending)   │
     │          └────────────────────┘    └──────┬───────┘
     │                                          │
     │    /ops-brief ◄── daily-briefing         │ /ops-quest
     │         │                                │     │
     │    메인 미션 1개                  quest-review
     │    즉시 시작 액션 1개                  │
     │                                verdict (done/partial/hold)
     │                                        │
     │    /ops-close ◄── session-refresh       │
     │         │                                │
     │    종료 보고                    data/queue/
     │    재시작 전략                  (report.json)
     │    세션 export
     ▼
┌──────────────┐
│  sessions/   │ (운영 메모리)
│ YYYY-MM-DD/  │
│ *.md         │
└──────────────┘
```

## 파일 위치 참조

| 파일 | 위치 |
|------|------|
| Mode 정의 | `.kilocodemodes` |
| Mode 규칙 (ops-brief) | `.kilo/rules-ops-brief/01-briefing-rules.md` |
| Mode 규칙 (ops-quest) | `.kilo/rules-ops-quest/01-quest-rules.md` |
| Mode 규칙 (ops-triage) | `.kilo/rules-ops-triage/01-triage-rules.md` |
| Mode 규칙 (ops-close) | `.kilo/rules-ops-close/01-closing-rules.md` |
| Skill (daily-briefing) | `.kilocode/skills/daily-briefing/SKILL.md` |
| Skill (quest-review) | `.kilocode/skills/quest-review/SKILL.md` |
| Skill (telegram-email-triage) | `.kilocode/skills/telegram-email-triage/SKILL.md` |
| Skill (session-refresh) | `.kilocode/skills/session-refresh/SKILL.md` |
| 운영 원칙 | `AGENTS.md` |
| 텔레그램 규칙 | `docs/13-telegram-storage-rules.md` |
