# Kilo Code Conversion Prompt

Below is the prompt to give directly to Kilo Code.

---

You are running inside Kilo Code. Convert the following local skill design documents into a Kilo-native, actually usable skill or prompt package.

Source documents:
- `G:\Ddrive\BatangD\task\workdiary\0-a-control\docs\skills\playwright-cli-starter-skill\SKILL.md`
- `G:\Ddrive\BatangD\task\workdiary\0-a-control\docs\skills\playwright-cli-starter-skill\site-0-a-control-example.md`
- `G:\Ddrive\BatangD\task\workdiary\0-a-control\docs\skills\playwright-cli-starter-skill\kilo-code-skill.md`

Target:
- Create the real Kilo Code skill/instruction format that Kilo can actually load or use.
- Do not rewrite the operational intent. Adapt it to Kilo's actual format and conventions.

Purpose of the skill:
- Repeated browser work on `0-a-control`
- URL: `http://localhost:4310`
- Known workflows only:
  1. Read current state
  2. Read completed work
  3. Submit quick input

Critical requirement:
- The final Kilo-native skill must be written so Kilo can automatically choose it when the user asks for:
  - `0-a-control 열기`
  - `메인 미션/현재 퀘스트 확인`
  - `완료 탭 확인`
  - `quick input 입력`
  - similar repeated local browser actions on `http://localhost:4310`

You must include:
1. Trigger conditions
   - when Kilo should automatically use this skill
   - when Kilo should not use this skill
2. Exact workflow handling for:
   - current state summary
   - completed summary
   - quick input submission
3. Failure rules
   - server unavailable
   - missing tab/control
   - layout drift
4. Output contract
   - always return concise Korean text summary
5. Minimal artifact policy
   - screenshot by default
   - video only for debugging/demo

Important constraints:
- This is not an exploratory browser skill.
- This is not a general-purpose web skill.
- This is for repeated operations on a known site only.
- If the page structure drifts, the skill should stop and report, not guess wildly.

Output format:
1. Kilo-native skill file content
2. Any required installation location or registration instructions
3. One short test prompt for each of the 3 workflows

---
