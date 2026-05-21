from __future__ import annotations

try:
    from scripts.services import agent_registry as _impl
except ModuleNotFoundError:
    from services import agent_registry as _impl

AgentSpec = _impl.AgentSpec
AGENT_SPECS = _impl.AGENT_SPECS
CANONICAL_AGENTS = _impl.CANONICAL_AGENTS
EXECUTABLES = _impl.EXECUTABLES
SPEC_BY_NAME = _impl.SPEC_BY_NAME
canonical_agent_name = _impl.canonical_agent_name
resolve_executable = _impl.resolve_executable
get_agent_spec = _impl.get_agent_spec
list_registered_agents = _impl.list_registered_agents
get_running_agent_names = _impl.get_running_agent_names


def get_agent_statuses() -> list[dict]:
    _impl.get_running_agent_names = get_running_agent_names
    return _impl.get_agent_statuses()
