# Extraction Task Prompt

Use this prompt for an external/free model after confirming the visual baseline and production rules.

```text
너는 교재 번역 재제작을 위한 원문 텍스트 추출 정리 담당자다.

중요:
- 지금 단계에서는 번역하지 않는다.
- 요약하지 않는다.
- 내용을 임의로 생략하지 않는다.
- 원문 영어를 최대한 그대로 보존한다.
- 구조화된 원고를 만드는 것이 목적이다.
- 시각 레이아웃 복원은 하지 말고, 논리 구조와 블록 단위 정리에 집중한다.

실행 환경 규칙:
- 너는 Windows에서 실행되는 모델이라고 가정하고 작업하라.
- 경로는 Windows 경로 기준으로 해석하라.

대상:
- 원본 PDF:
  G:\Ddrive\BatangD\task\workdiary\1. 매일정리\5. 공부및일지\공부\250208_NLPtext\2. Regular Expressions, Text Normalization, Edit Distance.pdf
- 페이지 이미지 폴더:
  G:\Ddrive\BatangD\task\workdiary\1. 매일정리\5. 공부및일지\공부\250208_NLPtext\jpg분할\2. Regular Expressions, Text Normalization, Edit Distance

이미 확보된 작업 기준:
- 기준 문서 1: 01-visual-structure-report.md
- 기준 문서 2: 02-production-rules.md
- 이 문서는 총 29페이지다.
- 주요 흐름은 대략 다음과 같다:
  2.1 Regular Expressions
  2.2 Words
  2.3 Corpora
  2.4 Text Normalization
  2.5 Minimum Edit Distance
  2.6 Summary
  Bibliographical and Historical Notes
  Exercises
- 이 단계에서는 원문 텍스트를 블록 단위로 정리하는 것이 목표다.

너의 작업 목표:
PDF 또는 페이지 이미지를 바탕으로, 원문 영어 텍스트를 “번역 가능한 구조화 원고” 형태로 정리하라.

반드시 지킬 규칙:
1. 번역하지 말 것
2. 요약하지 말 것
3. 보이는 영어 원문을 최대한 유지할 것
4. 정규식, 코드, 수식, 표, 그림 캡션은 일반 문단과 구분할 것
5. 읽기 불명확한 부분은 [unclear]로 표시할 것
6. 추정 복원은 최소화할 것
7. 페이지 번호와 블록 번호를 반드시 붙일 것
8. 한 번에 전체를 다 하려고 하지 말고, 지정된 페이지 범위만 처리할 것

이번 작업 범위:
페이지 1부터 페이지 8까지

출력 형식:
반드시 아래 형식을 그대로 지켜라.

# Page 1
## Block 1
- type:
- role:
- source text:

## Block 2
- type:
- role:
- source text:

# Page 2
## Block 1
- type:
- role:
- source text:

이 형식으로 페이지 8까지 계속 작성.

블록 type 분류 규칙:
- chapter_title
- section_title
- subsection_title
- paragraph
- bullet_list
- table
- figure_caption
- figure_text
- formula
- code
- dialogue
- margin_note
- exercise
- reference
- unclear

role 작성 규칙:
- main title
- section heading
- explanatory paragraph
- example
- caption
- algorithm
- glossary-like note
- margin keyword
- summary point
- bibliography
- exercise prompt
- other

source text 작성 규칙:
- 원문 영어를 최대한 보존
- 줄바꿈이 의미 있으면 유지
- 코드/정규식은 공백 포함 최대한 그대로 유지
- 표는 가능하면 셀 구조를 무너뜨리지 말고 plain text로 정리
- 표 구조가 어렵다면 다음처럼 작성:
  [table]
  row 1: ...
  row 2: ...
- 그림 안 텍스트가 읽히면 figure_text로 분리
- 그림 캡션은 figure_caption으로 분리

중요:
- 이번 응답은 페이지 1~8만 처리
- 페이지 9 이후는 절대 작성하지 말 것
- 불확실한 글자는 [unclear]로 남길 것
- 보이지 않는 내용을 상상해서 채우지 말 것

마지막에 반드시 아래를 추가:
추출 신뢰도: 높음 / 중간 / 낮음
신뢰도 이유: ...
미해결 문제:
- ...
- ...
```
