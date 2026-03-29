# Antigravity Session Skill Conversion Prompt

Below is the prompt to give directly to Antigravity.

---

Convert the attached session-recovery design into an Antigravity-native skill.

Source documents:
- `G:\Ddrive\BatangD\task\workdiary\0-a-control\docs\skills\session-recovery-skill\01-session-architecture-prompt.md`
- `G:\Ddrive\BatangD\task\workdiary\0-a-control\docs\skills\session-recovery-skill\02-codex-session-skill.md`

Goal:
- Build an Antigravity-native skill that can recover prior Codex work context from:
  - `~/.codex/state_5.sqlite`
  - `~/.codex/history.jsonl`
  - optional local `sessions/` and `sessions_html/`

The skill must:
1. preserve the distinction between raw source, summary, and display
2. reconstruct work state by topic
3. report what is done, what remains, and what to do next
4. clearly state when assistant replies are unavailable

Required topics:
- board-v2
- 0-a-control skills
- 메가존
- 아파트

Output format required:
- topic-by-topic recovery
- next priority
- whether handoff is additionally needed

Important:
- Do not collapse raw logs into summary
- Do not confuse HTML display files with source of truth
- Make the skill automatically applicable when the user asks to:
  - recover a Codex session
  - resume previous work
  - inspect `.codex` session history

Output:
1. Antigravity-native skill content
2. installation/use instructions
3. one short test prompt

---
