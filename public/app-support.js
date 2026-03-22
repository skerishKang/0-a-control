/**
 * Support Grid rendering module
 */

function normalizeProjectLabel(value) {
  const raw = String(value || "").trim();
  if (!raw) return "unknown";
  return raw
    .replace(/^ipu-security$/i, "24-1-ipu-ai-firewall")
    .replace(/^\[?ipu-security\]?/i, "24-1")
    .replace(/IPU AI Security Filter/gi, "IPU AI Firewall")
    .trim();
}

function renderSupportGrid(state) {
  renderTodaySummarySection(state);
  renderUnfinishedPlansSection(state);
  renderPlansSection(state);
  renderSessionsSection(state);
  renderBriefsSection(state);
  renderExternalInboxSection(state);
  renderAgentStatusSection(state);
  renderWorkdiarySection(state);
  renderPriorityCandidatesSection(state);
  renderExternalContextPanel(state);
  renderDerivedSuggestionsSection().catch(() => {});
}

function labelAgentStatus(status) {
  return {
    working: "작업 중",
    idle: "대기",
    stale: "정리 필요",
    error: "오류",
    unavailable: "미설치",
  }[status] || status || "";
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

function normalizeSuggestionTitle(value) {
  return String(value || "")
    .replace(/IPU AI Security Filter/gi, "IPU AI Firewall")
    .replace(/security-filter/gi, "firewall")
    .trim();
}

function normalizeDayPhaseLabel(value) {
  return {
    "in-progress": "진행 중",
    morning: "아침 정리",
    midday: "진행 중",
    end_of_day: "마감 정리",
  }[String(value || "").trim()] || value || "미정";
}

function normalizeBriefContent(value) {
  return String(value || "")
    .replace(/\bNone\b/g, "없음")
    .replace(/\s+-\s+/g, "\n- ");
}

function normalizeBriefTypeLabel(value) {
  const key = String(value || "").trim().toLowerCase();
  if (!key || key === "brief") return "브리프";
  if (key === "morning_auto") return "자동 아침";
  if (key === "morning") return "아침";
  if (key === "evening") return "저녁";
  return value || "브리프";
}

function normalizeItemTypeLabel(value) {
  const key = String(value || "").trim().toLowerCase();
  if (!key || key === "item") return "항목";
  if (key === "file") return "파일";
  if (key === "folder") return "폴더";
  if (key === "project") return "프로젝트";
  return value || "항목";
}

function normalizeExternalStatusLabel(value) {
  const key = String(value || "").trim().toLowerCase();
  if (!key || key === "new") return "새 항목";
  if (key === "reviewing") return "검토중";
  if (key === "saved") return "저장됨";
  if (key === "archived") return "보관됨";
  return labelStatus(value) || value || "";
}

function normalizeSessionTitleLabel(value) {
  const raw = String(value || "").trim();
  const normalized = raw.toLowerCase();
  if (!raw) return "세션 정보 없음";
  if (normalized === "0-a-control new session") return "0-a-control 기본 세션";
  if (normalized === "0-a-control new opencode session") return "0-a-control OpenCode 세션";
  if (normalized === "0-a-control new codex session") return "0-a-control Codex 세션";
  if (normalized === "0-a-control new gemini-cli session") return "0-a-control Gemini CLI 세션";
  if (normalized === "0-a-control new kilo session") return "0-a-control Kilo 세션";
  return raw;
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

function renderTodaySummarySection(state) {
  const targetId = "todaySummaryList";
  const container = document.getElementById(targetId);
  if (!container) return;
  const parentPanel = container.parentElement;
  if (parentPanel) parentPanel.classList.add("panel-browsing");

  const current = state.currentState || {};
  const progress = current.day_progress_summary || {};
  const verdict = current.recent_verdict || {};
  const datedPressure = current.dated_pressure_summary || [];
  const recommendedNext = current.recommended_next_quest || "";
  const dayPhase = current.day_phase || "";
  const todayDone = current.today_done_quests || [];
  const tomorrowFirst = current.tomorrow_first_quest || null;
  const confirmedStart = current.confirmed_starting_point || null;

  const items = [];
  const done = progress.done || 0;
  const partial = progress.partial || 0;

  // end-of-day 마감 처리 권장 신호
  if (dayPhase === "end-of-day") {
    items.push({ label: "마감", value: "정리 권장", type: "closing" });
  }

  if (done > 0) items.push({ label: "완료", value: `${done}건`, type: "done" });
  if (partial > 0) items.push({ label: "부분", value: `${partial}건`, type: "partial" });

  const questStatus = verdict.status || "none";
  if (questStatus === "done") {
    items.push({ label: "최근 판정", value: "완료", type: "done" });
  } else if (questStatus === "partial") {
    items.push({ label: "최근 판정", value: "부분", type: "partial" });
  } else if (questStatus === "hold") {
    items.push({ label: "최근 판정", value: "보류", type: "hold" });
  }

  if (datedPressure.length > 0) {
    const urgent = datedPressure[0];
    items.push({ label: "주의", value: urgent.title?.slice(0, 20) || "항목 없음", type: "risk" });
  }

  if (recommendedNext) {
    const short = recommendedNext.length > 25 ? `${recommendedNext.slice(0, 25)}...` : recommendedNext;
    items.push({ label: "다음", value: short, type: "action" });
  }

  if (tomorrowFirst && tomorrowFirst.title) {
    const short = tomorrowFirst.title.length > 20 ? `${tomorrowFirst.title.slice(0, 20)}...` : tomorrowFirst.title;
    items.push({ label: "내일 첫 퀘스트", value: short, type: "suggestion" });
  }

  if (items.length === 0) {
    container.innerHTML = `<div class="list-item empty">오늘 판단 요약이 아직 없습니다.</div>`;
  } else {
    container.innerHTML = items.slice(0, 4).map(item => `
      <div class="list-item summary-item">
        <span class="summary-label">${escapeHtml(item.label)}</span>
        <span class="summary-value ${item.type}">${escapeHtml(item.value)}</span>
      </div>
    `).join("");
  }

  if (parentPanel) {
    parentPanel.onclick = () => {
      const detailItems = [
        {
          title: "오늘 진행 요약",
          detail: `완료 ${done}건 / 부분 ${partial}건`,
        },
        {
          title: "최근 판정 상태",
          detail: verdict.status ? labelStatus(verdict.status) : "판정 없음",
        },
        {
          title: "추천 다음 행동",
          detail: recommendedNext || "추천 없음",
        },
        {
          title: "오늘 단계",
          detail: normalizeDayPhaseLabel(dayPhase),
        },
      ];

      // 오늘 완료된 quest 목록
      if (todayDone.length > 0) {
        detailItems.push({
          title: "--- 오늘 완료된 퀘스트 ---",
          detail: `${todayDone.length}건`,
        });
        todayDone.forEach((q) => {
          detailItems.push({
            title: `✓ ${q.title || "제목 없음"}`,
            detail: q.verdict_reason || q.updated_at || "",
          });
        });
      }

      // end-of-day 마감 권장 메시지
      if (dayPhase === "end-of-day") {
        detailItems.push({
          title: "🌙 마감 처리 권장",
          detail: "오늘 작업을 정리하고 미완료 항목의 재시작 전략을 정하세요. 미완료를 hold로 남기거나 단기 플랜으로 넘길 수 있습니다.",
        });
      }

      // 내일 첫 퀘스트 제안
      if (tomorrowFirst && tomorrowFirst.title) {
        const sourceLabel = tomorrowFirst.source === "today_hold" ? "오늘 미완료 → 계속" : "단기 플랜 → 이동";
        detailItems.push({
          title: `🌅 내일 첫 퀘스트`,
          detail: `<strong>${escapeHtml(tomorrowFirst.title)}</strong><br><span class="muted">${escapeHtml(tomorrowFirst.reason || "")} (${sourceLabel})</span>`,
        });
      }

      // confirmed_starting_point: 사용자가 확정한 내일 첫 퀘스트 (아직 자동 연동)
      if (confirmedStart && confirmedStart.title) {
        const isPromotable = !current.current_quest_id;
        const actionHtml = isPromotable
          ? `<div style="margin-top:8px;"><button type="button" class="primary-btn" onclick="promoteStartingPoint()">이 약속으로 작업 시작</button></div>`
          : `<div style="margin-top:8px;"><button type="button" class="primary-btn" disabled title="이미 진행 중인 퀘스트가 있습니다">이 약속으로 작업 시작 (진행 중인 퀘스트 있음)</button></div>`;

        detailItems.push({
          title: `✅ 내일 첫 퀘스트 (확인됨)`,
          detail: `<strong>${escapeHtml(confirmedStart.title)}</strong><br><span class="muted">${escapeHtml(confirmedStart.reason || "")} · ${confirmedStart.confirmed_at || ""}</span>${actionHtml}`,
        });
      }

      // dated pressure
      datedPressure.slice(0, 5).forEach((item) => {
        detailItems.push({
          title: `주의 일정: ${item.title || "항목 없음"}`,
          detail: item.due_at || item.why_now || "세부 정보 없음",
        });
      });

      showDetailedList("오늘 운영 요약", "오늘 상태를 요약한 상세 보기", detailItems, (i) => `
        <div class='list-item'>
          <strong>${escapeHtml(i.title)}</strong>
          <p class='muted'>${escapeHtml(i.detail || "-")}</p>
        </div>
      `);
    };
  }
}

function renderUnfinishedPlansSection(state) {
  const targetId = "unfinishedPlanList";
  const container = document.getElementById(targetId);
  if (!container) return;

  const plans = state.plans || [];
  const unfinished = plans.filter(p => p.status && !["done", "rejected", "archived"].includes(p.status));
  const count = unfinished.length;

  const countEl = document.getElementById("unfinishedPlanCount");
  if (countEl) countEl.textContent = String(count);

  if (count === 0) {
    container.innerHTML = `<div class="list-item empty">미완료 플랜이 없습니다.</div>`;
    return;
  }

  const topItems = unfinished.slice(0, 4);
  container.innerHTML = topItems.map(plan => `
    <div class="list-item">
      <div class="candidate-head">
        <strong>${escapeHtml(plan.title)}</strong>
        <span class="session-badge verdict ${escapeHtml(plan.status || "pending")}">${escapeHtml(labelStatus(plan.status))}</span>
      </div>
      <span class="candidate-reason">${escapeHtml(plan.due_at || labelBucket(plan.bucket) || "-")}</span>
    </div>
  `).join("");
}

const externalContextStatusOptions = [
  { value: "new", label: "새 항목" },
  { value: "reviewing", label: "검토중" },
  { value: "saved", label: "저장됨" },
];

const externalContextSourceOptions = [
  { value: "all", label: "전체" },
  { value: "core", label: "핵심4개" },
  { value: "stock", label: "주식큐레이터" },
  { value: "news", label: "뉴스" },
  { value: "general", label: "일반대화" },
];

function externalContextMatchesStatus(item, status) {
  if (status === "saved") {
    return ["accepted", "archived"].includes(item.status);
  }
  return item.status === status;
}

function externalContextMatchesSource(item, source) {
  if (source === "all") return true;
  if (source === "core") return ["self_chat", "kang_hyerim_chat", "kilo_chat", "local_chat"].includes(item.chat_class);
  if (source === "stock") return item.chat_class === "stock_curator_channel";
  if (source === "news") return item.chat_class === "news_channel";
  if (source === "general") return item.chat_class === "general_chat" || !item.chat_class;
  return true;
}

function getExternalContextItemsForActiveStatus() {
  const panelItems = state.externalInboxPanel?.items || [];
  if (panelItems.length > 0) {
    return panelItems;
  }

  const globalItems = state.externalInbox?.items || [];
  return globalItems.filter((item) =>
    externalContextMatchesStatus(item, state.externalContextStatus)
  );
}

function getFilteredExternalContextItems() {
  const items = getExternalContextItemsForActiveStatus();
  return items.filter((item) =>
    externalContextMatchesSource(item, state.externalContextSource)
  );
}

function getExternalContextListEntries(items) {
  const grouped = new Map();

  items.forEach((item) => {
    const key = `${item.source_id || item.source_name || "unknown"}::${item.chat_class || ""}`;
    const existing = grouped.get(key);
    const ts = getInboxDisplayTimestamp(item);
    if (!existing) {
      grouped.set(key, {
        key,
        item,
        count: 1,
        latestTimestamp: ts,
      });
      return;
    }

    existing.count += 1;
    const existingTs = existing.latestTimestamp || "";
    if ((ts || "") > existingTs) {
      existing.item = item;
      existing.latestTimestamp = ts;
    }
  });

  return Array.from(grouped.values()).sort((a, b) =>
    String(b.latestTimestamp || "").localeCompare(String(a.latestTimestamp || ""))
  );
}

function renderExternalContextTabs(containerId, options, activeValue, counts = {}, onClick) {
  const target = document.getElementById(containerId);
  if (!target) return;
  target.innerHTML = options.map((option) => {
    const count = counts[option.value];
    const countLabel = (count !== undefined) ? ` <span class="chip-count">${count}</span>` : "";
    return `
      <button
        type="button"
        class="filter-chip ${option.value === activeValue ? "active" : ""}"
        data-value="${escapeHtml(option.value)}"
      >
        ${escapeHtml(option.label)}${countLabel}
      </button>
    `;
  }).join("");
  target.querySelectorAll(".filter-chip").forEach((button) => {
    button.onclick = () => onClick(button.dataset.value);
  });
}

function renderExternalContextDetail(item) {
  const target = document.getElementById("externalContextDetail");
  if (!target) return;
  if (!item) {
    target.innerHTML = `<div class="empty-state">왼쪽에서 채팅을 고르면 오늘 대화 전체를 여기서 볼 수 있습니다.</div>`;
    return;
  }

  const thread = state.externalContextThread;
  const sourceLabel = item.source_name || item.source_id || item.source_type || "source";
  const category = item.category || "기타";
  const messages = thread?.source_id === item.source_id ? (thread.messages || []) : [];
  const loadedDays = thread?.source_id === item.source_id ? (thread.loaded_days || []) : [];
  const isLoadingOlder = Boolean(thread?.source_id === item.source_id && thread?.loadingOlder);
  const canLoadOlder = Boolean(thread?.source_id === item.source_id && thread?.has_more_before && thread?.previous_day);

  if (!messages.length) {
    target.innerHTML = `
      <div class="detail-view-content">
        <div class="conversation-panel-header">
          <h4>${escapeHtml(sourceLabel)}</h4>
          <div class="detail-meta-row">
            <span class="meta-chip source">${escapeHtml(sourceLabel)}</span>
            <span class="meta-chip category">${escapeHtml(category)}</span>
          </div>
        </div>
        ${
          canLoadOlder
            ? `<button type="button" class="secondary-btn compact load-older-btn" id="loadOlderMessagesBtn">이전 날짜 불러오기</button>`
            : ""
        }
        <div class="empty-state">오늘 저장된 메시지가 아직 없거나, 오늘 대화를 불러오는 중입니다.</div>
      </div>
    `;
    attachExternalContextThreadInteractions();
    return;
  }

  const dayGroups = new Map();
  messages.forEach((message) => {
    const dayKey = message.display_day || (message.display_timestamp || message.item_timestamp || message.imported_at || "").slice(0, 10) || "unknown";
    const bucket = dayGroups.get(dayKey) || [];
    bucket.push(message);
    dayGroups.set(dayKey, bucket);
  });

  const transcript = Array.from(dayGroups.entries()).map(([dayKey, dayMessages]) => {
    const rows = dayMessages.map((message) => {
      const who = message.author || "Unknown";
      const when = formatConversationTime(message.display_timestamp || message.item_timestamp || message.imported_at || "");
      const attachment = message.attachment_path
        ? `<span class="attachment-pill" title="${escapeHtml(message.attachment_path)}">첨부 있음</span>`
        : (message.item_type && message.item_type !== "text")
          ? `<span class="attachment-pill">${escapeHtml(message.item_type)}</span>`
          : "";
      return `
        <div class="conversation-row">
          <div class="conversation-meta">
            <span class="conversation-time">${escapeHtml(when)}</span>
            <strong>${escapeHtml(who)}</strong>
            ${attachment}
          </div>
          <div class="conversation-body">${escapeHtml(message.raw_content || "(빈 메시지)")}</div>
        </div>
      `;
    }).join("");

    return `
      <section class="conversation-day-block" data-day="${escapeHtml(dayKey)}">
        <div class="conversation-day-divider"><span>${escapeHtml(dayKey)}</span></div>
        <div class="conversation-day-messages">${rows}</div>
      </section>
    `;
  }).join("");

  target.innerHTML = `
    <div class="detail-view-content">
      <div class="conversation-panel-header">
        <h4>${escapeHtml(sourceLabel)}</h4>
        <div class="detail-meta-row">
          <span class="meta-chip source">${escapeHtml(sourceLabel)}</span>
          <span class="meta-chip category">${escapeHtml(category)}</span>
          <span class="meta-chip">오늘 기본 · ${escapeHtml(String(messages.length))}건</span>
          <span class="meta-chip">${escapeHtml(String(loadedDays.length))}일 로드</span>
        </div>
      </div>
      ${
        canLoadOlder
          ? `<div class="conversation-load-row"><button type="button" class="secondary-btn compact load-older-btn" id="loadOlderMessagesBtn">${isLoadingOlder ? "불러오는 중..." : "이전 날짜 불러오기"}</button></div>`
          : ""
      }
      <div class="conversation-thread">${transcript}</div>
    </div>
  `;
  attachExternalContextThreadInteractions();
}

function formatConversationTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return formatRecentLabel(value);
  const hh = String(date.getHours()).padStart(2, "0");
  const mm = String(date.getMinutes()).padStart(2, "0");
  return `${hh}:${mm}`;
}

function attachExternalContextThreadInteractions() {
  const target = document.getElementById("externalContextDetail");
  if (!target) return;

  const button = document.getElementById("loadOlderMessagesBtn");
  if (button) {
    const loading = Boolean(state.externalContextThread?.loadingOlder);
    button.disabled = loading;
    button.onclick = () => {
      if (!loading && window.loadOlderExternalContextDay) {
        window.loadOlderExternalContextDay();
      }
    };
  }

  target.onscroll = () => {
    if (target.scrollTop > 24) return;
    if (!state.externalContextThread?.has_more_before || state.externalContextThread?.loadingOlder) return;
    if (window.loadOlderExternalContextDay) {
      window.loadOlderExternalContextDay();
    }
  };
}

function getTelegramConnectionState() {
  const telegramStatus = state.telegramStatus || {};
  const missingConfig = Array.isArray(telegramStatus.missing_config) ? telegramStatus.missing_config : [];
  const hasUsableSession = Boolean(
    telegramStatus.configured &&
    telegramStatus.session_exists &&
    !telegramStatus.auth_required &&
    (telegramStatus.user || telegramStatus.last_seen || telegramStatus.session_path)
  );
  if (!telegramStatus.configured) {
    return {
      code: "unconfigured",
      label: "미설정",
      summary: "Telegram 내부 서비스 설정이 아직 없습니다.",
      detail: missingConfig.length
        ? `${missingConfig.join(", ")} 값을 먼저 설정해야 합니다.`
        : "TELEGRAM_API_ID / TELEGRAM_API_HASH와 핵심 소스 설정이 필요합니다.",
      tone: "warning",
    };
  }
  if (!hasUsableSession) {
    return {
      code: "auth",
      label: "인증 필요",
      summary: "Telegram 로그인 세션 확인이 필요합니다.",
      detail: telegramStatus.session_exists
        ? `세션이 끊겼거나 인증이 만료되었습니다. 세션 파일: ${telegramStatus.session_path || "-"}`
        : `세션 파일이 아직 없습니다. 첫 연결이 성공하면 ${telegramStatus.session_path || "-"} 에 생성됩니다.`,
      tone: "warning",
    };
  }
  const userLabel = telegramStatus.user?.username || telegramStatus.user?.first_name || "사용자";
  return {
    code: "connected",
    label: "연결됨",
    summary: `Telegram 내부 서비스가 ${userLabel} 계정으로 연결되어 있습니다.`,
    detail: telegramStatus.last_seen
      ? `마지막 확인 ${formatRecentLabel(telegramStatus.last_seen)}`
      : "인증 세션과 핵심 소스가 준비되어 있습니다.",
    tone: "success",
  };
}

function deriveTelegramFailureMessage(lastRun, sources) {
  const telegramStatus = state.telegramStatus || {};
  const missingConfig = Array.isArray(telegramStatus.missing_config) ? telegramStatus.missing_config : [];
  const hasUsableSession = Boolean(
    telegramStatus.configured &&
    telegramStatus.session_exists &&
    !telegramStatus.auth_required &&
    (telegramStatus.user || telegramStatus.last_seen || telegramStatus.session_path)
  );
  if (!telegramStatus.configured) {
    return {
      title: "동기화에 실패했습니다. Telegram 설정이 아직 없습니다.",
      detail: missingConfig.length
        ? `${missingConfig.join(", ")} 를 설정하고 서버를 다시 확인하세요.`
        : "TELEGRAM_API_ID / TELEGRAM_API_HASH를 설정하고 서버를 다시 확인하세요.",
    };
  }
  if (!sources.length) {
    return {
      title: "동기화할 핵심 소스가 없습니다.",
      detail: "telegram_sources에서 core 소스를 지정해야 sync-core가 동작합니다.",
    };
  }
  if (!hasUsableSession) {
    return {
      title: "동기화에 실패했습니다. Telegram 인증 세션이 필요합니다.",
      detail: "로그인 세션을 다시 연결한 뒤 sync-core를 다시 실행하세요.",
    };
  }
  return {
    title: "동기화에 실패했습니다. Telegram 응답을 확인해야 합니다.",
    detail: lastRun?.error ? `상세: ${lastRun.error}` : "일시적 오류일 수 있으니 잠시 후 다시 시도하세요.",
  };
}

function renderTelegramSetupHint(connectionState, sources) {
  const target = document.getElementById("telegramSetupHint");
  if (!target) return;
  const telegramStatus = state.telegramStatus || {};

  let hint = "동기화 전 준비: Telegram API ID/API HASH 설정, 로그인 세션 생성, 핵심 소스 지정이 필요합니다.";
  if (connectionState.code === "auth") {
    hint = `동기화 전 준비: ${connectionState.detail}`;
  } else if (connectionState.code === "connected") {
    hint = sources.length
      ? "동기화 전 준비 완료: 연결된 세션으로 핵심 소스만 가져옵니다."
      : "연결은 되어 있지만 sync-core용 핵심 소스 지정이 아직 없습니다.";
  } else if (telegramStatus.setup_message) {
    hint = `동기화 전 준비: ${telegramStatus.setup_message}`;
  }

  target.textContent = hint;
  target.className = `telegram-setup-hint ${connectionState.tone}`;
}

function renderTelegramSyncStatus() {
  const banner = document.getElementById("syncStatusBanner");
  const sourceStatus = document.getElementById("telegramSourceStatus");
  if (!banner) return;

  const sources = state.telegramSyncStatus?.sources || [];
  const telegramStatus = state.telegramStatus || {};
  const lastRun = state.lastTelegramSyncRun || null;
  const connectionState = getTelegramConnectionState();
  renderTelegramSetupHint(connectionState, sources);

  const lastRunDetails = Array.isArray(lastRun?.details) ? lastRun.details : [];
  const sourceDetailMap = new Map(lastRunDetails.map((detail) => [String(detail.source_id), detail]));
  if (sourceStatus) {
    sourceStatus.innerHTML = sources.map((source) => {
      const detail = sourceDetailMap.get(String(source.source_id));
      const hasError = Boolean(detail?.error) || /No module named 'telethon'/.test(String(telegramStatus.error || ""));
      const hasHistory = Boolean(source.last_synced_at) && !hasError;
      const label = hasError ? "실패" : hasHistory ? "연결됨" : "미수집";
      const klass = hasError ? "warning" : hasHistory ? "success" : "muted";
      const countLabel = Number(source.new_count || 0) > 0 ? ` · 새 ${Number(source.new_count || 0)}건` : "";
      const title = hasError
        ? detail.error
        : hasHistory
          ? `${source.source_name} · 마지막 ${formatRecentLabel(source.last_synced_at)}`
          : `${source.source_name} · 아직 동기화 이력 없음`;
      return `
        <div class="telegram-source-pill ${klass}" title="${escapeHtml(title)}">
          <strong>${escapeHtml(source.source_name || source.source_id)}</strong>
          <span>${escapeHtml(label)}${escapeHtml(countLabel)}</span>
        </div>
      `;
    }).join("");
  }

  if (state.telegramSyncRunning) {
    banner.innerHTML = `
      <span class="sync-status-text"><span class="telegram-status-chip ${connectionState.tone}">${escapeHtml(connectionState.label)}</span>핵심 소스를 확인하며 동기화를 실행하고 있습니다.</span>
      <span class="sync-status-time">Telegram 메시지를 직접 불러오는 중</span>
    `;
    banner.className = "sync-status-banner info";
    return;
  }

  if (!sources.length) {
    const setupHint = lastRun?.error
      ? deriveTelegramFailureMessage(lastRun, sources).detail
      : (telegramStatus.setup_message || connectionState.detail);
    banner.innerHTML = `
      <span class="sync-status-text"><span class="telegram-status-chip ${connectionState.tone}">${escapeHtml(connectionState.label)}</span>${escapeHtml(connectionState.summary)}</span>
      <span class="sync-status-time">${escapeHtml(setupHint)}</span>
    `;
    banner.className = "sync-status-banner warning";
    return;
  }

  const coreCount = sources.length;
  const syncedCount = sources.filter((s) => s.last_synced_at).length;
  const queuedNewCount = sources.reduce((sum, source) => sum + Number(source.new_count || 0), 0);
  const reviewingCount = sources.reduce((sum, source) => sum + Number(source.reviewing_count || 0), 0);
  let latestSync = null;
  sources.forEach((s) => {
    if (s.last_synced_at) {
      const d = new Date(s.last_synced_at);
      if (!latestSync || d > latestSync) latestSync = d;
    }
  });

  const timeLabel = latestSync ? formatRecentLabel(latestSync.toISOString()) : "이력 없음";
  const statusClass = lastRun && !lastRun.ok ? "warning" : "info";

  if (lastRun) {
    if (lastRun.ok) {
      const details = Array.isArray(lastRun.details) ? lastRun.details : [];
      const successCount = details.filter((detail) => !detail.error).length || syncedCount;
      const failedCount = details.filter((detail) => detail.error).length;
      const importedCount = Number(lastRun.synced_count || 0);

      banner.innerHTML = `
        <span class="sync-status-text"><span class="telegram-status-chip ${connectionState.tone}">${escapeHtml(connectionState.label)}</span>마지막 동기화 ${formatRecentLabel(lastRun.executed_at || latestSync?.toISOString() || "")} · 새 메시지 ${importedCount}건 반영</span>
        <span class="sync-status-time">핵심 ${coreCount}개 중 ${successCount}개 성공${failedCount ? ` / ${failedCount}개 실패` : ""} · 검토중 ${reviewingCount}건 보관</span>
      `;
      banner.className = "sync-status-banner success";
      return;
    }

    const failure = deriveTelegramFailureMessage(lastRun, sources);
    banner.innerHTML = `
      <span class="sync-status-text"><span class="telegram-status-chip ${connectionState.tone}">${escapeHtml(connectionState.label)}</span>${escapeHtml(failure.title)}</span>
      <span class="sync-status-time">마지막 시도 ${formatRecentLabel(lastRun.failed_at || "")} · ${escapeHtml(failure.detail)}</span>
    `;
    banner.className = "sync-status-banner warning";
    return;
  }

  banner.innerHTML = `
    <span class="sync-status-text"><span class="telegram-status-chip ${connectionState.tone}">${escapeHtml(connectionState.label)}</span>마지막 동기화 ${timeLabel} · 새 항목 ${queuedNewCount}건 대기</span>
    <span class="sync-status-time">핵심 ${coreCount}개 중 ${syncedCount}개 이력 있음 · 검토중 ${reviewingCount}건 보관</span>
  `;
  banner.className = `sync-status-banner ${statusClass}`;
}

function renderExternalContextPanel(state) {
  renderTelegramSyncStatus();
  const payload = state.externalInbox || {};
  const allItems = payload.items || [];
  const summary = payload.summary || {};
  const activeStatusItems = getExternalContextItemsForActiveStatus();

  // 1. Calculate counts for filter chips
  const statusCounts = {
    new: summary.new || 0,
    reviewing: summary.reviewing || 0,
    saved: (summary.accepted || 0) + (summary.archived || 0),
  };

  const sourceCounts = {
    all: activeStatusItems.length,
    core: activeStatusItems.filter(i => ["self_chat", "kang_hyerim_chat", "kilo_chat", "local_chat"].includes(i.chat_class)).length,
    stock: activeStatusItems.filter(i => i.chat_class === "stock_curator_channel").length,
    news: activeStatusItems.filter(i => i.chat_class === "news_channel").length,
    general: activeStatusItems.filter(i => i.chat_class === "general_chat" || !i.chat_class).length,
  };

  // 2. Render filter tabs with counts
  renderExternalContextTabs("externalContextStatusTabs", externalContextStatusOptions, state.externalContextStatus, statusCounts, (value) => {
    state.externalContextStatus = value;
    if (window.refreshExternalContextPanelData) {
      window.refreshExternalContextPanelData();
    } else {
      renderExternalContextPanel(state);
    }
  });
  renderExternalContextTabs("externalContextSourceTabs", externalContextSourceOptions, state.externalContextSource, sourceCounts, (value) => {
    state.externalContextSource = value;
    if (window.refreshExternalContextPanelData) {
      window.refreshExternalContextPanelData();
    } else {
      renderExternalContextPanel(state);
    }
  });

  const target = document.getElementById("externalContextList");
  const countTarget = document.getElementById("externalContextPanelCount");
  if (!target || !countTarget) return;

  // 3. Filter items and update list count badge
  const items = getFilteredExternalContextItems();
  const entries = getExternalContextListEntries(items);
  countTarget.textContent = `${entries.length}개`;

  // 4. Handle selection state
  if (!state.externalContextSelectedId || !entries.some((entry) => String(entry.item.id) === String(state.externalContextSelectedId))) {
    state.externalContextSelectedId = entries[0]?.item.id || null;
  }

  // 5. Render list or empty state
  if (!entries.length) {
    const activeStatus = externalContextStatusOptions.find((option) => option.value === state.externalContextStatus)?.label || "현재 상태";
    const activeSource = externalContextSourceOptions.find((option) => option.value === state.externalContextSource)?.label || "전체";
    target.innerHTML = `<div class="list-item empty">${activeStatus} · ${activeSource} 조건에 맞는 항목이 아직 없습니다.</div>`;
    renderExternalContextDetail(null);
    return;
  }

  target.innerHTML = entries.map(({ item, count }) => {
    const isActive = String(item.id) === String(state.externalContextSelectedId);
    const sourceLabel = item.source_name || item.source_id || item.source_type || "source";
    const timeLabel = formatRecentLabel(getInboxDisplayTimestamp(item));
    
    return `
      <div class="list-item candidate-item external-context-list-item ${isActive ? "active" : ""}" data-id="${escapeHtml(String(item.id))}">
        <div class="external-context-inline-row">
          <strong>${escapeHtml(sourceLabel)}</strong>
          <span class="count-badge source-count-badge">${escapeHtml(String(count))}</span>
          <span class="source-tag inline">${escapeHtml(item.category || "기타")}</span>
          <span class="time-tag">${escapeHtml(timeLabel)}</span>
        </div>
      </div>
    `;
  }).join("");

  // 6. Attach click events to list items
  target.querySelectorAll(".external-context-list-item").forEach((node) => {
    node.onclick = () => {
      state.externalContextSelectedId = node.dataset.id;
      const selectedItem = entries.map((entry) => entry.item).find((item) => String(item.id) === String(state.externalContextSelectedId));
      state.externalContextThread = null;
      renderExternalContextDetail(selectedItem || null);
      if (selectedItem && window.refreshExternalContextThread) {
        window.refreshExternalContextThread(selectedItem.source_id);
      }
      target.querySelectorAll(".external-context-list-item").forEach(n => n.classList.toggle("active", n.dataset.id === node.dataset.id));
    };
  });

  // 7. Render detail view for initially selected item
  const selectedItem = entries.map((entry) => entry.item).find((item) => String(item.id) === String(state.externalContextSelectedId)) || null;
  renderExternalContextDetail(selectedItem);
  if (selectedItem && (!state.externalContextThread || state.externalContextThread.source_id !== selectedItem.source_id) && window.refreshExternalContextThread) {
    window.refreshExternalContextThread(selectedItem.source_id);
  }
}

function renderExternalInboxSection(state) {
  const targetId = "externalInboxList";
  const parentPanel = document.getElementById(targetId)?.parentElement;
  if (!parentPanel) return;
  parentPanel.classList.add("panel-browsing");

  const payload = state.externalInbox || {};
  const items = payload.items || [];
  const summary = payload.summary || {};
  const actionableCount = (summary.new || 0) + (summary.reviewing || 0);
  setCountBadge("externalInboxCount", actionableCount || summary.total || 0);

  const formatter = (item) => {
    const title = item.title || item.raw_content || "외부 입력";
    const source = item.source_name || item.source_id || item.source_type || "source";
    const preview = (item.raw_content || "").slice(0, 80);
    return `
      <div class="list-item candidate-item">
        <div class="candidate-head">
          <strong>${escapeHtml(title)}</strong>
          <span class="session-badge verdict ${escapeHtml(item.status || "new")}">${escapeHtml(normalizeExternalStatusLabel(item.status))}</span>
        </div>
        <span class="candidate-reason">${escapeHtml(source)} · ${escapeHtml(preview || "-")}</span>
      </div>
    `;
  };

  renderCappedList(
    targetId,
    items,
    formatter,
    3,
    "새로 검토할 항목이 없습니다. 텔레그램/이메일을 동기화하면 여기에 표시됩니다."
  );

  parentPanel.onclick = () => {
    openExternalContextPanel();
  };
}

function renderPlansSection(state) {
  const current = state.currentState || {};
  const plans = state.plans || [];
  const markAsBrowsing = (id) => document.getElementById(id)?.parentElement.classList.add('panel-browsing');

  markAsBrowsing('dueSoonList');
  markAsBrowsing('shortTermList');
  markAsBrowsing('longTermList');
  markAsBrowsing('recurringList');

  setCountBadge("dueSoonCount", byBucket(plans, "dated").length);
  setCountBadge("shortTermCount", byBucket(plans, "short_term").length);
  setCountBadge("longTermCount", byBucket(plans, "long_term").length);
  setCountBadge("recurringCount", byBucket(plans, "recurring").length);

  const planFormatter = (item) => `
    <div class="list-item signal-item">
      <div class="signal-head">
        <strong>${escapeHtml(item.title)}</strong>
        <span class="session-badge verdict ${escapeHtml(item.status || "pending")}">${escapeHtml(labelStatus(item.status))}</span>
      </div>
      <span>${escapeHtml(item.due_at || labelBucket(item.bucket))}</span>
    </div>
  `;

  const detailFormatter = (secondary) => (i) => `
    <div class='list-item'><strong>${escapeHtml(i.title)}</strong> <span>${escapeHtml(secondary(i))}</span></div>
  `;

  renderCappedList("dueSoonList", byBucket(plans, "dated"), planFormatter, 3, "이번 달 예정된 고정 기한 일정이 없습니다.");
  document.getElementById("dueSoonList")?.parentElement?.addEventListener("click", () => {
    showDetailedList("기한 임박", "기한 고정 플랜", byBucket(state.plans, "dated"), detailFormatter((i) => i.due_at));
  }, { once: true });

  renderCappedList("shortTermList", byBucket(plans, "short_term"), planFormatter, 3, "현재 집중해야 할 단기 계획이 비어 있습니다.");
  document.getElementById("shortTermList")?.parentElement?.addEventListener("click", () => {
    showDetailedList("단기 플랜", "단기 계획", byBucket(state.plans, "short_term"), detailFormatter((i) => labelStatus(i.status)));
  }, { once: true });

  renderCappedList("longTermList", byBucket(plans, "long_term"), planFormatter, 3, "장기적 관점에서 준비 중인 프로젝트가 없습니다.");
  document.getElementById("longTermList")?.parentElement?.addEventListener("click", () => {
    showDetailedList("장기 플랜", "장기 계획", byBucket(state.plans, "long_term"), detailFormatter((i) => labelStatus(i.status)));
  }, { once: true });

  renderCappedList("recurringList", byBucket(plans, "recurring"), planFormatter, 3, "주기적으로 검토할 반복 일정이 설정되지 않았습니다.");
  document.getElementById("recurringList")?.parentElement?.addEventListener("click", () => {
    showDetailedList("반복 플랜", "반복 계획", byBucket(state.plans, "recurring"), detailFormatter((i) => labelStatus(i.status)));
  }, { once: true });
}

function renderSessionsSection(state) {
  renderSessions(); // Already defined in app-sessions.js and refined
}

function renderBriefsSection(state) {
  const targetId = "briefList";
  const parentPanel = document.getElementById(targetId)?.parentElement;
  if (!parentPanel) return;
  parentPanel.classList.add("panel-browsing");

  const items = state.briefs || [];
  setCountBadge("briefCount", items.length);

  const formatter = (item) => {
    const summary = normalizeBriefContent(item.content_md || "")
      .split("\n")
      .map((line) => line.trim())
      .find((line) => line && !line.startsWith("#")) || "핵심 요약이 아직 없습니다.";
    return `
      <div class="list-item candidate-item">
        <div class="candidate-head">
          <strong>${escapeHtml(item.title)}</strong>
          <span class="candidate-rank">${escapeHtml(normalizeBriefTypeLabel(item.brief_type))}</span>
        </div>
        <span class="candidate-reason">${escapeHtml(summary)}</span>
      </div>
    `;
  };

  renderCappedList(targetId, items, formatter, 3, "아직 생성된 브리프가 없습니다. 작업 일지가 쌓이면 AI가 요약 브리프를 생성합니다.");
  parentPanel.onclick = () => {
    showDetailedList("최근 브리프", "브리프 목록", state.briefs, (i) => `
      <div class='list-item'>
        <strong>${escapeHtml(i.title)}</strong>
        <p class='muted'>${escapeHtml(normalizeBriefContent(i.content_md))}</p>
      </div>
    `);
  };
}

function renderWorkdiarySection(state) {
  const targetId = "workdiaryList";
  const parentPanel = document.getElementById(targetId)?.parentElement;
  if (!parentPanel) return;
  parentPanel.classList.add("panel-browsing");

  // 자연 정렬 적용 (Intl.Collator 사용)
  const collator = new Intl.Collator(undefined, {numeric: true, sensitivity: 'base'});
  const items = (state.workdiaryItems || []).sort((a, b) => collator.compare(a.name, b.name));

  setCountBadge("workdiaryCount", items.length);

  const formatter = (item) => `
    <div class="list-item candidate-item">
      <div class="candidate-head">
        <strong>${escapeHtml(item.name)}</strong>
        <span class="candidate-rank">${escapeHtml(normalizeItemTypeLabel(item.item_type))}</span>
      </div>
      <span class="candidate-reason">${escapeHtml(formatDateTime(item.modified_at).slice(0, 16) || "-")}</span>
    </div>
  `;

  renderCappedList(targetId, items, formatter, 3, "workdiary 스캔 결과가 비어 있거나 경로 설정이 필요합니다.");
  parentPanel.onclick = () => {
    showDetailedList("workdiary 상위 폴더", "폴더 목록 (자연 정렬)", items, (i) => `
      <div class='list-item'><strong>${escapeHtml(i.name)}</strong> <span class='muted'>${escapeHtml(i.modified_at)}</span></div>
    `);
  };
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

function renderPriorityCandidatesSection(state) {
  const targetId = "priorityCandidateList";
  const parentPanel = document.getElementById(targetId)?.parentElement;
  if (!parentPanel) return;
  parentPanel.classList.add("panel-browsing");

  const items = state.priorityCandidates || [];
  setCountBadge("priorityCandidateCount", items.length);

  const renderCandidate = (item) => `
    <div class="list-item candidate-item">
      <div class="candidate-head">
        <strong>${escapeHtml(item.name)}</strong>
      </div>
      <span class="candidate-reason">${escapeHtml(item.priority_reason || "-")}</span>
    </div>
  `;

  const formatter = (item) => renderCandidate(item);
  renderCappedList(targetId, items, formatter, 3, "우선순위를 분석할 만한 작업 데이터가 아직 충분하지 않습니다.");
  parentPanel.onclick = () => {
    showDetailedList("우선 검토 후보", "프로젝트 후보 목록", state.priorityCandidates, (i) => `
      <div class='list-item'>
        <strong>${escapeHtml(i.name)}</strong>
        <p class='muted'>${escapeHtml(i.priority_reason)} (점수: ${escapeHtml(String(i.priority_score ?? 0))})</p>
      </div>
    `);
  };
}

async function renderDerivedSuggestionsSection() {
  const targetId = "derivedSuggestionList";
  const container = document.getElementById(targetId);
  if (!container) return;
  const parentPanel = container.parentElement;
  if (parentPanel) parentPanel.classList.add("panel-browsing");

  try {
    const response = await fetch("/api/suggestions");
    const data = await response.json();
    const suggestions = data.suggestions || [];
    state.derivedSuggestions = suggestions;

    setCountBadge("derivedSuggestionCount", suggestions.length);

    if (suggestions.length === 0) {
      container.innerHTML = `<div class="empty-state">추천 퀘스트가 없습니다. CLI에서 새로고침 후 다시 확인하세요.</div>`;
      return;
    }

    container.innerHTML = suggestions.map((s) => {
      const source = normalizeProjectLabel(s.source_project || "unknown");
      return `
        <div class="list-item">
          <div class="candidate-head">
            <strong>[${escapeHtml(source)}] ${escapeHtml(normalizeSuggestionTitle(s.title))}</strong>
          </div>
          <span class="candidate-reason">${escapeHtml(s.why_now || "-")}</span>
        </div>
      `;
    }).join("");

    if (parentPanel) {
      parentPanel.onclick = () => {
        showDetailedList("프로젝트에서 온 추천 퀘스트", "추천 퀘스트 상세", state.derivedSuggestions || [], (i) => `
          <div class='list-item'>
            <strong>[${escapeHtml(normalizeProjectLabel(i.source_project || "unknown"))}] ${escapeHtml(normalizeSuggestionTitle(i.title || "-"))}</strong>
            <p class='muted'>${escapeHtml(i.why_now || "-")}</p>
            <p class='muted'>완료 기준: ${escapeHtml(i.completion_criteria || "-")}</p>
            <p class='muted'>다음 후보: ${escapeHtml(i.next_candidates || i.next_quest_candidates || "-")}</p>
          </div>
        `);
      };
    }
  } catch (error) {
    console.error("Failed to load derived suggestions", error);
    container.innerHTML = `<div class="empty-state">추천 퀘스트를 불러오지 못했습니다.</div>`;
  }
}

window.promoteStartingPoint = async function promoteStartingPoint() {
  if (!window.confirm("어제 확정한 시작점으로 작업을 시작할까요?")) return;
  
  try {
    const response = await fetch("/api/tomorrow-first-quest/promote", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "승격에 실패했습니다.");
    }
    
    const modal = document.getElementById("detailedListModal");
    if (modal) modal.style.display = "none";
    
    if (window.loadAll) await window.loadAll();
    alert("퀘스트를 시작했습니다. 작업 일지를 유지하세요.");
  } catch (error) {
    console.error("Failed to promote starting point:", error);
    alert(`작업 시작 실패: ${error.message}`);
  }
};
