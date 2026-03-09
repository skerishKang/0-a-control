function deriveSessionDecision(session, records) {
  if (session.summary_md) return session.summary_md;
  const modelRecord = records.find((record) => record.role === "assistant" || record.role === "tool");
  return modelRecord?.content || "세션 종료 시 에이전트의 대화와 작업 결과를 바탕으로 핵심 판단이 요약됩니다.";
}

function deriveSessionNextAction(session, records) {
  if (Array.isArray(session.actions_json) && session.actions_json.length) {
    return session.actions_json.join(", ");
  }
  const lastUserRecord = [...records].reverse().find((record) => record.role === "user");
  if (lastUserRecord?.content) return lastUserRecord.content;
  return "세션 맥락을 분석하여 다음 단계에 필요한 구체적인 행동이 여기에 도출됩니다.";
}

function findLatestRecordBySourceType(records, sourceType) {
  return [...records].reverse().find((record) => record.source_type === sourceType);
}

function getAgentBadgeClass(agentName) {
  const name = (agentName || "").toLowerCase();
  if (name.includes("codex")) return "agent-codex";
  if (name.includes("gemini")) return "agent-gemini-cli";
  if (name.includes("windsurf")) return "agent-windsurf";
  return "agent-generic";
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

  const target = document.getElementById("sessionPanelRecords");
  if (!target) return;

  if (!filteredRecords.length) {
    target.innerHTML = `<div class="list-item empty">대화 기록이 없습니다.</div>`;
    return;
  }

  target.innerHTML = `
    <div class="transcript-container">
      ${filteredRecords.map((record) => {
    const role = normalizeRecordRole(record);
    const time = formatDateTime(record.created_at).slice(11, 16);
    return `
          <div class="chat-bubble ${role}">
            <span class="chat-meta">${escapeHtml(role.toUpperCase())} · ${time}</span>
            <div class="chat-content">${escapeHtml(record.content)}</div>
          </div>
        `;
  }).join("")}
    </div>
  `;
}

async function openSessionDetailPanel(sessionId) {
  if (!sessionId) return;
  
  const [session, recordsPayload] = await Promise.all([
    Promise.resolve(state.sessions.find((item) => item.id === sessionId)),
    fetchJson(`/api/sessions/records?session_id=${encodeURIComponent(sessionId)}&limit=100`)
  ]);

  if (!session) return;
  
  const records = recordsPayload.records || [];
  const sessionDecision = deriveSessionDecision(session, records);
  const sessionNextAction = deriveSessionNextAction(session, records);
  const questReport = findLatestRecordBySourceType(records, "quest_report")?.content || "이 세션에서 공식적으로 보고된 퀘스트 작업 결과가 없습니다.";
  const questVerdict = findLatestRecordBySourceType(records, "quest_verdict")?.content || "이 세션에서 생성된 AI 작업 판정 기록이 없습니다.";
  
  const meta = [
    session.agent_name,
    session.model_name,
    session.project_key,
    formatRecentLabel(session.started_at),
  ].filter(Boolean).join(" / ");

  const detailHtml = `
    <div class="session-panel-body">
      <div class="detail-section">
        <strong>기본 정보</strong>
        <p class="muted">${escapeHtml(meta)}</p>
      </div>
      <div class="session-panel-highlight-grid">
        <div class="detail-section highlight-box">
          <strong>핵심 판단</strong>
          <p class="muted">${escapeHtml(sessionDecision)}</p>
        </div>
        <div class="detail-section highlight-box">
          <strong>다음 액션</strong>
          <p class="muted">${escapeHtml(sessionNextAction)}</p>
        </div>
      </div>
      ${session.summary_md ? `<div class="detail-section"><strong>요약</strong><p class="muted">${escapeHtml(session.summary_md)}</p></div>` : ''}
      <div class="session-panel-highlight-grid">
        <div class="detail-section highlight-box">
          <strong>최근 퀘스트 보고</strong>
          <p class="muted">${escapeHtml(questReport)}</p>
        </div>
        <div class="detail-section highlight-box">
          <strong>최근 AI 판정</strong>
          <p class="muted">${escapeHtml(questVerdict)}</p>
        </div>
      </div>
      <div class="detail-section">
        <strong>대화 기록</strong>
        <div id="sessionRecordFilter" class="filter-chip-row compact"></div>
        <div id="sessionPanelRecords" class="list session-record-list"></div>
      </div>
    </div>
  `;

  openDetailPanel("세션 상세", session.title || session.project_key || "세션", detailHtml);
  
  // Now that the panel is open, render the records
  state.sessionPanelRecords = records;
  state.sessionRecordFilter = "all";
  renderSessionRecords();
}

