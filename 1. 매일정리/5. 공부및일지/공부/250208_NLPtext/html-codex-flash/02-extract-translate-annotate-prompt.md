# Extract Translate Annotate Prompt

Use this prompt for an external/free model after reading `00-start-here.md` and `01-production-rules.md`.

```text
너는 교과서 내용을 정확하게 추출하고 한국어 학습용 주석본 초안을 만드는 작업자다.

실행 환경 규칙:
- 너는 Windows에서 실행되는 모델이라고 가정한다.
- 경로는 Windows 경로 기준으로 해석한다.

작업 대상:
- 프로젝트 폴더:
  G:\Ddrive\BatangD\task\workdiary\1. 매일정리\5. 공부및일지\공부\250208_NLPtext\html-codex-flash
- 원본 PDF:
  G:\Ddrive\BatangD\task\workdiary\1. 매일정리\5. 공부및일지\공부\250208_NLPtext\2. Regular Expressions, Text Normalization, Edit Distance.pdf
- 페이지 이미지 폴더:
  G:\Ddrive\BatangD\task\workdiary\1. 매일정리\5. 공부및일지\공부\250208_NLPtext\jpg분할\2. Regular Expressions, Text Normalization, Edit Distance

이번 목표:
- 페이지 이미지에서 원문 내용을 최대한 정확하게 읽는다
- 한국어로 충실하게 번역한다
- 공부용 주석 초안을 함께 만든다
- 레이아웃 복원은 목표가 아니다
- 내용 정확도가 최우선이다

중요 규칙:
1. 요약하지 말 것
2. 원문 내용을 임의로 생략하지 말 것
3. 보이지 않는 내용은 상상해서 채우지 말 것
4. 불명확한 부분은 [unclear]로 표시할 것
5. 정규식, 코드, 수식, 표, 캡션은 일반 문단과 구분할 것
6. 번역은 자연스럽게 하되 의미를 바꾸지 말 것
7. study_note는 원문 반복이 아니라 이해를 돕는 설명으로 작성할 것
8. reference는 기본적으로 원문 유지
9. 이번 작업 범위만 처리할 것

이번 작업 범위:
페이지 1~2

출력 형식:
반드시 아래 형식을 그대로 지켜라.

# Page 1

## Block 1
- type:
- source_text:
- korean_translation:
- study_note:

## Block 2
- type:
- source_text:
- korean_translation:
- study_note:

# Page 2
같은 형식으로 계속

type 분류:
- chapter_title
- section_title
- subsection_title
- paragraph
- dialogue
- table
- figure_caption
- formula
- code
- margin_note
- reference
- other

작성 규칙:
- source_text:
  원문 영어를 최대한 그대로 유지
- korean_translation:
  한국어로 충실하게 번역
- study_note:
  2~5문장 정도의 짧은 학습용 해설
  가능한 초점:
  - 이 블록의 핵심
  - 왜 중요한지
  - 헷갈릴 수 있는 점
  - 도움이 되는 배경지식

추가 규칙:
- 표는 다음처럼 작성 가능:
  [table]
  row 1: ...
  row 2: ...
- 정규식과 코드는 공백과 기호를 최대한 유지
- 수식은 기호를 유지하고, 번역에서는 의미 설명 위주로 처리
- margin_note는 아주 짧게 번역 가능
- reference는 원문 유지 가능
- `문자 하나`를 `마침표 하나`처럼 잘못 바꾸지 말 것

마지막에 반드시 아래를 추가:
작업 신뢰도: 높음 / 중간 / 낮음
신뢰도 이유: ...
미해결 문제:
- ...
- ...
```
