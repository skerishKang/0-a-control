# Antigravity Skill Draft

## Skill Name
`playwright-cli-0-a-control`

## Purpose
Use Playwright-CLI from Antigravity to control the local `0-a-control` board at `http://localhost:4310` through structured repeated workflows.

This is an operations skill for a known site, not an exploration tool.

## Primary Workflows

### A. Current State Summary
- open the board
- read current operating focus
- return:
  - main mission
  - current quest
  - why now

### B. Completed View Summary
- open the board
- switch to `완료`
- summarize:
  - today completed
  - recent completed
  - partial/hold-like items if visible

### C. Quick Input Submission
- open the board
- locate quick input
- enter operator text
- submit
- report whether the action succeeded

## Input Schema

```yaml
site_name: 0-a-control
url: http://localhost:4310
workflow: current_state | completed_summary | quick_input_submit
params:
  text: optional
artifacts:
  screenshot: true
  video: false
```

## Execution Sequence
1. Open `http://localhost:4310`.
2. Confirm the main UI is visible.
3. Take a screenshot if artifact capture is enabled.
4. Perform exactly one requested workflow.
5. Return a concise Korean summary.

## Safety / Stop Rules
- If the server does not respond, stop and report that the local service is unavailable.
- If the expected control is absent, stop after one screenshot.
- Do not wander into unrelated tabs or exploratory clicks.
- If the page structure looks different from the stored profile, recommend re-profiling instead of guessing.

## Recommended Prompt Style

### Current State
`0-a-control을 열고 현재 메인 미션, 현재 퀘스트, why now를 읽어서 짧게 보고해줘.`

### Completed Summary
`0-a-control에서 완료 탭으로 가서 오늘 완료와 최근 완료를 요약해줘.`

### Quick Input
`0-a-control quick input에 '내일 첫 퀘스트는 메가존 송달일 확인'을 입력하고 제출해줘.`

## Response Contract

### For Current State
- `메인 미션`
- `현재 퀘스트`
- `why now`

### For Completed Summary
- `오늘 완료`
- `최근 완료`
- `부분 완료` (if visible)

### For Quick Input
- `입력 텍스트`
- `제출 성공 여부`
- `보이는 반응`

## Notes
- This skill is intentionally narrow.
- Repeated success on one site is more important than broad site coverage.
- If this works reliably, clone the same pattern for other repeated web tasks.

