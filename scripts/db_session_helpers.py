from __future__ import annotations


def _compact_text(content: str, limit: int = 300) -> str:
    text = " ".join((content or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _format_resume_prompt(
    project_key: str,
    title: str,
    state: dict,
    previous_sessions: list[dict],
    recent_turns: list[dict],
    compact: bool = False,
) -> str:
    lines = [
        f"Resume work in project `{project_key or 'unknown-project'}`.",
        f"Session title: {title or 'untitled session'}",
        "",
        "Use this stored memory as a starting brief, not as ground truth.",
        "If the repository or SQLite state disagrees, trust the live state and note the mismatch.",
        "",
        "Current control state:",
        f"- Main mission: {state.get('main_mission_title') or '-'}",
        f"- Current quest: {state.get('current_quest_title') or '-'}",
        f"- Restart point: {state.get('restart_point') or '-'}",
        f"- Recommended next quest: {state.get('recommended_next_quest') or '-'}",
    ]

    if compact and previous_sessions:
        latest = previous_sessions[0]
        lines.extend(
            [
                "",
                "Latest prior session:",
                f"- {latest.get('started_at') or '-'} | {latest.get('agent_name') or '-'} | {latest.get('title') or '(untitled)'}",
                f"- Summary: {latest.get('summary_md') or '-'}",
            ]
        )
    elif previous_sessions:
        lines.extend(["", "Recent sessions:"])
        for session in previous_sessions:
            lines.append(
                f"- {session.get('started_at') or '-'} | {session.get('agent_name') or '-'} | {session.get('title') or '(untitled)'}"
            )
            lines.append(f"  summary: {session.get('summary_md') or '-'}")

    if recent_turns and not compact:
        lines.extend(["", "Recent key turns from the latest prior session:"])
        for turn in recent_turns:
            lines.append(f"- {turn['role']}: {turn['content']}")
    elif state.get("_transcript_excerpt"):
        lines.extend(["", "Recent transcript excerpt from the latest prior session:"])
        for line in state["_transcript_excerpt"]:
            lines.append(f"- {line}")

    lines.extend(
        [
            "",
            "Start by validating the restart point against the current codebase, then continue with the next concrete quest.",
        ]
    )
    return "\n".join(lines).strip()