# 0-a-control: Daily Operating Loop

## 1. Daily Operating Loop 개요
0-a-control은 단순한 대시보드가 아닌 **CMD 중심의 대화형 통제탑**입니다.
하루의 운영은 철저히 **"One Main Mission, One Current Quest"** 원칙 아래, Codex와의 대화(세션)를 통해 이루어집니다.
웹 UI는 이 대화의 결과를 반영하는 읽기 전용 '상황판'일 뿐입니다.

## 2. Recovery 읽기 순서 (모든 단계의 전제)

모든 단계에서 다음 순서를 따릅니다:

1. **current urgent state** 확인
2. **관련 sessions archive** 선택적 읽기 (전체가 아님)
3. **sessions_html/** 빠른 탐색 (필요 시)
4. **raw transcript / DB** 추가 확인 (부족할 때)
5. **summary/current quest** 압축 (마지막 정리)

**핵심**: 전체를 읽을 필요 없음. 오늘 주제와 관련된 세션만 선택적으로.

## 3. Morning Loop (아침 시작 — 1분)
하루의 방향을 잡고 유일한 '주 임무(Main Mission)'를 설정하는 단계입니다.

### 읽기 순서 (1분)
1. **current state** (10초) — 오늘 주 임무와 현재 퀘스트 확인
2. **관련 archive** (30초) — 오늘 주제와 관련된 어제 세션이 있으면 Dialogue 일부 읽기
3. **mission decision** (20초) — main mission 확정

### 사용자 발화 예시
```
"어제 archive 확인하고 오늘 주 임무 정하자."
```

### Codex가 읽는 정보
- `current_state`의 `day_progress_summary`, `top_unfinished_summary`, `dated_pressure_summary`
- 관련된 어제 세션 archive (있으면)
- 전날 밤 생성된 `daily_digest_YYYYMMDD.json`

### 산출물
1. **Main Mission 확정**: 오늘 반드시 끝내야 할 하나의 목표.
2. **First Quest 할당**: 주 임무를 시작하기 위한 첫 번째 구체적 행동.

## 4. Midday / Re-entry Loop (중간 재정렬 — 30초)
작업이 끊겼거나 흐름을 다시 잡아야 할 때 실행하는 루프입니다.

### 읽기 순서 (30초)
1. **current state** (10초) — restart_point, recommended_next_quest 확인
2. **관련 archive** (20초) — 맥락이 기억 안 나면 관련 세션 일부 재확인

### 사용자 발화 예시
```
"흐름이 좀 끊겼네. 지금 어디까지 했고, 다음 퀘스트로 뭘 하면 좋을까?"
```

### 언제 archive를 읽는가
| 상황 | 행동 |
|------|------|
| 맥락이 기억 안 남 | 관련 세션 Dialogue 일부 재확인 |
| 주제가 명확하면 | archive 건너뜀 |

## 5. In-Progress Quest Loop (작업 중 — 30초)
하나의 퀘스트를 수행하고 보고하며, AI의 판정(Verdict)을 받는 가장 빈번한 루프입니다.

### 읽기 순서 (30초, 필요할 때만)
1. **current quest** — 항상 중심
2. **관련 archive** — 맥락 분실 시에만

### 사용자 발화 예시
```
"퀘스트 보고: A 모듈 API 연동 끝남. 남은 건 예외 처리. 완료(done)로 판단해줘."
```

### 산출물
1. **상태 전이**: `report_quest_progress` → `pending`
2. **AI 판정**: `done`, `partial`, `hold`
3. **다음 퀘스트**: 판정 결과에 따라 다음 quest 제안

## 6. End-of-Day Loop (마감 — 2분)
하루를 닫고, 미완료 항목을 내일로 이월하며, 전략을 정리하는 루프입니다.

### 읽기 순서 (2분)
1. **오늘 세션 archive 확인** (30초) — 세션이 잘 남았는지
2. **unfinished items** (1분) — 남은 일 정리
3. **restart strategy** (30초) — 내일 첫 시작점

### 사용자 발화 예시
```
"오늘 마감하자. 한 일, 남은 일, 내일 첫 퀘스트 정리해줘."
```

### archive 확인
```bash
ls sessions/$(date +%Y-%m-%d)/
```
오늘 작업한 세션이 archive에 잘 남았는지 확인합니다.

### 산출물
1. **Session Summary**: 오늘의 총평
2. **Plan Revision**: 미완료 항목 재배치
3. **Restart Strategy**: 내일 아침 시작점

### 내일을 위한 압축 문장
```
내일 아침 시작점: [주제]의 [구체적 상태]
```

## 7. 언제 archive를 읽고 언제 안 읽는지

| 상황 | 행동 |
|------|------|
| 오늘 주제와 관련된 어제 세션 | 해당 세션 Dialogue 읽기 |
| 관련 세션이 없으면 | 건너뜀 |
| 작업 중 맥락이 기억 안 나면 | 관련 세션 일부 재확인 |
| 새 세션 시작 | `codex 세션 복원해줘` |
| 주제가 명확하면 | archive 건너뜀 |

## 8. CLI Entry Point
```bash
python scripts/operating_loop_cli.py status
python scripts/operating_loop_cli.py prompt
python scripts/operating_loop_cli.py checklist
```

- `status`: 현재 `day_phase`와 주 임무/현재 퀘스트 상태
- `prompt`: 지금 Codex에게 어떤 문장으로 말하면 좋은지
- `checklist`: 현재 phase에서 놓치지 말아야 할 확인 항목
