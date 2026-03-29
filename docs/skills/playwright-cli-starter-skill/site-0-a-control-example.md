# 0-a-control Site Profile Example

## Basic Info
- `site_name`: `0-a-control`
- `url`: `http://localhost:4310`
- `environment`: `local server`
- `primary_goal`: `read the current control state, inspect completed work, and submit quick operational input`

## Why This Site Is a Good First Skill Target
- We use it repeatedly.
- The workflow is stable and easy to verify.
- The expected outputs are mostly text, which is easy for an agent to report back.
- We control the product, so selectors and workflow can be improved later if needed.

## Repeated Workflow Targets

### Workflow A: Read Current State
Goal:
- Open `0-a-control`
- Stay on the default dashboard or current tab
- Read and summarize:
  - main mission
  - current quest
  - why now

Expected output:
- A short text summary of the current operating focus

### Workflow B: Read Completed Work
Goal:
- Open `0-a-control`
- Switch to the `완료` tab
- Read and summarize:
  - today completed
  - recent completed
  - notable partial items if visible

Expected output:
- A short text summary of what has already been finished

### Workflow C: Submit Quick Input
Goal:
- Open `0-a-control`
- Locate the quick input field
- Enter a short operational note
- Submit it
- Confirm whether the input was accepted or reflected in the UI

Expected output:
- Submission confirmation
- Any visible UI response or failure note

## Suggested Skill Input Contract

```yaml
site_name: 0-a-control
url: http://localhost:4310
goal: read_current_state
inputs: {}
expected_output:
  - main mission
  - current quest
  - why now
artifacts:
  screenshot: true
  video: false
```

## Example Natural-Language Commands

### Example 1
`0-a-control을 열고 현재 메인 미션, 현재 퀘스트, why now를 짧게 요약해줘.`

### Example 2
`0-a-control에서 완료 탭으로 가서 오늘 완료와 최근 완료를 요약해줘.`

### Example 3
`0-a-control quick input에 '메가존 지급명령 송달일 확인 필요'를 넣고 제출해줘.`

## Expected Page Areas

### Current / Main Area
- Main mission card
- Current quest card
- Why now / context panel

### Completed Area
- Today completed list
- Partial / hold-like section if present
- Recent completed list
- Full completed list toggle if present

### Input Area
- Quick input text field
- Submit button

## Failure Rules
- If the page does not load, stop and report that the local server is unavailable.
- If the expected tab is not visible, take a screenshot and report selector drift.
- If the quick input field is not found, do not guess wildly; report the missing control.
- If the UI looks different from the expected profile, stop and request a one-time MCP-style exploration or manual re-profiling.

## Recommended First Validation Sequence
1. Open `http://localhost:4310`
2. Read the current view and identify main mission / current quest
3. Switch to `완료`
4. Summarize today completed and recent completed
5. Return to the main working view if needed
6. Submit one harmless quick input test line

## Why This Still Needs Exploration Once
Even though this is our own site, the first run should still verify:
- actual tab labels
- quick input selector
- completed tab structure
- whether screenshots alone are enough or video is needed

After that, this becomes a strong candidate for a repeatable Playwright-CLI skill.
