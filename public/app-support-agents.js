/**
 * Agent Status rendering module for Classic UI
 */

function labelAgentStatus(status) {
  return {
    working: "작업 중",
    idle: "대기",
    stale: "정리 필요",
    error: "오류",
    unavailable: "미설치",
  }[status] || status || "";
}

function formatAgentTimestamp(value) {
  if (!value) return "";
  if (typeof formatRecentLabel === "function") {
    const recent = formatRecentLabel(value);
    if (recent) return recent;
  }
  if (typeof formatDateTime === "function") return formatDateTime(value);
  return String(value);
}

function renderAgentStatusSection(state) {
  const targetId = "agentStatusList";
  const container = document.getElementById(targetId);
  if (!container) return;

  const parentPanel = container.parentElement;
  if (parentPanel) parentPanel.classList.add("panel-browsing");

  const items = (state.agents || []).slice().sort((a, b) => {
    const statusOrder = { working: 0, stale: 1, error: 2, idle: 3, unavailable: 4 };
    const aOrder = statusOrder[a.status] ?? 9;
    const bOrder = statusOrder[b.status] ?? 9;
    if (aOrder !== bOrder) return aOrder - bOrder;
    return String(a.label || a.canonical_name || "").localeCompare(String(b.label || b.canonical_name || ""));
  });

  setCountBadge("agentStatusCount", items.length);

  if (!items.length) {
    container.innerHTML = `<div class="list-item empty">에이전트 상태 정보를 아직 불러오지 못했습니다.</div>`;
    return;
  }

  const staleItems = items.filter((item) => item.status === "stale");
  const topItems = items.slice(0, 4);
  const topActions = staleItems.length
    ? `<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px;"><button type="button" class="secondary-btn" onclick="cleanupAllStaleAgents()">전체 정리 (${staleItems.length})</button></div>`
    : "";

  container.innerHTML = topActions + topItems.map((item) => {
    const latest = item.last_session || {};
    const latestDisplay = latest.title ? normalizeSessionTitleLabel(latest.title) : formatAgentTimestamp(latest.started_at);
    const latestText = item.status === "stale"
      ? `활성 세션 기록 남음: ${latestDisplay || "최근 세션 없음"}`
      : (latestDisplay || "최근 세션 없음");
    return `
      <div class="list-item candidate-item">
        <div class="candidate-head">
          <strong>${escapeHtml(item.label || item.canonical_name || "agent")}</strong>
          <span class="session-badge agent-status-badge ${escapeHtml(item.status || "idle")}">${escapeHtml(labelAgentStatus(item.status))}</span>
        </div>
        <span class="candidate-reason">${escapeHtml(latestText)}</span>
      </div>
    `;
  }).join("");

  if (parentPanel) {
    parentPanel.onclick = () => {
      showDetailedList("에이전트 상태", "실행기 상태와 최근 세션", items, (item) => {
        const latest = item.last_session || {};
        const latestTitle = latest.title ? normalizeSessionTitleLabel(latest.title) : formatAgentTimestamp(latest.started_at);
        const latestLines = [
            latest.title || latest.started_at ? `최근 세션: ${latestTitle}` : "최근 세션: 없음",
            latest.status ? `세션 상태: ${latest.status}` : "",
            latest.started_at ? `시작: ${formatAgentTimestamp(latest.started_at)}` : "",
            latest.ended_at ? `종료: ${formatAgentTimestamp(latest.ended_at)}` : "",
            item.resolved_path ? `실행 파일: ${item.resolved_path}` : `실행 파일: ${item.executable || "-"}`,
            item.status === "stale" ? "실행 프로세스는 없지만 active 세션 기록이 남아 있음" : "",
          ].filter(Boolean);
        const actionButton = item.status === "stale"
          ? `<div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap;"><button type="button" class="secondary-btn" onclick="cleanupStaleAgentSession('${escapeHtml(item.canonical_name)}')">stale 세션 정리</button><button type="button" class="secondary-btn" onclick="cleanupAllStaleAgents()">전체 정리 (${staleItems.length})</button></div>`
          : "";
        return `
          <div class='list-item'>
            <strong>${escapeHtml(item.label || item.canonical_name || "agent")}</strong>
            <p class='muted'>상태: ${escapeHtml(labelAgentStatus(item.status))}</p>
            <p class='muted'>${escapeHtml(latestLines.join(" / "))}</p>
            ${actionButton}
          </div>
        `;
      });
    };
  }
}

window.cleanupStaleAgentSession = async function cleanupStaleAgentSession(agentName) {
  if (!agentName) return;
  const label = (state.agents || []).find((item) => item.canonical_name === agentName)?.label || agentName;
  if (!window.confirm(`${label}의 stale 세션을 정리할까요?`)) return;
  try {
    await fetchJson("/api/agents/cleanup-stale", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agent_name: agentName }),
    });
    await loadAll();
  } catch (error) {
    console.error("Failed to clean stale agent session:", error);
    alert(`stale 세션 정리에 실패했습니다: ${error.message || error}`);
  }
};

window.cleanupAllStaleAgents = async function cleanupAllStaleAgents() {
  const staleAgents = (state.agents || []).filter((item) => item.status === "stale");
  if (!staleAgents.length) return;
  const preview = staleAgents.slice(0, 5).map((item) => item.label || item.canonical_name || "agent").join(", ");
  const suffix = staleAgents.length > 5 ? ` 외 ${staleAgents.length - 5}개` : "";
  if (!window.confirm(`stale 상태인 에이전트 ${staleAgents.length}개를 모두 정리할까요?\n${preview}${suffix}`)) return;
  try {
    for (const agent of staleAgents) {
      await fetchJson("/api/agents/cleanup-stale", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent_name: agent.canonical_name }),
      });
    }
    await loadAll();
  } catch (error) {
    console.error("Failed to clean all stale agent sessions:", error);
    alert(`전체 stale 세션 정리에 실패했습니다: ${error.message || error}`);
  }
};
