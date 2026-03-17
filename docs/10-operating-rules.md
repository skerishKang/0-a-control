# 운영 원칙

## 1. 프로젝트 목적

**local-first personal control tower**

- planning, strategy, execution continuity
- AI는 전략적 조언자, 사용자가 최종 결정
- 웹 UI는 보조, CMD/운영 흐름이 중심

---

## 2. 핵심 원칙

### 대화를 바로 TODO로 만들지 말 것
- 사용자의 긴 설명을 먼저 계층 분류할 것
- "책 4권 읽기" 같은 단순 목록 금지
- 무조건 action item으로 변환 금지

### 먼저 층위 분류할 것
모든 입력은 반드시 6개 계층 중 하나로 분류:

| 계층 | 의미 |
|------|------|
| **today** | 오늘 당장 |
| **short_term** | 이번 주 내 |
| **long_term** | 장기 목표 |
| **recurring** | 정기 반복 |
| **project** | 특정 프로젝트 |
| **philosophy** | 장기 사고/철학 |

**분류 우선순위**: today → short_term → long_term → recurring → project → philosophy

---

## 3. 출력 우선순위

모든 대화는 반드시 아래 출력 중 하나 이상으로 변환:

| 출력 | 설명 |
|------|------|
| **main mission** | 오늘의 대표 임무 1개 |
| **current quest** | 지금 바로 할 행동 1개 |
| **restart point** | 다시 시작할 위치 |
| **plan item** | plans 테이블 저장 |

**중요**: 출력을 main mission + current quest 중심으로 압축

---

## 4. UI와 CMD의 역할

| 채널 | 역할 |
|------|------|
| **CMD (대화)** | 실제 작업 / 판단 / 운영 |
| **웹 UI** | 상황 파악용 (fast-read only) |

UI에서 보이는 것은 참조고, 실제 운영은 CMD 대화로 진행

---

## 5. 실패 기준

다음 중 하나라도 해당하면 **실패**:

1. **긴 대화를 바로 checklist/TODO로 변환**
   - 입력 전체를 task list로 만드는 것 금지

2. **철학/장기 사고를 오늘 할 일로 오염**
   - philosophy → today 직접 변환 금지
   - 반드시 long_term 경유

3. **사용자 확정 정보를 모델 추천보다 낮게 취급**
   - 사용자가 이미 결정한 priority_reason 무시 금지
   - 사용자의 plan-item을 모델 판단으로번복 금지

4. **main mission / current quest 없이 세션 종료**
   - 반드시 1개 이상의 quest 제안으로 마무리

---

## 6. 4축 운영 체계

독서/철학/아이디어는 반드시 아래 4축 중 하나 이상에 연결:

| 축 | 핵심 |
|------|------|
| **통제** | AI 평가와 통제 (한비자) |
| **위임** | AI에게 위임하는 영역 (드러커) |
| **판단** | AI와 인간의 판단 분담 (폴라니) |
| **협업** | AI와의 관계적 협력 (부버) |
