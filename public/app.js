/**
 * 0-a-control - Main Application Entry (Orchestrator)
 * Responsibility: State loading and module coordination
 */

function updateQuestFormState(current) {

  const currentQuestExists = Boolean(current.current_quest_id);
  const statusSummary = current.quest_status_summary || {};
  const isAwaitingVerdict = Boolean(statusSummary.is_awaiting_external_verdict);
  const form = document.getElementById("questEvalForm");

  if (form) {
    Array.from(form.elements).forEach((element) => {
      if ("disabled" in element) {
        element.disabled = !currentQuestExists || isAwaitingVerdict;
      }
    });

    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
      if (!currentQuestExists) {
        submitBtn.textContent = "활성 퀘스트 없음";
      } else if (isAwaitingVerdict) {
        submitBtn.textContent = "판정 대기 중(수정 불가)";
      } else {
        submitBtn.textContent = "퀘스트 완료 보고 (Ctrl+Enter)";
      }
    }
  }

  const holdBtn = document.getElementById("holdCurrentQuestBtn");
  if (holdBtn) {
    holdBtn.disabled = !currentQuestExists;
  }

  const deferBtn = document.getElementById("deferCurrentQuestBtn");
  if (deferBtn) {
    deferBtn.disabled = !currentQuestExists;
  }

  const startBtn = document.getElementById("startCurrentQuestBtn");
  if (startBtn) {
    startBtn.hidden = currentQuestExists;
    startBtn.disabled = currentQuestExists;
  }
}

function updateLoadingStatus(loadErrors = [], renderErrors = []) {
  const titleEl = document.getElementById("mainMissionTitle");
  const messageEl = document.getElementById("loadStatusMessage");
  if (!titleEl) return;

  const messages = [];
  if (loadErrors.length > 0) {
    messages.push(`로드 실패: ${loadErrors.join(", ")}`);
  }
  if (renderErrors.length > 0) {
    messages.push(`렌더 실패: ${renderErrors.join(", ")}`);
  }

  if (messageEl) {
    if (messages.length > 0) {
      messageEl.hidden = false;
      messageEl.textContent = messages.join(" | ");
      messageEl.style.color = "var(--red)";
    } else {
      messageEl.hidden = true;
      messageEl.textContent = "";
      messageEl.style.color = "";
    }
  }

  const titleStillLoading = titleEl.textContent.includes("불러오고 있습니다");
  if ((loadErrors.includes("current-state") || renderErrors.includes("hero")) && titleStillLoading) {
    titleEl.textContent = "메인 미션을 불러오지 못했습니다.";
  }
}

function applyApiResult(api, payload) {
  switch (api.key) {
    case "currentState":
      state.currentState = payload?.current_state || null;
      break;
    case "plans":
      state.plans = payload?.plans || [];
      break;
    case "briefs":
      state.briefs = payload?.briefs || [];
      break;
    case "quests":
      state.quests = payload?.quests || [];
      break;
    case "sessions":
      state.sessions = payload?.sessions || [];
      break;
    case "activeSession":
      state.activeSession = payload?.session || null;
      break;
    case "workdiaryItems":
      state.workdiaryItems = payload?.items || [];
      break;
    case "priorityCandidates":
      state.priorityCandidates = payload?.items || [];
      break;
    case "externalInbox":
      state.externalInbox = {
        items: payload?.items || [],
        summary: payload?.summary || {},
      };
      break;
    case "externalInboxPanel":
      state.externalInboxPanel = {
        items: payload?.items || [],
      };
      break;
    case "telegramSyncStatus":
      state.telegramSyncStatus = {
        sources: payload?.sources || [],
      };
      break;
    case "telegramStatus":
      state.telegramStatus = payload || null;
      break;
    default:
      break;
  }
}

function recordLoadFailure(api, reason, errors) {
  if (api.optional) {
    console.warn(`Optional load failed: ${api.label}`, reason);
    return;
  }
  errors.push(api.label);
  console.error(`Failed to load ${api.label}:`, reason);
}

function runRenderStep(label, renderFn, errors) {
  try {
    renderFn();
  } catch (error) {
    errors.push(label);
    console.error(`Failed to render ${label}:`, error);
  }
}

