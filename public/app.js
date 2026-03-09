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
        submitBtn.textContent = "판정 대기 중 (수정 불가)";
      } else {
        submitBtn.textContent = "퀘스트 완료 보고 (Ctrl+Enter)";
      }
    }
  }
}

function renderCurrentState() {
  const current = state.currentState || {};

  // 1. Hero Card (Main Mission & Progress)
  const { nextCore, cautionText } = renderHeroCard(current);

  // 2. Action Panels (Recent Verdict, Next Quest, Restart Point, Cautions)
  renderRecentVerdictCard(current);
  renderNextQuestCard(current);
  renderRestartPointCard(current);
  renderCautionCard(current, nextCore, cautionText);

  // 3. UI States
  updateQuestFormState(current);
}

async function loadAll() {
  try {
    const [currentPayload, plansPayload, briefsPayload, questsPayload, sessionsPayload, activeSessionPayload, workdiaryPayload, priorityPayload] = await Promise.all([
      fetchJson("/api/current-state"),
      fetchJson("/api/plans"),
      fetchJson("/api/briefs/latest"),
      fetchJson("/api/quests"),
      fetchJson("/api/sessions/recent?limit=8"),
      fetchJson("/api/sessions/active"),
      fetchJson("/api/workdiary/top-level"),
      fetchJson("/api/workdiary/priority-candidates"),
    ]);

    state.currentState = currentPayload.current_state;
    state.plans = plansPayload.plans;
    state.briefs = briefsPayload.briefs;
    state.quests = questsPayload.quests;
    state.sessions = sessionsPayload.sessions;
    state.activeSession = activeSessionPayload.session || null;
    state.workdiaryItems = workdiaryPayload.items;
    state.priorityCandidates = priorityPayload.items;

    // Orchestrate rendering across modules
    renderCurrentState();
    renderSupportGrid(state);
    renderPlanChangesCard(state.currentState);
    renderCalendarCard(state.plans, state.selectedDate);
  } catch (error) {
    console.error("Failed to load dashboard data:", error);
    // alert("상태를 불러오지 못했습니다.");
  }
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

// Global Event Listeners
document.getElementById("openReportPanelBtn").addEventListener("click", openReportPanel);
document.getElementById("closeReportPanelBtn").addEventListener("click", closeReportPanel);
document.getElementById("closeSessionPanelBtn").addEventListener("click", closeSessionPanel);
document.getElementById("closeDetailPanelBtn").addEventListener("click", closeDetailPanel);
document.getElementById("panelBackdrop").addEventListener("click", () => {
  closeReportPanel();
  closeSessionPanel();
  closeDetailPanel();
  document.getElementById("panelBackdrop").hidden = true;
});

const evalForm = document.getElementById("questEvalForm");
if (evalForm) {
  evalForm.addEventListener("submit", (event) => {
    handleQuestEvaluation(event).catch((error) => {
      console.error(error);
      alert("퀘스트 판정을 반영하지 못했습니다.");
    });
  });
}

// Initial Load
loadAll();
