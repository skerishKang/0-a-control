# Kilo Code Skill Draft

## Skill Name
`playwright-cli-0-a-control`

## Purpose
Use Playwright-CLI from Kilo Code to automate repeated interactions with `0-a-control` at `http://localhost:4310`.

This skill is for repeated operational workflows, not first-time site exploration.

## Use This Skill When
- the site structure is already known
- the task is repetitive
- the result can be summarized as text
- one of these workflows is needed:
  - read current state
  - read completed work
  - submit quick input

## Do Not Use This Skill When
- the site layout has recently changed
- the required element is unknown
- login or unexpected modal handling is needed
- the task is exploratory rather than repetitive

## Target Site
- `site_name`: `0-a-control`
- `url`: `http://localhost:4310`

## Supported Workflows

### 1. Read Current State
Goal:
- open `0-a-control`
- identify the main working view
- extract:
  - main mission
  - current quest
  - why now

Output:
- concise text summary

### 2. Read Completed Work
Goal:
- open `0-a-control`
- switch to `완료`
- extract:
  - today completed
  - recent completed
  - partial items if clearly visible

Output:
- concise completion summary

### 3. Submit Quick Input
Goal:
- open `0-a-control`
- find quick input
- type supplied text
- submit
- confirm visible response

Output:
- submission result summary

## Input Contract

```yaml
site_name: 0-a-control
url: http://localhost:4310
goal: read_current_state | read_completed | submit_quick_input
payload:
  quick_input_text: optional
artifacts:
  screenshot: true
  video: false
```

## Execution Rules
1. Open the URL.
2. Wait for the main board to render.
3. Capture a screenshot before critical actions if screenshot mode is enabled.
4. Execute only the requested workflow.
5. Summarize results in plain Korean text.
6. Stop immediately if the expected control is missing.

## Failure Rules
- If the local server is unreachable, report that the site is not available.
- If the expected tab or field is not found, take a screenshot and stop.
- Do not guess selectors repeatedly.
- If the UI seems changed, recommend one-time MCP/manual re-profiling.

## Natural Language Invocation Examples

### Example A
`0-a-control을 열고 현재 메인 미션과 현재 퀘스트를 요약해줘.`

### Example B
`0-a-control 완료 탭으로 가서 오늘 완료와 최근 완료를 짧게 정리해줘.`

### Example C
`0-a-control quick input에 '메가존 지급명령 송달일 확인 필요'를 입력하고 제출해줘.`

## Expected Output Format

### Read Current State
- `메인 미션: ...`
- `현재 퀘스트: ...`
- `왜 지금: ...`

### Read Completed
- `오늘 완료: ...`
- `최근 완료: ...`
- `부분 완료: ...` (only if clearly visible)

### Submit Quick Input
- `입력 내용: ...`
- `제출 결과: 성공/실패`
- `화면 반응: ...`

## Operational Notes
- Prefer screenshots over video for normal operation.
- Use video only for debugging repeated failure or demo recording.
- Keep summaries short and factual.