function renderCurrentState() {
  const current = state.currentState || {};
  const activeQuest = state.quests.find((item) => item.id === current.current_quest_id) || {};
  const metadata = activeQuest.metadata_json || {};
  const aiVerdict = metadata.ai_verdict || {};

  const heroResult = renderHeroCard(current) || {};
  const nextCore = heroResult.nextCore || null;
  const cautionText = heroResult.cautionText || "";

  renderRecentVerdictCard(current, state.quests, aiVerdict, metadata.report || {});
  renderNextQuestCard(current);
  renderRestartPointCard(current, aiVerdict);
  renderCautionCard(current, nextCore, cautionText);
  updateQuestFormState(current);
}

async function loadAll() {
  const apis = [
    { key: "currentState", label: "current-state", url: "/api/current-state" },
    { key: "plans", label: "plans", url: "/api/plans" },
    { key: "briefs", label: "briefs", url: "/api/briefs/latest" },
    { key: "quests", label: "quests", url: "/api/quests" },
    { key: "sessions", label: "sessions", url: "/api/sessions/recent?limit=8" },
    { key: "activeSession", label: "active-session", url: "/api/sessions/active" },
    { key: "workdiaryItems", label: "workdiary", url: "/api/workdiary/top-level" },
    { key: "priorityCandidates", label: "priority-candidates", url: "/api/workdiary/priority-candidates" },
    { key: "externalInbox", label: "external-inbox", url: "/api/external-inbox?limit=500" },
    { key: "externalInboxPanel", label: "external-inbox-panel", url: `/api/external-inbox?limit=1000&status=${encodeURIComponent(state.externalContextStatus || "new")}` },
    { key: "telegramSyncStatus", label: "telegram-sync-status", url: "/api/telegram/sync-status", optional: true },
    { key: "telegramStatus", label: "telegram-status", url: "/api/telegram/status", optional: true },
  ];

  const loadErrors = [];
  const renderErrors = [];
  const results = await Promise.allSettled(
    apis.map(async (api) => {
      try {
        const payload = await fetchJson(api.url);
        return { api, payload };
      } catch (error) {
        recordLoadFailure(api, error, loadErrors);
        return { api, payload: null };
      }
    })
  );

  results.forEach((result, index) => {
    const api = apis[index];

    if (result.status === "fulfilled") {
      applyApiResult(api, result.value.payload);
      return;
    }

    recordLoadFailure(api, result.reason, loadErrors);
    applyApiResult(api, null);
  });

  state.loadErrors = [...new Set(loadErrors)];
  state.renderErrors = [];

  runRenderStep("hero", () => renderCurrentState(), renderErrors);
  runRenderStep("support-grid", () => renderSupportGrid(state), renderErrors);
  runRenderStep("plan-changes", () => renderPlanChangesCard(state.currentState || {}), renderErrors);
  runRenderStep("calendar", () => renderCalendarCard(state.plans || [], state.selectedDate), renderErrors);

  state.renderErrors = [...new Set(renderErrors)];
  updateLoadingStatus(state.loadErrors, state.renderErrors);
}

async function refreshExternalContextPanelData() {
  const status = state.externalContextStatus || "new";
  const category = state.externalContextSource && state.externalContextSource !== "all"
    ? `&category=${encodeURIComponent(
        state.externalContextSource === "core" ? "핵심4개" :
        state.externalContextSource === "stock" ? "주식큐레이터" :
        state.externalContextSource === "news" ? "뉴스" :
        state.externalContextSource === "general" ? "일반대화" : state.externalContextSource
      )}`
    : "";

  try {
    const payload = await fetchJson(`/api/external-inbox?limit=1000&status=${encodeURIComponent(status)}${category}`);
    state.externalInboxPanel = {
      items: payload?.items || [],
    };
    renderExternalContextPanel(state);
  } catch (error) {
    console.error("Failed to refresh external context panel:", error);
  }
}

window.refreshExternalContextPanelData = refreshExternalContextPanelData;

function mergeExternalContextThread(existingThread, payload) {
  if (!payload) return null;
  if (!existingThread || existingThread.source_id !== payload.source_id) {
    return {
      ...payload,
      loaded_days: Array.isArray(payload.loaded_days) ? payload.loaded_days : (payload.day ? [payload.day] : []),
      loadingOlder: false,
    };
  }

  const mergedMessages = [...(payload.messages || []), ...(existingThread.messages || [])];
  const dedupedMessages = Array.from(
    new Map(
      mergedMessages.map((message) => [
        `${message.id || ""}:${message.external_message_id || ""}:${message.display_timestamp || message.imported_at || ""}`,
        message,
      ])
    ).values()
  );
  dedupedMessages.sort((a, b) =>
    String(a.display_timestamp || a.item_timestamp || a.imported_at || "").localeCompare(
      String(b.display_timestamp || b.item_timestamp || b.imported_at || "")
    )
  );

  const loadedDays = Array.from(new Set([...(payload.loaded_days || []), ...(existingThread.loaded_days || [])])).sort();
  return {
    ...existingThread,
    ...payload,
    messages: dedupedMessages,
    loaded_days: loadedDays,
    loadingOlder: false,
  };
}

