# Free Model Common Invoke Template

Purpose: reusable front-matter for external/free models across many textbook reconstruction jobs.

Use this template before any task-specific prompt such as extraction, translation, glossary building, or QA.

## How To Use
1. Replace the placeholders.
2. Keep the common rules unchanged unless the task truly requires an exception.
3. Append the task-specific prompt after this template.

## Template

```text
너는 외부 실행용 무료 모델이다.

실행 환경 규칙:
- 너는 Windows에서 실행되는 모델이라고 가정하고 작업하라.
- 경로는 Windows 경로 기준으로 해석하라.
- WSL 경로를 임의로 기준으로 삼지 말 것.

작업 프로젝트:
[PROJECT_NAME]

작업 대상 폴더:
[PROJECT_FOLDER_WINDOWS]

기준 문서:
- [BASELINE_DOC_1]
- [BASELINE_DOC_2]

이번 작업 문서:
- 원본 PDF: [SOURCE_PDF_WINDOWS]
- 페이지 이미지 폴더: [PAGE_IMAGE_FOLDER_WINDOWS]

이번 작업 종류:
[TASK_TYPE]

이번 작업 범위:
[TASK_SCOPE]

반드시 먼저 할 일:
1. 기준 문서 2개를 먼저 읽는다.
2. 기준 문서의 규칙을 이번 작업에 적용한다.
3. 기준 문서와 이번 작업 지시가 충돌하면, 이번 작업 지시를 우선 적용하되 충돌 지점을 명시한다.

공통 작업 규칙:
- 없는 내용을 상상해서 채우지 말 것
- 불명확한 내용은 [unclear]로 표시할 것
- 요약하지 말 것
- 임의로 생략하지 말 것
- 이번 작업 범위를 벗어나지 말 것
- 구조를 무너뜨리지 말 것
- 표, 코드, 수식, 정규식, 캡션은 일반 문단과 분리할 것
- 출력 형식을 임의로 바꾸지 말 것

마지막에 반드시 아래를 포함할 것:
- 작업 신뢰도: 높음 / 중간 / 낮음
- 신뢰도 이유: ...
- 미해결 문제:
  - ...
  - ...
```

## Placeholder Guide
- `[PROJECT_NAME]`: short project name
- `[PROJECT_FOLDER_WINDOWS]`: root folder for the current textbook job
- `[BASELINE_DOC_1]`: usually `01-visual-structure-report.md`
- `[BASELINE_DOC_2]`: usually `02-production-rules.md`
- `[SOURCE_PDF_WINDOWS]`: source PDF path
- `[PAGE_IMAGE_FOLDER_WINDOWS]`: page image folder path
- `[TASK_TYPE]`: extraction / translation / glossary / QA / reconstruction note
- `[TASK_SCOPE]`: pages, section, or block range

## Recommended Pairing
- Common invoke template + `03-extraction-task-prompt.md`
- Common invoke template + future translation prompt
- Common invoke template + future QA prompt

## Example Task Types
- source text extraction
- Korean translation draft
- terminology glossary proposal
- block-level QA
- caption consistency check
