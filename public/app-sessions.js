function deriveSessionDecision(session, records) {
  if (session.summary_md) return session.summary_md;
  const modelRecord = records.find((record) => record.role === "assistant" || record.role === "tool");
  return modelRecord?.content || "세션 종료 시점의 작업 결과를 바탕으로 판단 요약이 필요합니다.";
}

function deriveSessionNextAction(session, records) {
  if (Array.isArray(session.actions_json) && session.actions_json.length) {
    return session.actions_json.join(", ");
  }
  const lastUserRecord = [...records].reverse().find((record) => record.role === "user");
  if (lastUserRecord?.content) return lastUserRecord.content;
  return "세션 마지막 흐름을 바탕으로 다음 시작 지점을 정리해야 합니다.";
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

function renderSessionDetailTabs() {
  const target = document.getElementById("sessionDetailTabs");
  if (!target) return;
  const tabs = [
    { value: "summary", label: "요약" },
    { value: "dialogue", label: "대화기록" },
    { value: "transcript", label: "원문 transcript" },
  ];
  target.innerHTML = tabs
    .map(
      (tab) => `
        <button
          type="button"
          class="filter-chip${state.sessionDetailTab === tab.value ? " active" : ""}"
          data-session-tab="${escapeHtml(tab.value)}"
        >
          ${escapeHtml(tab.label)}
        </button>
      `
    )
    .join("");

  target.querySelectorAll("[data-session-tab]").forEach((button) => {
    button.addEventListener("click", () => {
      state.sessionDetailTab = button.dataset.sessionTab || "summary";
      renderSessionPanelContent();
    });
  });
}

function renderTranscriptModeTabs(transcript) {
  const target = document.getElementById("sessionTranscriptModeTabs");
  if (!target || !transcript?.available) return;
  const hasRaw = Boolean(transcript.raw_content);
  const hasCleaned = Boolean(transcript.cleaned_content || transcript.content);
  const modes = [
    { value: "cleaned", label: "정리본", disabled: !hasCleaned },
    { value: "raw", label: "원문", disabled: !hasRaw },
  ];

  if ((state.sessionTranscriptMode === "raw" && !hasRaw) || (state.sessionTranscriptMode === "cleaned" && !hasCleaned)) {
    state.sessionTranscriptMode = hasCleaned ? "cleaned" : "raw";
  }

  target.innerHTML = modes
    .filter((mode) => !mode.disabled)
    .map(
      (mode) => `
        <button
          type="button"
          class="filter-chip${state.sessionTranscriptMode === mode.value ? " active" : ""}"
          data-transcript-mode="${escapeHtml(mode.value)}"
        >
          ${escapeHtml(mode.label)}
        </button>
      `
    )
    .join("");

  target.querySelectorAll("[data-transcript-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      state.sessionTranscriptMode = button.dataset.transcriptMode || "cleaned";
      renderSessionPanelContent();
    });
  });
}