async function refreshExternalContextThread(sourceId) {
  if (!sourceId) {
    state.externalContextThread = null;
    renderExternalContextPanel(state);
    return;
  }

  try {
    const payload = await fetchJson(`/api/external-inbox/source?source_id=${encodeURIComponent(sourceId)}&day=today&limit=500`);
    state.externalContextThread = mergeExternalContextThread(null, payload);
    renderExternalContextPanel(state);
  } catch (error) {
    console.error("Failed to refresh external context thread:", error);
  }
}

window.refreshExternalContextThread = refreshExternalContextThread;

async function loadOlderExternalContextDay() {
  const thread = state.externalContextThread;
  if (!thread?.source_id || !thread.previous_day || thread.loadingOlder) {
    return;
  }

  const detail = document.getElementById("externalContextDetail");
  const previousHeight = detail ? detail.scrollHeight : 0;
  const previousTop = detail ? detail.scrollTop : 0;
  thread.loadingOlder = true;
  renderExternalContextPanel(state);

  try {
    const payload = await fetchJson(
      `/api/external-inbox/source?source_id=${encodeURIComponent(thread.source_id)}&before=${encodeURIComponent(thread.day)}&limit=500`
    );
    state.externalContextThread = mergeExternalContextThread(thread, payload);
    renderExternalContextPanel(state);

    if (detail) {
      requestAnimationFrame(() => {
        const currentDetail = document.getElementById("externalContextDetail");
        if (!currentDetail) return;
        currentDetail.scrollTop = currentDetail.scrollHeight - previousHeight + previousTop;
      });
    }
  } catch (error) {
    console.error("Failed to load older external context day:", error);
    if (state.externalContextThread) {
      state.externalContextThread.loadingOlder = false;
    }
    renderExternalContextPanel(state);
  }
}

window.loadOlderExternalContextDay = loadOlderExternalContextDay;

