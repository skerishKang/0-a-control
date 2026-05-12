# Agent Work Runner Extraction Plan

Refs #118.

## Purpose

`scripts/agent-work.sh` is the operational wrapper for starting agent work sessions. It currently handles several responsibilities in one shell script. This document defines a safe extraction path without changing behavior immediately.

## Current responsibilities

The wrapper currently handles:

1. Project root and workdiary root resolution.
2. Workspace path resolution.
3. Python interpreter detection.
4. Agent executable resolution through `agent_registry`.
5. Session creation through `workon.sh`.
6. Runtime session file reading.
7. Resume prompt construction and injection.
8. Transcript path setup.
9. Platform-specific command adaptation.
10. Transcript import during cleanup.
11. Session closing and runtime file cleanup.

## Pain points

- Shell code is harder to unit test than Python code.
- Platform-specific branches for Windows, Git Bash, WSL, and Unix `script` behavior are coupled with session lifecycle logic.
- Cleanup performs multiple stateful actions, so failures need clearer logging and recovery steps.
- Adding new agent types increases the risk of accidental behavior changes.

## Extraction principle

Keep shell wrappers thin. Move deterministic orchestration logic into Python where it can be tested.

The shell layer should eventually do only:

1. Resolve repository root.
2. Invoke a Python runner with original arguments.
3. Preserve terminal/transcript behavior where shell-specific handling is unavoidable.

## Proposed target modules

```text
scripts/
  agent_runner.py
  agent_runner_paths.py
  agent_runner_session.py
  agent_runner_transcript.py
```

Suggested responsibilities:

| Module | Responsibility |
| --- | --- |
| `agent_runner.py` | top-level orchestration |
| `agent_runner_paths.py` | root/workspace/path resolution |
| `agent_runner_session.py` | session start, resume context, session end |
| `agent_runner_transcript.py` | transcript import and cleanup helpers |

## Safe migration sequence

1. Add tests for path/workspace resolution behavior.
2. Extract Python helper for workspace resolution only.
3. Extract session metadata/resume prompt construction.
4. Extract cleanup status reporting.
5. Leave terminal execution behavior in shell until platform behavior is well covered.

## Compatibility requirements

- Existing invocation form must keep working:

```bash
bash scripts/agent-work.sh <tool> <project-or-path> <title> [model] [-- tool args...]
```

- Existing wrapper scripts should not need to change during the first extraction step.
- The runner must preserve `CONTROL_TOWER_SESSION_ID` behavior.
- Transcript import should remain best-effort and should not prevent cleanup.

## Recovery notes to add in follow-up

Future implementation should document manual recovery for:

- session started but tool failed before transcript capture
- transcript exists but import failed
- runtime session file remains after interrupted process
- current session file points to a non-existent session

## Non-goals

- Do not replace the agent registry in this work.
- Do not change supported agent names.
- Do not change prompt semantics while extracting mechanics.
