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

function normalizeSuggestionTitle(value) {
  return String(value || "")
    .replace(/IPU AI Security Filter/gi, "IPU AI Firewall")
    .replace(/security-filter/gi, "firewall")
    .trim();
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

function renderSessionsSection(state) {
  renderSessions(); // Already defined in app-sessions.js and refined
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
