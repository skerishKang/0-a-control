function formatDashboardTodayLabel() {
  const now = new Date();
  const weekdays = ["일", "월", "화", "수", "목", "금", "토"];
  const yyyy = now.getFullYear();
  const mm = String(now.getMonth() + 1).padStart(2, "0");
  const dd = String(now.getDate()).padStart(2, "0");
  return `오늘 ${yyyy}-${mm}-${dd} (${weekdays[now.getDay()]})`;
}

function pickDashboardFreshness(current) {
  const verdictAt = current?.recent_verdict?.updated_at || "";
  const briefTitle = current?.latest_morning_brief?.title || "";
  const briefDateMatch = briefTitle.match(/\d{4}-\d{2}-\d{2}/);
  const stale = current?.quest_status_summary?.is_stale;

  if (verdictAt) {
    const label = typeof formatRecentLabel === "function" ? formatRecentLabel(verdictAt) : verdictAt;
    return stale ? `데이터 기준 ${label} · 이전 판단 유지 중` : `데이터 기준 ${label}`;
  }
  if (briefDateMatch) {
    return stale ? `브리프 기준 ${briefDateMatch[0]} · 갱신 필요` : `브리프 기준 ${briefDateMatch[0]}`;
  }
  return "데이터 기준 확인 필요";
}
/**
 * Hero Card rendering module
 * Responsibility: UI rendering for the main mission and overall progress
 */

function renderHeroCard(current) {
  const statusSummary = current.quest_status_summary || {};
  const todayLabel = document.getElementById("dashboardTodayLabel");
  const freshnessLabel = document.getElementById("dashboardFreshnessLabel");
  if (todayLabel) todayLabel.textContent = formatDashboardTodayLabel();
  if (freshnessLabel) freshnessLabel.textContent = pickDashboardFreshness(current);
  
  // 1. Titles & Texts
  document.getElementById("mainMissionTitle").textContent = current.main_mission_title || "주 임무가 없습니다.";
  
  // Store reason for the button
  const reason = current.main_mission_reason || "추천 이유가 없습니다.";
  const reasonBtn = document.getElementById("openMissionReasonBtn");
  if (reasonBtn) {
    reasonBtn.onclick = () => {
      openDetailPanel("추천 이유", current.main_mission_title, `<div class="detail-content"><p>${reason.replace(/\n/g, '<br>')}</p></div>`);
    };
  }

  document.getElementById("mainMissionCriteria").textContent =
    current.main_mission_completion_criteria || "완료 기준이 아직 없습니다.";
  document.getElementById("currentQuestTitle").textContent =
    current.current_quest_title || "현재 퀘스트가 없습니다.";

  // 2. Mission Status (Calculated but not rendered as a badge in hero anymore as per request)
  const unfinished = current.top_unfinished_summary || [];
  const recentVerdict = current.recent_verdict || {};
  const latestVerdictStatus = recentVerdict.verdict || "";
  const missionSummary = unfinished.find((item) => item.title === current.main_mission_title) || unfinished[0] || null;
  const missionStatus = missionSummary?.status || latestVerdictStatus || "pending";

  // 3. Progress Fill & Text
  // Note: Hero card progress elements are now expected in index.html (mainMissionProgressFill, etc.)
  // If they are missing, we skip them silently to avoid errors.
  const missionProgress = missionProgressPercent(missionStatus);
  const mainMissionProgressFill = document.getElementById("mainMissionProgressFill");
  if (mainMissionProgressFill) {
    mainMissionProgressFill.className = `progress-track-fill ${missionStatus}`;
    mainMissionProgressFill.style.width = `${missionProgress}%`;
  }
  const mainMissionProgressText = document.getElementById("mainMissionProgressText");
  if (mainMissionProgressText) {
    const statusLabel = typeof labelStatus === 'function' ? labelStatus(missionStatus) : missionStatus;
    mainMissionProgressText.textContent = `현재 상태: ${statusLabel} · ${missionProgress}%`;
  }

  // 4. Mission Risk / Caution Hint Calculation
  const nextCore = unfinished.find((item) => item.title !== current.main_mission_title) || null;
  let cautionText = missionRiskText({
    missionStatus,
    nextCore,
    currentQuestTitle: current.current_quest_title,
  });
  
  if (statusSummary.is_stale && statusSummary.stale_reason) {
    cautionText = `${statusSummary.stale_reason} ${cautionText}`;
  }

  const mainMissionRisk = document.getElementById("mainMissionRisk");
  if (mainMissionRisk) {
    mainMissionRisk.textContent = cautionText;
  }

  // Return values for other cards to use (like Caution Card)
  return { nextCore, cautionText };
}

