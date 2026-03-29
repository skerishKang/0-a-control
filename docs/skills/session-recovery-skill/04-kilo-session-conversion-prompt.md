# Kilo Session Skill Conversion Prompt

Below is the prompt to give directly to Kilo Code.

---

Convert the attached session-recovery design into a Kilo-native skill.

Source documents:
- `G:\Ddrive\BatangD\task\workdiary\0-a-control\docs\skills\session-recovery-skill\01-session-architecture-prompt.md`
- `G:\Ddrive\BatangD\task\workdiary\0-a-control\docs\skills\session-recovery-skill\02-codex-session-skill.md`

Goal:
- Build a Kilo-native skill that can recover prior Codex work context from:
  - `~/.codex/state_5.sqlite`
  - `~/.codex/history.jsonl`
  - optional local session folders

The skill must:
1. distinguish raw source vs summary vs display
2. reconstruct current work state by topic
3. show what is done / what remains / next action
4. tell the user when assistant messages are unavailable

Required topics:
- board-v2
- 0-a-control skills
- 메가존
- 아파트

Trigger intent examples:
- `이전 codex 세션 복원해줘`
- `codex 세션 읽어서 이어갈 일 정리해줘`
- `resume previous codex work`

Important:
- Prefer actual local evidence over guesses
- Do not treat HTML views as the raw source of truth
- Make the skill usable for repeat session recovery

Output:
1. Kilo-native skill content
2. installation location/instructions
3. one short test prompt

---
