# 31. External Skills Registry

`0-a-control` keeps policy and inventory for externally installed Codex skills.
Actual runnable skills should live in the global Codex skills directory so every project can use the same installation.

## Rule

- Install reusable Codex skills globally in `C:\Users\limone\.codex\skills`
- Track the reason, source, and intended usage in `0-a-control`
- Do not duplicate full skill payloads into each project unless a project-specific fork is required

## Installed External Skills

### `hwpx`

- Source: `https://github.com/Canine89/hwpxskill`
- Installed path: `C:\Users\limone\.codex\skills\hwpx`
- Installed as: global Codex skill
- Reason:
  - HWPX document generation/editing/parsing is reusable across multiple projects
  - `24-1-ipu-ai-firewall` already has HWPX parsing logic, but this skill is broader and can be reused for structured document work
  - `0-a-control` should remember that this capability exists even though the executable skill is global

## Operating Guidance

- If a skill is reusable across projects, prefer global installation
- If a skill contains project-specific workflows, keep only the policy/index in `0-a-control` and fork the skill later if needed
- When adding another external skill, append it here with:
  - source URL
  - install path
  - why it exists
  - which projects may use it
