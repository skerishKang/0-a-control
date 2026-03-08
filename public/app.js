const state = {
  currentState: null,
  plans: [],
  briefs: [],
  quests: [],
  sessions: [],
  workdiaryItems: [],
  priorityCandidates: [],
  sessionAgentFilter: "all",
  sessionRecordFilter: "all",
  sessionPanelRecords: [],
  activeSession: null,
};

const sessionAgentOptions = [{ value: "all", label: "전체" }, { value: "codex", label: "codex" }, { value: "gemini-cli", label: "gemini-cli" }, { value: "antigravity", label: "antigravity" }, { value: "windsurf", label: "windsurf" }, { value: "kilo", label: "kilo" }, { value: "opencode", label: "opencode" }];
const visibleSessionAgents = new Set(sessionAgentOptions.filter((option) => option.value !== "all").map((option) => option.value));
const sessionRecordOptions = [{ value: "all", label: "전체" }, { value: "user", label: "사용자" }, { value: "assistant", label: "모델" }, { value: "tool", label: "도구" }];

// Utility functions moved to app-utils.js

function openReportPanel() {
  const panel = document.getElementById("reportPanel");
  const backdrop = document.getElementById("panelBackdrop");
  closeSessionPanel();
  panel.hidden = false;
  panel.classList.add("open");
  panel.setAttribute("aria-hidden", "false");
  backdrop.hidden = false;
}

function closeReportPanel() {
  const panel = document.getElementById("reportPanel");
  const backdrop = document.getElementById("panelBackdrop");
  if (!panel) return;
  panel.classList.remove("open");
  panel.setAttribute("aria-hidden", "true");
  backdrop.hidden = true;
  window.setTimeout(() => {
    if (!panel.classList.contains("open")) {
      panel.hidden = true;
    }
  }, 180);
}

function openSessionPanel() {
  const panel = document.getElementById("sessionPanel");
  const backdrop = document.getElementById("panelBackdrop");
  closeReportPanel();
  panel.hidden = false;
  panel.classList.add("open");
  panel.setAttribute("aria-hidden", "false");
  backdrop.hidden = false;
}

function closeSessionPanel() {
  const panel = document.getElementById("sessionPanel");
  if (!panel) return;
  panel.classList.remove("open");
  panel.setAttribute("aria-hidden", "true");
  window.setTimeout(() => {
    if (!panel.classList.contains("open")) {
      panel.hidden = true;
    }
  }, 180);
}

function openDetailPanel(label, title, bodyHtml) {
  const panel = document.getElementById("detailPanel");
  const backdrop = document.getElementById("panelBackdrop");
  closeReportPanel();
  closeSessionPanel();
  
  document.getElementById("detailPanelLabel").textContent = label;
  document.getElementById("detailPanelTitle").textContent = title;
  document.getElementById("detailPanelBody").innerHTML = bodyHtml;
  
  panel.hidden = false;
  panel.classList.add("open");
  panel.setAttribute("aria-hidden", "false");
  backdrop.hidden = false;
}

function closeDetailPanel() {
  const panel = document.getElementById("detailPanel");
  const backdrop = document.getElementById("panelBackdrop");
  if (!panel) return;
  panel.classList.remove("open");
  panel.setAttribute("aria-hidden", "true");
  backdrop.hidden = true;
  window.setTimeout(() => {
    if (!panel.classList.contains("open")) {
      panel.hidden = true;
    }
  }, 180);
}


