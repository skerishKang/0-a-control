# SKILL: conversation-to-control-tower

## skill name
`conversation-to-control-tower`

## description
사용자의 긴 대화를 0-a-control 운영 체계(control tower)용 구조로 변환한다.

## trigger 조건
다음 상황에서 이 skill을 사용:
- 사용자 입력 길이가 200자 이상
- 아이디어, 철학, 프로젝트, 오늘 할 일이 섞인 입력
- "책 읽고 싶다", "철학 정리해줘" 같은 요청
- 기존 세션과 다른 해석을 하고 싶을 때

## 변환 규칙

### 1. 입력 분류 (6개 계층)

| 계층 | 의미 | 변환 방향 |
|------|------|----------|
| **today** | 오늘 당장 | current quest 바로 생성 |
| **short_term** |이번 주中 | plan-item (short_term) |
| **long_term** | 장기 | plan-item (long_term) |
| **recurring** | 정기 반복 | plan-item (recurring) |
| **project** | 특정 프로젝트 | plan-item (project bucket) |
| **philosophy** | 장기 사고/철학 | 운영 원칙으로 변환 |

**분류 우선순위**: today → short_term → long_term → recurring → project → philosophy

### 2. 출력 생성

분류 후 반드시 아래 출력 중 하나 이상 생성:

| 출력 | 설명 |
|------|------|
| **main mission** | 오늘의 대표 임무 |
| **current quest** | 지금 바로 할 행동 |
| **plan item** | plans 테이블 저장 |
| **model prompt** | 다음 세션 지시 |

### 3. 4축 연결 (philosophy 분류 시 필수)

philosophy는 반드시 4축 중 하나 이상에 연결:
- **통제**: AI 평가와 통제
- **위임**: AI에게 위임
- **판단**: AI와 인간 판단 분담
- **협업**: AI와 협력

## 실패 기준

다음 중 하나라도 해당하면 **실패**:

1. **입력 분류 없이 바로 TODO 생성**
   - 6개 계층 분류 없이 action list 만드는 것 금지

2. **philosophy → today 직접 변환**
   - 장기 사고를 무조건 오늘 할 일로 만드는 것 금지

3. **긴 대화를 단순 checklist로 압축**
   - "책 4권 읽기" 같은 목록 금지

4. **main mission / current quest 없이 종료**
   - 최소 1개 quest 제안 필수

## 예시

### 입력
```
한비자, 드러커, 폴라니, 부버 읽고 싶어.
이제AI하고 일하는 방식도 잘 정리해야 할 것 같아.
특히 AI한테 뭐 위임하고 뭐 직접 해야 하는지 판단基准이 필요해.
```

### 분석 및 변환

1. **분류**: philosophy (장기 사고/철학)
2. **4축 연결**: 위임 + 판단

### 출력

```
## main mission
**AI와 함께하는 운영 원칙 10조 구축**

## current quest (today)
**4本书 핵심 키워드 추출** (각 1개씩)

## plan item
- long_term: "AI 위임 원칙 정리"
- short_term: "한비자 통제 핵심 추출"
- recurring: "주 1회 독서 노트 통합"
```

## 주의

- 이 skill은 "대화 → 구조" 변환기
- 입력 길이에 관계없이 반드시 분류 먼저
- philosophy는 반드시 4축 연결
- 출력은 항상 main mission + current quest 중심으로
