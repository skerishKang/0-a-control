# 0-a-control: Daily Operating Loop

## 1. Daily Operating Loop 개요
0-a-control은 단순한 대시보드가 아닌 **CMD 중심의 대화형 통제탑**입니다.
하루의 운영은 철저히 **"One Main Mission, One Current Quest"** 원칙 아래, Codex와의 대화(세션)를 통해 이루어집니다.
웹 UI는 이 대화의 결과를 반영하는 읽기 전용 '상황판'일 뿐입니다.

## 2. Morning Loop (아침 시작)
하루의 방향을 잡고 유일한 '주 임무(Main Mission)'를 설정하는 단계입니다.

*   **사용자 발화 예시**: `"Codex, 좋은 아침. 오늘 상황 브리핑해 주고, 어제 남은 일 기반으로 오늘 주 임무 제안해 줘."`
*   **Codex가 읽는 정보**:
    *   `current_state`의 `day_progress_summary`, `top_unfinished_summary`, `dated_pressure_summary` (기한 임박)
    *   전날 밤 생성된 `daily_digest_YYYYMMDD.json` (밤사이 들어온 텔레그램/이메일 핵심 요약)
*   **산출물 (대화 결과)**:
 1. **Main Mission 확정**: 오늘 반드시 끝내야 할 하나의 목표.
 2. **First Quest 할당**: 주 임무를 시작하기 위한 첫 번째 구체적 행동.
*   **상태 갱신**: `current_state`의 `main_mission_*` 및 `current_quest_*` 키가 갱신됩니다.
*   **UI 변경**: 대시보드 중앙의 Hero 카드가 오늘의 주 임무와 첫 퀘스트로 교체됩니다.

## 3. Midday / Re-entry Loop (중간 재정렬)
작업이 끊겼거나 흐름을 다시 잡아야 할 때 (예: 점심 식사 후, 긴급 회의 직후) 실행하는 루프입니다.

*   **사용자 발화 예시**: `"Codex, 흐름이 좀 끊겼네. 지금 내가 어디까지 했고, 다음 퀘스트로 뭘 하면 좋을까?"` 또는 `"방금 강혜림님이랑 회의했는데, 우선순위 좀 다시 잡자."`
*   **Codex가 읽는 정보**:
    *   `current_state`의 `restart_point`, `recommended_next_quest`
    *   `external_inbox` (최근 2~3시간 내 `new` 상태의 메시지가 있는지 `fetch`로 확인)
*   **산출물 (대화 결과)**:
 1. **Main Mission 유지/변경 결단**: 웬만하면 유지하되, 치명적 외부 입력(긴급 버그 등)이 있다면 합의하에 변경.
 2. **Next Quest 재할당**: `restart_point`를 기반으로 즉시 실행 가능한 다음 퀘스트를 뽑아냅니다.
*   **UI 변경**: 퀘스트가 변경되면 Hero 카드가 갱신되고, Midday 패널(재시작 포인트 등)이 초기화됩니다.

## 4. In-Progress Quest Loop (작업 중)
하나의 퀘스트를 수행하고 보고하며, AI의 판정(Verdict)을 받는 가장 빈번한 루프입니다.

*   **사용자 발화 예시**: `"퀘스트 보고: A 모듈 API 연동 끝냄. 남은 일은 예외 처리. 블로커는 없음. 완료(done)로 판단함."`
*   **Codex가 읽는 정보**: 현재 진행 중인 퀘스트의 메타데이터 (`completion_criteria` 등).
*   **산출물 (대화/시스템 결과)**:
 1. **상태 전이**: `report_quest_progress` 호출 -> 상태가 `pending`으로 변경.
 2. **AI 판정**: 시스템(또는 Codex)이 `done`, `partial`, `hold` 중 하나로 판정(`apply_verdict`).
 3. **후속 조치 추출**: 판정 결과에 따라 `restart_point`, `next_hint`, `plan_impact`를 도출.
*   **UI 변경**: 대시보드의 '최근 판정(Recent Verdict)' 카드가 즉시 업데이트되어 AI의 평가를 보여줍니다.

## 5. End-of-Day Loop (마감)
하루를 닫고, 미완료 항목을 내일로 이월하며, 전략을 정리하는 루프입니다.

*   **사용자 발화 예시**: `"Codex, 오늘 마감하자. 오늘 한 일 요약하고, 남은 건 내일 단기 플랜으로 돌려줘."`
*   **Codex가 읽는 정보**:
    *   오늘 완료된 `quests` 목록 및 `decision_records`.
    *   `external_inbox`의 남은 `new` 또는 `reviewing` 항목 (이때 `digest` 생성을 지시할 수 있음).
*   **산출물 (대화 결과)**:
 1. **Session Summary**: 오늘의 총평 (잘한 점, 막힌 점).
 2. **Plan Revision**: 미완료된 주 임무나 퀘스트를 `short_term` 등의 계획으로 강등/재배치.
 3. **Restart Strategy**: 내일 아침 가장 먼저 봐야 할 `restart_point` 지정.
*   **상태 갱신**: `current_state`의 데일리 서머리 키들이 갱신되고, 불필요한 퀘스트/미션은 클리어됩니다.
*   **UI 변경**: 대시보드가 마감 모드로 전환되며, '오늘 판단 / 남은 핵심' 패널이 채워집니다.

## 6. External Inbox의 운영 루프 내 위치
`external_inbox`는 사용자를 방해하는 알림(Push)이 아니라, 사용자가 필요할 때 당겨보는(Pull) 큐입니다.

*   **아침 시작 전 (Pre-Morning)**: 백그라운드 스크립트가 밤사이 데이터를 모아 `digest`를 생성합니다. 아침 루프 때 Codex가 이를 읽고 브리핑에 참고합니다.
*   **중간 재정렬 시 (Midday)**: 사용자가 "혹시 놓친 긴급한 거 있어?"라고 물을 때만 Codex가 `fetch --status new --time-range 3h` 등으로 확인합니다.
*   **마감 시 (End-of-Day)**: 오늘 처리하지 않고 남겨둔 `new` 항목들에 대해 일괄적으로 `mark-reviewing` 하거나 `digest`를 생성하여 내일 아침으로 넘깁니다.
*   **매번 보지 않습니다**: 퀘스트 집중 루프(In-Progress) 중에는 절대 Inbox를 열어보지 않는 것이 원칙입니다.

## 7. CLI Entry Point
운영 루프는 문서만 읽고 끝내지 않고, 아래 CLI로 현재 상태를 바로 확인할 수 있습니다.

```bash
python scripts/operating_loop_cli.py status
python scripts/operating_loop_cli.py prompt
python scripts/operating_loop_cli.py checklist
```

- `status`: 현재 `day_phase`와 주 임무/현재 퀘스트/외부 입력 상태를 함께 보여줍니다.
- `prompt`: 지금 Codex에게 어떤 문장으로 말하면 좋은지 한 줄로 보여줍니다.
- `checklist`: 현재 phase에서 놓치지 말아야 할 확인 항목만 보여줍니다.
