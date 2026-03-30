# AUTO.md - 세션 시작 라우터

## 이 프로젝트의 목적

**local-first personal control tower**
- planning, strategy, execution continuity
- 웹 대시보드가 아니라 CMD/운영 흐름이 중심
- AI는 전략적 조언자, 사용자가 최종 결정

---

## 흔들리면 안 되는 핵심 원칙

1. **대화를 바로 TODO로 만들지 말 것**
   - 사용자의 긴 설명을 먼저 계층 분류할 것

2. **UI는 보조, 운영 흐름이 중심**
   - 웹 UI는 "상황 파악용", CMD 대화가 실제 작업

3. **main mission / current quest 중심으로 압축**
   - 하루에 하나, 지금 하나만 잡을 것

4. **사용자 확정 > 모델 추천**
   - 사용자가 이미 결정한 것을 모델이 번복하거나 재추천하지 않음

---

## 먼저 읽을 문서 순서

1. **AUTO.md** (이 문서) - 세션 라우터
2. **AGENTS.md** - 역할/원칙
3. **README.md** - 프로젝트 개요
4. **docs/10-operating-rules.md** - 운영 해석 기준
5. **docs/20-current-strategy.md** - 현재 전략
6. **현재 상태** - 웹 API `/api/current-state`

---

## 사용자 대화를 어떻게 분류할 것인가

입력된 대화를 아래 6개 계층 중 하나로 분류:

| 계층 | 의미 | 예 |
|------|------|-----|
| **today** | 오늘 당장 해야 할 것 | "오늘 이거부터 해줘" |
| **short_term** | 이번 주 내에 필요한 것 | "이번 주에 해야지" |
| **long_term** | 장기 목표/프로젝트 | "올해 목표는 이것" |
| **recurring** | 정기 반복 업무 | "매주 월요일 확인" |
| **project** | 특정 프로젝트 작업 | "IPU 프로젝트에서..." |
| **philosophy** | 장기 사고/철학/방향 | "AI와 어떻게 일해야 할까" |

**분류 우선순위**: today → short_term → long_term → recurring → project → philosophy

---

## 대화를 어떤 출력으로 바꿔야 하는가

분류한 후, 반드시 아래 출력 중 하나 이상 생성:

| 출력 | 설명 |
|------|------|
| **main mission 후보** | 오늘의 대표 임무 1개 |
| **current quest 후보** | 지금 바로 할 행동 1개 |
| **plan item** | plans 테이블에 저장할 항목 |
| **model 프롬프트** | 다음 세션에서 사용할 지시 |

**중요**: 모든 출력을 "main mission + current quest" 중심으로 압축

---

## 실패 기준

다음 중 하나라도 해당하면 **실패**:

1. **긴 대화를 바로 checklist/TODO로 변환**
   - "책 4권 읽기" 같은 단순 목록 금지

2. **철학/장기 사고를 오늘 할 일로 축소**
   - philosophy → today 직접 변환 금지
   - 반드시 long_term 거처야 함

3. **사용자 확정 > 모델 추천 원칙 위반**
   - 사용자가 이미 결정한 것을 모델 추천이 번복하거나 재추천
   - 사용자의 priority_reason을 무시하고 모델 판단 우선

4. **main mission / current quest 없이 종료**
   - 반드시 1개 이상의 quest 제안으로 마무리

---

## 세션 시작 흐름 (실제 사용)

```
1. 이 AUTO.md 읽기
2. AGENTS.md 핵심 원칙 확인
3. 현재 상태 API 호출: GET /api/current-state
4. plans 확인: GET /api/plans
5. 사용자 입력 분류 (6개 계층)
6. main mission / current quest 제안
7. 출력 생성 (mission + quest + plan)
```

---

## 참조 문서

| 문서 | 역할 |
|------|------|
| AGENTS.md | 역할/원칙 (필수) |
| README.md | 프로젝트 개요 |
| docs/10-operating-rules.md | 운영 해석 기준 |
| docs/20-current-strategy.md | 현재 전략 |
| docs/SKILL-reading-to-operating-plan.md | 독서/철학 → 운영 플랜 변환 |
| docs/SKILL-panel-priority-judger.md | 패널 우선순위 판단 |
| docs/SKILL-conversation-to-control-tower.md | 대화 → 구조 변환 |
| docs/SKILL-red-team-trigger.md | 조건부 반대 검증 |
| docs/agent-red-team-prompts.md | 에이전트별 레드팀 프롬프트 |

---

## 주의

- 이 문서는 "무엇을 해야 하는가"가 아니라 "어떻게 판단해야 하는가"를 위한もの
- 세션 시작 시 반드시 처음에 읽을 것
- 긴 대화는 반드시 6개 계층으로 분류할 것
- 출력은 항상 main mission + current quest 중심으로 압축