function classifySession(session) {
  const title = (session.title || "").toLowerCase();
  const agent = (session.agent_name || "").toLowerCase();
  const summary = (session.summary_md || "").trim();

  // 1. Test 분류: 검증용 키워드
  if (["test", "dev", "debug", "smoke", "meta", "dummy"].some(k => title.includes(k)) || agent === "tester") {
    return "test";
  }
  // 2. Simulated 분류: 모델링/시뮬레이션용
  if (["sim", "model", "mock"].some(k => title.includes(k))) {
    return "simulated";
  }
  // 3. Operational 분류: 실제 대화/판정이 있었던 세션
  if (session.has_quest_verdict || summary.length > 20) {
    return "operational";
  }
  return "unknown";
}

function renderSessions() {
  const targetId = 'recentSessionList';
  const parentPanel = document.getElementById(targetId)?.parentElement;
  if (!parentPanel) return;

  renderSessionFilters();
  
  // Apply agent filter
  const allFilteredSessions = state.sessions.filter((item) => {
    if (!visibleSessionAgents.has(item.agent_name)) return false;
    if (state.sessionAgentFilter === "all") return true;
    return item.agent_name === state.sessionAgentFilter;
  });

  // Main view only shows operational
  const operationalSessions = allFilteredSessions
    .filter((s) => classifySession(s) === 'operational')
    .sort((a, b) => {
      const aTime = new Date(a.ended_at || a.started_at || 0).getTime();
      const bTime = new Date(b.ended_at || b.started_at || 0).getTime();
      return bTime - aTime;
    });

  setCountBadge("recentSessionCount", operationalSessions.length);
  parentPanel.classList.add("panel-browsing");

  const renderSessionCard = (item, isDetailed = false) => {
    const agentLabel = [item.agent_name, item.model_name].filter(Boolean).join(" / ");
    const summary = item.summary_md || "아직 세션 요약이 없습니다.";
    const category = classifySession(item);
    
    const verdictBadge = item.has_quest_verdict
      ? renderVerdictBadge(item.quest_verdict_status)
      : "";
    const agentBadge = `<span class="agent-badge ${getAgentBadgeClass(item.agent_name)}">${escapeHtml(item.agent_name)}</span>`;
    
    // category badge for non-operational sessions
    const categoryBadge = (isDetailed && category !== 'operational') 
      ? `<span class="session-badge verdict ${category === 'test' ? 'hold' : 'pending'}">${category.toUpperCase()}</span>` 
      : "";

    return `
      <div class="list-item session-link ${getAgentBadgeClass(item.agent_name)}" data-session-id="${escapeHtml(item.id)}">
        <div class="session-link-head">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            ${agentBadge}
            <strong>${escapeHtml(item.title || item.project_key || "세션")}</strong>
            ${categoryBadge}
          </div>
          ${verdictBadge}
        </div>
        <span class="session-link-summary">${escapeHtml(summary)}</span>
        <span>${escapeHtml(`${agentLabel} / ${formatRecentLabel(item.ended_at || item.started_at)}`)}</span>
      </div>
    `;
  };
  
  const categoryRank = {
    operational: 0,
    unknown: 1,
    test: 2,
    simulated: 3,
  };

  const categoryLabel = {
    operational: "운영 세션",
    unknown: "분류 미확정 세션",
    test: "테스트 세션",
    simulated: "시뮬레이션 세션",
  };

  parentPanel.onclick = () => {
    const sortedSessions = [...allFilteredSessions].sort((a, b) => {
      const categoryDiff = (categoryRank[classifySession(a)] ?? 99) - (categoryRank[classifySession(b)] ?? 99);
      if (categoryDiff !== 0) return categoryDiff;
      const aTime = new Date(a.ended_at || a.started_at || 0).getTime();
      const bTime = new Date(b.ended_at || b.started_at || 0).getTime();
      return bTime - aTime;
    });

    let lastCategory = null;
    const detailFormatter = (item) => {
      const category = classifySession(item);
      const headerHtml = category !== lastCategory
        ? `<div class="list-section-header">${escapeHtml(categoryLabel[category] || category.toUpperCase())}</div>`
        : "";
      lastCategory = category;
      const cardHtml = renderSessionCard(item, true);
      return `${headerHtml}<div onclick="openSessionDetailPanel('${item.id}')" class="clickable-item">${cardHtml}</div>`;
    };

    showDetailedList("최근 세션", "전체 세션 목록", sortedSessions, detailFormatter);
  };
  
  renderCappedList(targetId, operationalSessions, renderSessionCard, 3, "운영 세션 기록이 없습니다.");
}