function renderTranscriptActions(transcriptText, sessionTitle, transcriptMode) {
  const target = document.getElementById("sessionTranscriptActions");
  if (!target || !transcriptText) return;
  target.innerHTML = `
    <button type="button" class="filter-chip" data-transcript-action="copy">복사</button>
    <button type="button" class="filter-chip" data-transcript-action="download">다운로드</button>
  `;

  target.querySelectorAll("[data-transcript-action]").forEach((button) => {
    button.addEventListener("click", async () => {
      const action = button.dataset.transcriptAction;
      if (action === "copy") {
        await navigator.clipboard.writeText(transcriptText);
        button.textContent = "복사됨";
        window.setTimeout(() => {
          button.textContent = "복사";
        }, 1200);
        return;
      }

      const safeTitle = (sessionTitle || "session").replace(/[\\/:*?\"<>|]+/g, "_");
      const filename = `${safeTitle}-${transcriptMode}.txt`;
      const blob = new Blob([transcriptText], { type: "text/plain;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    });
  });
}

function renderSessionRecords() {
  renderSessionRecordFilters();
  const filteredRecords = (state.sessionPanelView?.dialogue || []).filter((record) => {
    if (state.sessionRecordFilter === "all") return true;
    return normalizeRecordRole(record) === state.sessionRecordFilter;
  });

  const target = document.getElementById("sessionPanelRecords");
  if (!target) return;

  if (!filteredRecords.length) {
    target.innerHTML = `<div class="list-item empty">기록이 없습니다.</div>`;
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

function renderSessionPanelContent() {
  renderSessionDetailTabs();
  const target = document.getElementById("sessionPanelContent");
  if (!target || !state.sessionPanelView) return;

  const view = state.sessionPanelView;
  const summary = view.summary || {};
  const quest = view.quest || {};
  const transcript = view.transcript || { available: false, content: "" };

  if (state.sessionDetailTab === "dialogue") {
    target.innerHTML = `
      <div class="detail-section">
        <strong>대화 기록</strong>
        <div id="sessionRecordFilter" class="filter-chip-row compact"></div>
        <div id="sessionPanelRecords" class="list session-record-list"></div>
      </div>
    `;
    renderSessionRecords();
    return;
  }

  if (state.sessionDetailTab === "transcript") {
    const transcriptMode = state.sessionTranscriptMode || "cleaned";
    const transcriptText = transcriptMode === "raw"
      ? (transcript.raw_content || "")
      : (transcript.cleaned_content || transcript.content || "");
    const transcriptModeLabel = transcriptMode === "raw" ? "원문" : "정리본";
    target.innerHTML = transcript.available
      ? `
        <div class="detail-section">
          <strong>원문 transcript</strong>
          <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:8px 0 12px;">
            <div id="sessionTranscriptModeTabs" class="filter-chip-row compact"></div>
            <div id="sessionTranscriptActions" class="filter-chip-row compact"></div>
          </div>
          <p class="muted" style="margin:0 0 8px;">현재 보기: ${escapeHtml(transcriptModeLabel)}${transcript.profile ? ` · profile: ${escapeHtml(transcript.profile)}` : ""}</p>
          <pre style="white-space:pre-wrap;max-height:420px;overflow:auto;">${escapeHtml(transcriptText)}</pre>
        </div>
      `
      : `<div class="detail-section"><strong>원문 transcript</strong><p class="muted">저장된 transcript가 없습니다.</p></div>`;
    renderTranscriptModeTabs(transcript);
    renderTranscriptActions(transcriptText, normalizeSessionTitle(view.header?.title, view.project_key) || view.session_id, transcriptModeLabel);
    return;
  }

  target.innerHTML = `
    <div class="detail-section" style="background:#fffbea;padding:12px;border-radius:8px;border-left:4px solid #f1c40f;margin:12px 0;">
      <strong>Intent</strong>
      <p class="muted">${escapeHtml(summary.intent || "요약이 없습니다.")}</p>
    </div>
    ${summary.actions?.length ? `
      <div class="detail-section">
        <strong>Actions</strong>
        <ul style="margin:8px 0;padding-left:20px;">
          ${summary.actions.map((line) => `<li style="margin:4px 0;">${escapeHtml(line)}</li>`).join("")}
        </ul>
      </div>
    ` : ""}
    ${summary.decisions?.length ? `
      <div class="detail-section">
        <strong>Decisions</strong>
        <ul style="margin:8px 0;padding-left:20px;">
          ${summary.decisions.map((line) => `<li style="margin:4px 0;">${escapeHtml(line)}</li>`).join("")}
        </ul>
      </div>
    ` : ""}
    ${summary.next_start?.length ? `
      <div class="detail-section" style="background:#e8f5e9;padding:12px;border-radius:8px;border-left:4px solid #27ae60;margin:12px 0;">
        <strong>Next Start</strong>
        <ul style="margin:8px 0;padding-left:20px;">
          ${summary.next_start.map((line) => `<li style="margin:4px 0;">${escapeHtml(line)}</li>`).join("")}
        </ul>
      </div>
    ` : ""}
    <div class="session-panel-highlight-grid">
      <div class="detail-section highlight-box">
        <strong>최근 퀘스트 보고</strong>
        <p class="muted">${escapeHtml(quest.report || "기록이 없습니다.")}</p>
      </div>
      <div class="detail-section highlight-box">
        <strong>최근 AI 판정</strong>
        <p class="muted">${escapeHtml(quest.verdict || "기록이 없습니다.")}</p>
      </div>
    </div>
  `;
}

async function openSessionDetailPanel(sessionId) {
  if (!sessionId) return;

  const [session, viewPayload] = await Promise.all([
    Promise.resolve(state.sessions.find((item) => item.id === sessionId)),
    fetchJson(`/api/sessions/view/${encodeURIComponent(sessionId)}?limit=500`)
  ]);

  if (!session) {
    console.warn(`Session not found: ${sessionId}`);
    return;
  }

  const view = viewPayload.view;
  const badges = {
    lengthColor: view.badges?.length_color || "#999",
    lengthBadge: view.badges?.length_badge || "short",
    valueColor: view.badges?.value_color || "#999",
    valueLabel: view.badges?.value_label || "비어있음",
  };
  const preview = view.summary?.intent || generateSessionPreview(session);
  const meta = [
    session.agent_name,
    session.model_name,
    session.project_key,
    formatRecentLabel(session.started_at),
  ].filter(Boolean).join(" / ");

  const detailHtml = `
    <div class="session-panel-body">
      <div style="margin-bottom:16px;padding:12px;background:#f8f9fa;border-radius:8px;">
        <div style="display:flex;gap:8px;margin-bottom:8px;">
          <span style="color:${badges.lengthColor};font-size:12px;padding:2px 8px;background:${badges.lengthColor}22;border-radius:4px;">${badges.lengthBadge}</span>
          <span style="color:${badges.valueColor};font-size:12px;padding:2px 8px;background:${badges.valueColor}22;border-radius:4px;">${badges.valueLabel}</span>
        </div>
        <span style="color:#555;font-size:13px;">${escapeHtml(preview)}</span>
      </div>

      <div class="detail-section">
        <strong>기본 정보</strong>
        <p class="muted">${escapeHtml(meta)}</p>
      </div>

      <div id="sessionDetailTabs" class="filter-chip-row compact"></div>
      <div id="sessionPanelContent"></div>
    </div>
  `;

  openDetailPanel("세션 상세", session.title || session.project_key || "세션", detailHtml);
  state.sessionPanelView = view;
  state.sessionDetailTab = "summary";
  state.sessionRecordFilter = "all";
  state.sessionTranscriptMode = "cleaned";
  renderSessionPanelContent();
}

function classifySession(session) {
  const title = (session.title || "").toLowerCase();
  const agent = (session.agent_name || "").toLowerCase();
  const summary = (session.summary_md || "").trim();

  // 1. Test sessions
  if (["test", "dev", "debug", "smoke", "meta", "dummy"].some(k => title.includes(k)) || agent === "tester") {
    return "test";
  }
  // 2. Simulated sessions
  if (["sim", "model", "mock"].some(k => title.includes(k))) {
    return "simulated";
  }
  // 3. Operational sessions
  if (session.has_quest_verdict || summary.length > 20) {
    return "operational";
  }
  return "unknown";
}

// Analyze session for badges (similar to generate_session_html.py)
function analyzeSessionForBadges(session) {
  const summary = session.summary_md || "";
  const contentLength = summary.length;
  
  // Length badge
  let lengthBadge = "short";
  let lengthColor = "#999";
  if (contentLength >= 1500) { lengthBadge = "medium"; lengthColor = "#f39c12"; }
  if (contentLength >= 2500) { lengthBadge = "long"; lengthColor = "#27ae60"; }
  
  // Value badge based on content keywords
  let valueBadge = "empty";
  let valueColor = "#e74c3c";
  let valueLabel = "비어있음";
  
  const lowerSummary = summary.toLowerCase();
  if (summary.includes("완료") || summary.includes("종료") || lowerSummary.includes("done") || lowerSummary.includes("complete") || lowerSummary.includes("ended")) {
    valueBadge = "decisions"; valueColor = "#27ae60"; valueLabel = "결정";
  } else if (summary.includes("다음") || lowerSummary.includes("next") || lowerSummary.includes("continue")) {
    valueBadge = "next-action"; valueColor = "#3498db"; valueLabel = "다음";
  } else if (summary.includes("-") || summary.includes("*")) {
    valueBadge = "actions"; valueColor = "#9b59b6"; valueLabel = "행동";
  } else if (contentLength > 30) {
    valueBadge = "transcript-only"; valueColor = "#f39c12"; valueLabel = "기록";
  }
  
  return { lengthBadge, lengthColor, valueBadge, valueColor, valueLabel };
}

function normalizeSessionLengthLabel(value) {
  const key = String(value || "").trim().toLowerCase();
  if (key === "short") return "짧음";
  if (key === "medium") return "중간";
  if (key === "long") return "길음";
  return value || "";
}

function normalizeSessionTitle(value, projectKey) {
  const raw = String(value || "").trim();
  const normalized = raw.toLowerCase();
  if (!raw) return projectKey || "세션";
  if (normalized === "0-a-control new session") return "0-a-control 기본 세션";
  if (normalized === "0-a-control new opencode session") return "0-a-control OpenCode 세션";
  if (normalized === "0-a-control new codex session") return "0-a-control Codex 세션";
  if (normalized === "0-a-control new gemini-cli session") return "0-a-control Gemini CLI 세션";
  if (normalized === "0-a-control new kilo session") return "0-a-control Kilo 세션";
  return raw;
}

// Generate 1-line preview from summary
function generateSessionPreview(session) {
  const summary = session.summary_md || "";
  if (!summary) return "세션 요약 없음";
  
  // Get first meaningful line
  const lines = summary.split("\n").filter(l => l.trim());
  if (lines.length === 0) return "세션 요약 없음";
  
  // Return first line, truncated
  return lines[0].substring(0, 80) + (lines[0].length > 80 ? "..." : "");
}

function renderSessions() {
  const targetId = 'recentSessionList';
  const parentPanel = document.getElementById(targetId)?.parentElement;
  if (!parentPanel) return;

  // Hide agent filter for now - can be enabled later if needed
  const filterContainer = document.getElementById("sessionAgentFilter");
  if (filterContainer) filterContainer.style.display = "none";
  
  // Apply agent filter (still used for detail view)
  const allFilteredSessions = state.sessions.filter((item) => {
    if (!visibleSessionAgents.has(item.agent_name)) return false;
    if (state.sessionAgentFilter === "all") return true;
    return item.agent_name === state.sessionAgentFilter;
  });

  // Sort by time
  const sortedSessions = [...allFilteredSessions].sort((a, b) => {
    const aTime = new Date(a.ended_at || a.started_at || 0).getTime();
    const bTime = new Date(b.ended_at || b.started_at || 0).getTime();
    return bTime - aTime;
  });

  // RECENT PANEL: Only show 3 most recent items (compressed view)
  const recentItems = sortedSessions.slice(0, 3);
  
  const renderRecentCard = (item) => {
    const badges = analyzeSessionForBadges(item);
    const preview = generateSessionPreview(item);
    const time = formatRecentLabel(item.ended_at || item.started_at);
    const title = normalizeSessionTitle(item.title, item.project_key);
    
    return `
      <div class="list-item session-link" data-session-id="${escapeHtml(item.id)}" onclick="openSessionDetailPanel('${item.id}')">
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:4px;">
          <strong style="font-size:13px;">${escapeHtml(title.substring(0, 30))}</strong>
          <span style="color:${badges.lengthColor};font-size:10px;">${normalizeSessionLengthLabel(badges.lengthBadge)}</span>
          <span style="color:${badges.valueColor};font-size:10px;">${badges.valueLabel}</span>
        </div>
        <span style="color:#777;font-size:11px;">${escapeHtml(preview)}</span>
        <span style="color:#999;font-size:10px;display:block;margin-top:2px;">${escapeHtml(item.agent_name)} · ${time}</span>
      </div>
    `;
  };

  // Render compressed recent panel
  document.getElementById(targetId).innerHTML = recentItems.map(renderRecentCard).join("");
  
  // Update count badge
  setCountBadge("recentSessionCount", sortedSessions.length);
  
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
}



