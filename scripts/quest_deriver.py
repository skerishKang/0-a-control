from __future__ import annotations

from scripts.services import quest_deriver as _impl

ROOT_DIR = _impl.ROOT_DIR
CONTEXT_PATH = _impl.CONTEXT_PATH
OUTPUT_PATH = _impl.OUTPUT_PATH
DERIVE_RULES = _impl.DERIVE_RULES
SIGNAL_PRIORITY = _impl.SIGNAL_PRIORITY


def _sync_paths() -> None:
    _impl.CONTEXT_PATH = CONTEXT_PATH
    _impl.OUTPUT_PATH = OUTPUT_PATH


def load_context() -> dict:
    _sync_paths()
    return _impl.load_context()


def rule_git_uncommitted(ctx: dict) -> list[dict]:
    return _impl.rule_git_uncommitted(ctx)


def rule_session_resume(ctx: dict) -> list[dict]:
    return _impl.rule_session_resume(ctx)


def rule_stale_branch(ctx: dict) -> list[dict]:
    return _impl.rule_stale_branch(ctx)


def rule_recent_activity_no_commit(ctx: dict) -> list[dict]:
    return _impl.rule_recent_activity_no_commit(ctx)


def derive_suggestions() -> dict:
    _sync_paths()
    return _impl.derive_suggestions()


def main() -> None:
    _sync_paths()
    _impl.main()


if __name__ == "__main__":
    main()
