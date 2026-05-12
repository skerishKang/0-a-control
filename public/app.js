/**
 * 0-a-control - Main Application Entry (Init & Core)
 * Responsibility: State loading, API orchestration, form state, rendering
 */

// ── State helpers (defined in app-utils.js via <script>) ──────────

// ── Form & UI ─────────────────────────────────────────────────────

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
  if (holdBtn) holdBtn.disabled = !currentQuestExists;

  const deferBtn = document.getElementById("deferCurrentQuestBtn");
  if (deferBtn) deferBtn.disabled = !currentQuestExists;

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
  if (loadErrors.length > 0) messages.push("로드 실패: " + loadErrors.join(", "));
  if (renderErrors.length > 0) messages.push("렌더 실패: " + renderErrors.join(", "));

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

// ── API & rendering ───────────────────────────────────────────────

function applyApiResult(api, payload) {
  switch (api.key) {
    case "currentState":    state.currentState = payload?.current_state || null; break;
    case "plans":           state.plans = payload?.plans || []; break;
    case "briefs":          state.briefs = payload?.briefs || []; break;
    case "quests":          state.quests = payload?.quests || []; break;
    case "sessions":        state.sessions = payload?.sessions || []; break;
    case "agents":          state.agents = payload?.agents || []; break;
    case "activeSession":   state.activeSession = payload?.session || null; break;
    case "workdiaryItems":  state.workdiaryItems = payload?.items || []; break;
    case "priorityCandidates": state.priorityCandidates = payload?.items || []; break;
    case "externalInbox":
      state.externalInbox = { items: payload?.items || [], summary: payload?.summary || {} };
      break;
    case "externalInboxPanel":
      state.externalInboxPanel = { items: payload?.items || [] };
      break;
    case "telegramSyncStatus":
      state.telegramSyncStatus = { sources: payload?.sources || [] };
      break;
    case "telegramStatus":  state.telegramStatus = payload || null; break;
  }
}

function recordLoadFailure(api, reason, errors) {
  if (api.optional) { console.warn("Optional load failed: " + api.label, reason); return; }
  errors.push(api.label);
  console.error("Failed to load " + api.label + ":", reason);
}

function runRenderStep(label, renderFn, errors) {
  try { renderFn(); } catch (error) { errors.push(label); console.error("Failed to render " + label + ":", error); }
}

function renderCurrentState() {
  const current = state.currentState || {};
  const activeQuest = state.quests.find(item => item.id === current.current_quest_id) || {};
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
    { key: "currentState",        label: "current-state",               url: "/api/current-state" },
    { key: "plans",               label: "plans",                       url: "/api/plans" },
    { key: "briefs",              label: "briefs",                      url: "/api/briefs/latest" },
    { key: "quests",              label: "quests",                      url: "/api/quests" },
    { key: "sessions",            label: "sessions",                    url: "/api/sessions/recent?limit=8" },
    { key: "agents",              label: "agents",                      url: "/api/agents/status", optional: true },
    { key: "activeSession",       label: "active-session",              url: "/api/sessions/active" },
    { key: "workdiaryItems",      label: "workdiary",                   url: "/api/workdiary/top-level" },
    { key: "priorityCandidates",  label: "priority-candidates",         url: "/api/workdiary/priority-candidates" },
    { key: "externalInbox",       label: "external-inbox",              url: "/api/external-inbox?limit=500" },
    { key: "externalInboxPanel",  label: "external-inbox-panel",        url: "/api/external-inbox?limit=1000&status=" + encodeURIComponent(state.externalContextStatus || "new") },
    { key: "telegramSyncStatus",  label: "telegram-sync-status",        url: "/api/telegram/sync-status", optional: true },
    { key: "telegramStatus",      label: "telegram-status",             url: "/api/telegram/status", optional: true },
  ];

  const loadErrors = [];
  const renderErrors = [];

  const results = await Promise.allSettled(
    apis.map(async api => {
      try { return { api, payload: await fetchJson(api.url) }; }
      catch (error) { recordLoadFailure(api, error, loadErrors); return { api, payload: null }; }
    })
  );

  results.forEach((result, index) => {
    const api = apis[index];
    if (result.status === "fulfilled") { applyApiResult(api, result.value.payload); return; }
    recordLoadFailure(api, result.reason, loadErrors);
    applyApiResult(api, null);
  });

  state.loadErrors = [...new Set(loadErrors)];
  state.renderErrors = [];

  runRenderStep("hero",        () => renderCurrentState(), renderErrors);
  runRenderStep("support-grid", () => renderSupportGrid(state), renderErrors);
  runRenderStep("plan-changes", () => renderPlanChangesCard(state.currentState || {}), renderErrors);
  runRenderStep("calendar",    () => renderCalendarCard(state.plans || [], state.selectedDate), renderErrors);

  state.renderErrors = [...new Set(renderErrors)];
  updateLoadingStatus(state.loadErrors, state.renderErrors);
}

// ── Event bindings (deferred until all modules loaded) ────────────

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("openReportPanelBtn")?.addEventListener("click", openReportPanel);
  document.getElementById("holdCurrentQuestBtn")?.addEventListener("click", handleHoldCurrentQuest);
  document.getElementById("deferCurrentQuestBtn")?.addEventListener("click", handleDeferCurrentQuest);
  document.getElementById("openExternalContextPanelBtn")?.addEventListener("click", openExternalContextPanel);
  document.getElementById("syncTelegramBtn")?.addEventListener("click", handleTelegramSync);
  document.getElementById("closeReportPanelBtn")?.addEventListener("click", closeReportPanel);
  document.getElementById("closeDetailPanelBtn")?.addEventListener("click", closeDetailPanel);
  document.getElementById("startCurrentQuestBtn")?.addEventListener("click", handleStartCurrentQuest);

  document.getElementById("panelBackdrop")?.addEventListener("click", () => {
    closeReportPanel(); closeDetailPanel(); closeExternalContextPanel();
    document.getElementById("panelBackdrop").hidden = true;
  });

  document.getElementById("questEvalForm")?.addEventListener("submit", event => {
    event.preventDefault();
    handleQuestEvaluation(event).catch(error => { console.error(error); alert("퀘스트 판정 반영에 실패했습니다."); });
  });

  loadAll().catch(error => {
    console.error("Initial load failed:", error);
    state.loadErrors = ["loadAll"];
    state.renderErrors = [];
    updateLoadingStatus(state.loadErrors, state.renderErrors);
  });
});