function renderCurrentState() {
  const current = state.currentState || {};

  document.getElementById("mainMissionTitle").textContent = current.main_mission_title || "주 임무가 없습니다.";
  document.getElementById("mainMissionReason").textContent = summarizeMissionReason(current.main_mission_reason);
  document.getElementById("mainMissionCriteria").textContent =
    current.main_mission_completion_criteria || "완료 기준이 아직 없습니다.";
  document.getElementById("currentQuestTitle").textContent =
    current.current_quest_title || "현재 퀘스트가 없습니다.";

  const recentVerdict = current.recent_verdict || {};
  const statusSummary = current.quest_status_summary || {};
  const recentVerdictTarget = document.getElementById("recentVerdict");
  const activeQuest = state.quests.find((item) => item.id === current.current_quest_id) || {};
  const metadata = activeQuest.metadata_json || {};
  const aiVerdict = metadata.ai_verdict || {};
  const report = metadata.report || {};

  if (recentVerdictTarget) {
    if (statusSummary.is_awaiting_external_verdict) {
      recentVerdictTarget.innerHTML = `
        <div class="verdict-card-main">
          <div class="signal-head">
            <strong>${escapeHtml(current.current_quest_title || "퀘스트")}</strong>
            <span class="session-badge verdict pending">Awaiting</span>
          </div>
          <span class="verdict-reason-preview muted" style="font-size: 0.85rem; opacity: 0.85;">${escapeHtml(statusSummary.preliminary_reason || "외부 에이전트의 응답을 기다리고 있습니다.")}</span>
        </div>
      `;
    } else if (recentVerdict.title) {
      const providerStr = statusSummary.latest_verdict_provider ? ` (by ${statusSummary.latest_verdict_provider})` : "";
      recentVerdictTarget.innerHTML = `
        <div class="verdict-card-main">
          <div class="signal-head">
            <strong>${escapeHtml(recentVerdict.title)}</strong>
            ${renderVerdictBadge(recentVerdict.status)}
          </div>
          <span class="verdict-reason-preview">${escapeHtml(summarizeVerdictReason(recentVerdict.status, aiVerdict.reason))}</span>
          <span>${escapeHtml(formatRecentLabel(recentVerdict.updated_at))}${escapeHtml(providerStr)}</span>
        </div>
      `;
    } else {
      recentVerdictTarget.innerHTML = `<div class="list-item empty">퀘스트를 보고하면 여기에 AI 판정이 쌓입니다.</div>`;
    }
  }

  renderList(
    "nextQuestHint",
    current.recommended_next_quest
      ? [{
        title: current.recommended_next_quest,
        reason: current.restart_point || current.latest_decision_summary?.impact_summary || "현재 흐름을 이어가기 위한 다음 작은 행동",
      }]
      : [],
    (item) => `
      <div class="list-item signal-item next-quest-item">
        <div class="signal-head">
          <strong>${escapeHtml(item.title)}</strong>
          <span class="session-badge verdict partial">다음</span>
        </div>
        <span>${escapeHtml(item.reason)}</span>
      </div>
    `,
    "다음 퀘스트가 정리되면 여기에 표시됩니다."
  );

  const currentQuestExists = Boolean(current.current_quest_id);
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
        submitBtn.textContent = "퀘스트 없음";
      } else if (isAwaitingVerdict) {
        submitBtn.textContent = "판정 대기 중 (수정 불가)";
      } else {
        submitBtn.textContent = "퀘스트 완료 보고 (Ctrl+Enter)";
      }
    }
  }

  const progress = current.day_progress_summary || {};
  const unfinished = current.top_unfinished_summary || [];
  const latestVerdictStatus = recentVerdict.verdict || "";
  const missionSummary = unfinished.find((item) => item.title === current.main_mission_title) || unfinished[0] || null;
  const missionStatus = missionSummary?.status || latestVerdictStatus || "pending";
  const missionSecondary = missionSummary
    ? `${labelBucket(missionSummary.bucket)} / ${labelStatus(missionSummary.status)}`
    : "오늘 기준 다시 확인 필요";
  const nextCore = unfinished.find((item) => item.title !== current.main_mission_title) || null;
  const missionProgress = missionProgressPercent(missionStatus);
  const mainMissionStatus = document.getElementById("mainMissionStatus");
  if (mainMissionStatus) {
    let badges = renderVerdictBadge(missionStatus);
    if (statusSummary.is_pending && missionStatus !== 'pending') {
      badges += renderVerdictBadge("pending");
    }
    mainMissionStatus.innerHTML = badges;
  }
  const mainMissionProgressFill = document.getElementById("mainMissionProgressFill");
  if (mainMissionProgressFill) {
    mainMissionProgressFill.className = `progress-track-fill ${missionStatus}`;
    mainMissionProgressFill.style.width = `${missionProgress}%`;
  }
  const mainMissionProgressText = document.getElementById("mainMissionProgressText");
  if (mainMissionProgressText) {
    mainMissionProgressText.textContent = `현재 상태: ${labelStatus(missionStatus)} · ${missionProgress}%`;
  }
  const mainMissionRisk = document.getElementById("mainMissionRisk");
  if (mainMissionRisk) {
    mainMissionRisk.textContent = missionRiskText({
      missionStatus,
      nextCore,
      currentQuestTitle: current.current_quest_title,
    });
  }
  document.getElementById("progressSummary").innerHTML = `
    <div class="progress-focus">
      <div class="progress-focus-head">
        <strong>${escapeHtml(current.main_mission_title || "오늘 주 임무 확인 필요")}</strong>
        ${renderVerdictBadge(missionStatus)}${statusSummary.is_pending && missionStatus !== 'pending' ? renderVerdictBadge("pending") : ""}
      </div>
      <span>${escapeHtml(missionSecondary)}</span>
      <div class="progress-track" aria-label="오늘 주 임무 진행률">
        <div class="progress-track-fill ${escapeHtml(missionStatus)}" style="width: ${missionProgress}%"></div>
      </div>
      <span class="progress-track-label">주 임무 기준 진행 ${missionProgress}%</span>
    </div>
    <div class="progress-pill-row">
      <div class="progress-pill done">완료 ${progress.done || 0}</div>
      <div class="progress-pill partial">부분완료 ${progress.partial || 0}</div>
      <div class="progress-pill hold">보류 ${progress.hold || 0}</div>
      <div class="progress-pill active">진행중 ${progress.active || 0}</div>
    </div>
    <div class="progress-tail">
      <strong>아직 남은 핵심</strong>
      <span>${escapeHtml(nextCore ? nextCore.title : current.current_quest_title || "현재 퀘스트를 이어가면 됩니다")}</span>
    </div>
  `;

  const detailBody = document.getElementById("verdictDetailBody");
  if (detailBody) {
    detailBody.innerHTML = aiVerdict.verdict
      ? `
        <div class="detail-section"><strong>AI 판정</strong><p>${escapeHtml(labelStatus(aiVerdict.verdict))}</p></div>
        <div class="detail-section"><strong>판정 이유</strong><p>${escapeHtml(aiVerdict.reason || "-")}</p></div>
        <div class="detail-section"><strong>재시작 지점</strong><p>${escapeHtml(aiVerdict.restart_point || "-")}</p></div>
        <div class="detail-section"><strong>다음 퀘스트</strong><p>${escapeHtml(aiVerdict.next_hint || "-")}</p></div>
        <div class="detail-section"><strong>계획 반영</strong><p>${escapeHtml(aiVerdict.plan_impact || "-")}</p></div>
        <div class="detail-section"><strong>사용자 보고</strong><p>${escapeHtml(report.work_summary || "-")}</p></div>
      `
      : `<p class="muted">아직 상세 판정이 없습니다.</p>`;
  }
}

async function loadAll() {
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
  renderCurrentState();
  renderPlans();
  renderBriefs();
  renderSessions();
  renderWorkdiary();
  renderPriorityCandidates();
  renderPlanChanges();
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
document.getElementById("closeSessionPanelBtn").addEventListener("click", closeSessionPanel);
document.getElementById("closeDetailPanelBtn").addEventListener("click", closeDetailPanel);
document.getElementById("panelBackdrop").addEventListener("click", () => {
  closeReportPanel();
  closeSessionPanel();
  closeDetailPanel();
  document.getElementById("panelBackdrop").hidden = true;
});
document.getElementById("questEvalForm").addEventListener("submit", (event) => {
  handleQuestEvaluation(event).catch((error) => {
    console.error(error);
    alert("퀘스트 판정을 반영하지 못했습니다.");
  });
});

loadAll().catch((error) => {
  console.error(error);
  alert("상태를 불러오지 못했습니다.");
});