async function handleQuestEvaluation(event) {
  event.preventDefault();
  const current = state.currentState || {};
  if (!current.current_quest_id) {
    alert("현재 퀘스트가 없습니다.");
    return;
  }

  const payload = {
    quest_id: current.current_quest_id,
    work_summary: document.getElementById("questWorkSummary").value.trim(),
    remaining_work: document.getElementById("questRemainingWork").value.trim(),
    blocker: document.getElementById("questBlocker").value.trim(),
    self_assessment: document.getElementById("questSelfAssessment").value.trim(),
    session_id: state.activeSession?.id || "",
  };

  try {
    await fetchJson("/api/quests/report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (e) {
    alert(e.message || "보고 실패");
    return;
  }

  event.target.reset();
  document.getElementById("questSelfAssessment").value = "partial";
  closeReportPanel();
  await loadAll();
}

async function handleHoldCurrentQuest() {
  const current = state.currentState || {};
  if (!current.current_quest_id) {
    alert("현재 퀘스트가 없습니다.");
    return;
  }

  const btn = document.getElementById("holdCurrentQuestBtn");
  if (btn) {
    btn.disabled = true;
    btn.textContent = "정리 중...";
  }

  try {
    await fetchJson("/api/current-quest/hold", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    await loadAll();
  } catch (error) {
    alert(`미완료 처리 실패: ${error.message}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "미완료로 남기기";
    }
  }
}

async function handleStartCurrentQuest() {
  const current = state.currentState || {};
  if (current.current_quest_id) {
    await loadAll();
    return;
  }

  const btn = document.getElementById("startCurrentQuestBtn");
  if (btn) {
    btn.disabled = true;
    btn.textContent = "생성 중...";
  }

  try {
    await fetchJson("/api/current-quest/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    await loadAll();
  } catch (error) {
    alert(`퀘스트 시작 실패: ${error.message}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "지금 퀘스트 잡기";
    }
  }
}

async function handleDeferCurrentQuest() {
  const current = state.currentState || {};
  if (!current.current_quest_id) {
    alert("현재 퀘스트가 없습니다.");
    return;
  }

  const btn = document.getElementById("deferCurrentQuestBtn");
  if (btn) {
    btn.disabled = true;
    btn.textContent = "정리 중...";
  }

  try {
    await fetchJson("/api/current-quest/defer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    await loadAll();
  } catch (error) {
    alert(`단기 플랜 이동 실패: ${error.message}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "단기 플랜으로";
    }
  }
}

async function handleTelegramSync() {
  const btn = document.getElementById("syncTelegramBtn");
  const banner = document.getElementById("syncStatusBanner");
  if (!btn) return;

  state.telegramSyncRunning = true;
  btn.disabled = true;
  btn.textContent = "동기화 중...";
  renderTelegramSyncStatus();
  if (banner) banner.style.opacity = "0.65";

  try {
    const res = await fetchJson("/api/telegram/sync-core", { method: "POST" });
    state.lastTelegramSyncRun = {
      ...res,
      executed_at: new Date().toISOString(),
    };
    // Refresh data
    await loadAll();
    await refreshExternalContextPanelData();
  } catch (error) {
    console.error("Telegram sync failed:", error);
    state.lastTelegramSyncRun = {
      ok: false,
      error: error.message,
      failed_at: new Date().toISOString(),
    };
    renderTelegramSyncStatus();
    alert(`Telegram 동기화 실패: ${error.message}`);
  } finally {
    state.telegramSyncRunning = false;
    btn.disabled = false;
    btn.textContent = "지금 동기화";
    if (banner) banner.style.opacity = "1";
    renderTelegramSyncStatus();
  }
}

document.getElementById("openReportPanelBtn").addEventListener("click", openReportPanel);
document.getElementById("holdCurrentQuestBtn")?.addEventListener("click", handleHoldCurrentQuest);
document.getElementById("deferCurrentQuestBtn")?.addEventListener("click", handleDeferCurrentQuest);
document.getElementById("openExternalContextPanelBtn").addEventListener("click", openExternalContextPanel);
document.getElementById("openBridgePanelBtn")?.addEventListener("click", openBridgePanel);
document.getElementById("syncTelegramBtn").addEventListener("click", handleTelegramSync);
document.getElementById("closeReportPanelBtn").addEventListener("click", closeReportPanel);
document.getElementById("closeDetailPanelBtn").addEventListener("click", closeDetailPanel);

let bridgeState = { parsed: null };

function openBridgePanel() {
  document.getElementById("bridgePanel").hidden = false;
  document.getElementById("bridgePanel").style.display = "block";
}

function closeBridgePanel() {
  document.getElementById("bridgePanel").hidden = true;
  document.getElementById("bridgePanel").style.display = "none";
  document.getElementById("bridgeInput").value = "";
  document.getElementById("bridgeResult").innerHTML = "";
  document.getElementById("bridgeCreatePlanBtn").disabled = true;
  bridgeState.parsed = null;
}

async function handleBridgeParse() {
  const text = document.getElementById("bridgeInput").value.trim();
  if (!text) return;

  const btn = document.getElementById("bridgeParseBtn");
  btn.disabled = true;
  btn.textContent = "정리 중...";

  try {
    const res = await fetchJson("/api/bridge/quick-input", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    bridgeState.parsed = res;

    const resultDiv = document.getElementById("bridgeResult");
    const candidates = res.candidates || [];
    const mainMission = res.main_mission;
    const currentQuest = res.current_quest;
    const summary = res.summary || {};

    const todayCandidates = candidates.filter(p => p.bucket === "today").sort((a, b) => (b.priority_score || 0) - (a.priority_score || 0));
    const datedCandidates = candidates.filter(p => p.bucket === "dated").sort((a, b) => (b.priority_score || 0) - (a.priority_score || 0));
    const holdCandidates = candidates.filter(p => p.bucket === "hold").sort((a, b) => (b.priority_score || 0) - (a.priority_score || 0));
    const otherCandidates = candidates.filter(p => !["today", "dated", "hold"].includes(p.bucket)).sort((a, b) => (b.priority_score || 0) - (a.priority_score || 0));

    const bucketLabels = {
      "today": "오늘",
      "dated": "기한",
      "hold": "보류",
      "short_term": "단기",
      "long_term": "장기",
      "recurring": "반복"
    };

    const bucketColors = {
      "today": "bridge-bucket-today",
      "dated": "bridge-bucket-dated",
      "hold": "bridge-bucket-hold",
      "short_term": "bridge-bucket-short",
      "long_term": "bridge-bucket-long",
      "recurring": "bridge-bucket-recurring"
    };

    let html = "";

    html += `<div class="bridge-summary">`;
    html += `<span class="bridge-count-badge bridge-bucket-today">${summary.today_count || 0}개 오늘</span>`;
    html += `<span class="bridge-count-badge bridge-bucket-dated">${summary.dated_count || 0}개 기한</span>`;
    html += `<span class="bridge-count-badge bridge-bucket-hold">${summary.hold_count || 0}개 보류</span>`;
    html += `</div>`;

    if (mainMission || currentQuest) {
      html += `<div class="bridge-priority-section">`;
      if (mainMission) {
        html += `<div class="bridge-highlight-card bridge-main-mission">
          <span class="bridge-priority-label">📌 메인 미션</span>
          <strong class="bridge-priority-title">${escapeHtml(mainMission.title)}</strong>
          <span class="bridge-priority-reason">${escapeHtml(mainMission.reason || "")}</span>
        </div>`;
      }
      if (currentQuest) {
        html += `<div class="bridge-highlight-card bridge-current-quest">
          <span class="bridge-priority-label">🎯 현재 퀘스트</span>
          <strong class="bridge-priority-title">${escapeHtml(currentQuest.title)}</strong>
          <span class="bridge-priority-reason">${escapeHtml(currentQuest.reason || "")}</span>
        </div>`;
      }
      html += `</div>`;
    }

    const renderCandidateSection = (items, label, icon) => {
      if (!items.length) return "";
      let section = `<div class="bridge-section">
  <p class="bridge-section-title">${icon} ${label} <span class="bridge-section-count">(${items.length}개)</span></p>
  <div class="bridge-candidates-list">`;
      items.forEach(p => {
        const score = p.priority_score ? `<span class="bridge-score-small">${p.priority_score}점</span>` : "";
        const due = p.due_date ? `<span class="bridge-due-small">${p.due_date}</span>` : "";
        section += `<div class="bridge-candidate-item">
  <span class="bridge-bucket-badge ${bucketColors[p.bucket] || ""}">${bucketLabels[p.bucket] || p.bucket}</span>
  <span class="bridge-candidate-title">${escapeHtml(p.title)}</span>
  <div class="bridge-candidate-meta">${score}${due}</div>
</div>`;
      });
      section += `</div></div>`;
      return section;
    };

    html += renderCandidateSection(todayCandidates, "오늘", "📅");
    html += renderCandidateSection(datedCandidates, "기한", "⏰");
    html += renderCandidateSection(holdCandidates, "보류", "⏸");
    html += renderCandidateSection(otherCandidates, "기타", "📋");

    resultDiv.innerHTML = html;

    document.getElementById("bridgeCreatePlanBtn").disabled = false;
  } catch (e) {
    alert("분류 실패: " + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "정리하기";
  }
}

async function handleBridgeCreatePlan() {
  if (!bridgeState.parsed?.candidates?.length) return;

  const btn = document.getElementById("bridgeCreatePlanBtn");
  btn.disabled = true;
  btn.textContent = "생성 중...";

  try {
    await fetchJson("/api/bridge/create-plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ candidates: bridgeState.parsed.candidates }),
    });

    alert("Plan이 생성되었습니다!");
    closeBridgePanel();
    loadAll();
  } catch (e) {
    alert("생성 실패: " + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Plan 생성";
  }
}

document.getElementById("closeBridgePanelBtn")?.addEventListener("click", closeBridgePanel);
document.getElementById("bridgeParseBtn")?.addEventListener("click", handleBridgeParse);
document.getElementById("bridgeCreatePlanBtn")?.addEventListener("click", handleBridgeCreatePlan);
document.getElementById("startCurrentQuestBtn")?.addEventListener("click", handleStartCurrentQuest);
document.getElementById("panelBackdrop").addEventListener("click", () => {
  closeReportPanel();
  closeDetailPanel();
  closeExternalContextPanel();
  document.getElementById("panelBackdrop").hidden = true;
});

const evalForm = document.getElementById("questEvalForm");
if (evalForm) {
  evalForm.addEventListener("submit", (event) => {
    handleQuestEvaluation(event).catch((error) => {
      console.error(error);
      alert("퀘스트 판정 반영에 실패했습니다.");
    });
  });
}

loadAll().catch((error) => {
  console.error("Initial load failed:", error);
  state.loadErrors = ["loadAll"];
  state.renderErrors = [];
  updateLoadingStatus(state.loadErrors, state.renderErrors);
});
