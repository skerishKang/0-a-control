# Antigravity Conversion Prompt

Below is the prompt to give directly to Antigravity.

---

You are running inside Antigravity. Convert the following local skill design documents into an Antigravity-native, actually usable skill or automation instruction package.

Source documents:
- `G:\Ddrive\BatangD\task\workdiary\0-a-control\docs\skills\playwright-cli-starter-skill\SKILL.md`
- `G:\Ddrive\BatangD\task\workdiary\0-a-control\docs\skills\playwright-cli-starter-skill\site-0-a-control-example.md`
- `G:\Ddrive\BatangD\task\workdiary\0-a-control\docs\skills\playwright-cli-starter-skill\antigravity-skill.md`

Target:
- Create the real Antigravity-native skill/instruction format that Antigravity can actually use.
- Preserve the operational rules, but express them in Antigravity's own format and conventions.

Purpose of the skill:
- Repeated browser automation on `0-a-control`
- URL: `http://localhost:4310`
- Known workflows only:
  1. Read current state
  2. Read completed work
  3. Submit quick input

Critical requirement:
- The final Antigravity-native skill must be structured so Antigravity can automatically pick it when the user asks for:
  - `0-a-control 열어줘`
  - `메인 미션/현재 퀘스트 읽어줘`
  - `완료 탭 요약해줘`
  - `quick input 넣어줘`
  - similar repeated browser tasks on the same local site

You must include:
1. Trigger conditions
   - when Antigravity should automatically apply the skill
   - when it should avoid using the skill
2. Exact repeated workflow handling for:
   - current state summary
   - completed summary
   - quick input submission
3. Stop conditions and fallback
   - local server unavailable
   - selector drift
   - missing control
4. Output contract
   - concise Korean summary
5. Artifact policy
   - screenshot by default
   - video only when explicitly requested or for debugging

Important constraints:
- This is not for open-ended browsing.
- This is not for first-time page exploration.
- It is for repeated operation on a known local site.
- If the expected structure is missing, stop and report clearly.

Output format:
1. Antigravity-native skill/instruction content
2. Any required placement or registration instructions
3. One short test prompt for each of the 3 workflows

---
