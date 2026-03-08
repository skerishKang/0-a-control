function deriveSessionDecision(session, records) {
  if (session.summary_md) return session.summary_md;
  const modelRecord = records.find((record) => record.role === "assistant" || record.role === "tool");
  return modelRecord?.content || "아직 핵심 판단이 정리되지 않았습니다.";
}

function deriveSessionNextAction(session, records) {
  if (Array.isArray(session.actions_json) && session.actions_json.length) {
    return session.actions_json.join(", ");
  }
  const lastUserRecord = [...records].reverse().find((record) => record.role === "user");
  if (lastUserRecord?.content) return lastUserRecord.content;
  return "다음 액션이 아직 기록되지 않았습니다.";
}

function findLatestRecordBySourceType(records, sourceType) {
  return [...records].reverse().find((record) => record.source_type === sourceType);
}

function renderSessionFilters() {
  const target = document.getElementById("sessionAgentFilter");
  if (!target) return;
  target.innerHTML = sessionAgentOptions
    .map(
      (option) => `
        <button
          type="button"
          class="filter-chip${state.sessionAgentFilter === option.value ? " active" : ""}"
          data-agent-filter="${escapeHtml(option.value)}"
        >
          ${escapeHtml(option.label)}
        </button>
      `
    )
    .join("");

  target.querySelectorAll("[data-agent-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      state.sessionAgentFilter = button.dataset.agentFilter || "all";
      renderSessions();
    });
  });
}

function normalizeRecordRole(record) {
  if (record.role === "assistant") return "assistant";
  if (record.role === "user") return "user";
  return "tool";
}

function renderSessionRecordFilters() {
  const target = document.getElementById("sessionRecordFilter");
  if (!target) return;
  target.innerHTML = sessionRecordOptions
    .map(
      (option) => `
        <button
          type="button"
          class="filter-chip${state.sessionRecordFilter === option.value ? " active" : ""}"
          data-record-filter="${escapeHtml(option.value)}"
        >
          ${escapeHtml(option.label)}
        </button>
      `
    )
    .join("");

  target.querySelectorAll("[data-record-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      state.sessionRecordFilter = button.dataset.recordFilter || "all";
      renderSessionRecords();
    });
  });
}

function renderSessionRecords() {
  renderSessionRecordFilters();
  const filteredRecords = state.sessionPanelRecords.filter((record) => {
    if (state.sessionRecordFilter === "all") return true;
    return normalizeRecordRole(record) === state.sessionRecordFilter;
  });
  renderList("sessionPanelRecords", filteredRecords, (record) =>
    formatItem(`[${record.role || "record"}] ${record.content}`, formatDateTime(record.created_at))
  );
}

function renderSessions() {
  renderSessionFilters();
  const filteredSessions = state.sessions.filter((item) => {
    if (!visibleSessionAgents.has(item.agent_name)) return false;
    if (state.sessionAgentFilter === "all") return true;
    return item.agent_name === state.sessionAgentFilter;
  });
  setCountBadge("recentSessionCount", filteredSessions.length);

  const target = document.getElementById("recentSessionList");
  if (!filteredSessions.length) {
    target.innerHTML = `<div class="list-item empty">작업을 시작하면 여기에 세션이 쌓입니다.</div>`;
    return;
  }

  const renderSessionCard = (item) => {
    const agent = [item.agent_name, item.model_name].filter(Boolean).join(" / ");
    const summary = item.summary_md || "아직 세션 요약이 없습니다.";
    const verdictBadge = item.has_quest_verdict
      ? renderVerdictBadge(item.quest_verdict_status) || `<span class="session-badge">AI 판정</span>`
      : "";
    return `
      <button type="button" class="list-item session-link" data-session-id="${escapeHtml(item.id)}">
        <div class="session-link-head">
          <strong>${escapeHtml(item.title || item.project_key || "세션")}</strong>
          ${verdictBadge}
        </div>
        <span class="session-link-summary">${escapeHtml(summary)}</span>
        <span>${escapeHtml(`${agent} / ${formatRecentLabel(item.ended_at || item.started_at)}`)}</span>
      </button>
    `;
  };

  const primary = filteredSessions.slice(0, 4).map(renderSessionCard).join("");
  const rest = filteredSessions.slice(4).map(renderSessionCard).join("");
  target.innerHTML = rest
    ? `
      ${primary}
      <details class="list-more">
        <summary>나머지 세션 보기</summary>
        <div class="list-more-list">
          ${rest}
        </div>
      </details>
    `
    : primary;

  document.querySelectorAll(".session-link").forEach((button) => {
    button.addEventListener("click", async () => {
      const sessionId = button.dataset.sessionId;
      if (!sessionId) return;
      const payload = await fetchJson(`/api/sessions/records?session_id=${encodeURIComponent(sessionId)}&limit=100`);
      const session = state.sessions.find((item) => item.id === sessionId);
      state.sessionRecordFilter = "all";
      state.sessionPanelRecords = payload.records || [];
      document.getElementById("sessionPanelTitle").textContent = session?.title || session?.project_key || "세션";
      document.getElementById("sessionPanelMeta").textContent = [
        session?.agent_name,
        session?.model_name,
        session?.project_key,
        formatDateTime(session?.started_at),
      ]
        .filter(Boolean)
        .join(" / ");
      document.getElementById("sessionPanelSummary").textContent = session?.summary_md || "아직 세션 요약이 없습니다.";
      document.getElementById("sessionPanelDecision").textContent = deriveSessionDecision(session || {}, payload.records || []);
      document.getElementById("sessionPanelNextAction").textContent = deriveSessionNextAction(session || {}, payload.records || []);
      document.getElementById("sessionPanelQuestReport").textContent =
        findLatestRecordBySourceType(payload.records || [], "quest_report")?.content || "아직 퀘스트 보고가 없습니다.";
      document.getElementById("sessionPanelQuestVerdict").textContent =
        findLatestRecordBySourceType(payload.records || [], "quest_verdict")?.content || "아직 AI 판정 기록이 없습니다.";
      renderSessionRecords();
      openSessionPanel();
    });
  });
}
