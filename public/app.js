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
    default:
      break;
  }
}

function recordLoadFailure(api, reason, errors) {
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

  await fetchJson("/api/quests/report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  event.target.reset();
  document.getElementById("questSelfAssessment").value = "partial";
  closeReportPanel();
  await loadAll();
}

document.getElementById("openReportPanelBtn").addEventListener("click", openReportPanel);
document.getElementById("closeReportPanelBtn").addEventListener("click", closeReportPanel);
document.getElementById("closeDetailPanelBtn").addEventListener("click", closeDetailPanel);
document.getElementById("panelBackdrop").addEventListener("click", () => {
  closeReportPanel();
  closeDetailPanel();
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
