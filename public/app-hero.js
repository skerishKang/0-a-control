/**
 * Hero Card rendering module
 * Responsibility: UI rendering for the main mission and overall progress
 */

function renderHeroCard(current) {
  const statusSummary = current.quest_status_summary || {};
  
  // 1. Titles & Texts
  document.getElementById("mainMissionTitle").textContent = current.main_mission_title || "주 임무가 없습니다.";
  document.getElementById("mainMissionReason").textContent = summarizeMissionReason(current.main_mission_reason);
  document.getElementById("mainMissionCriteria").textContent =
    current.main_mission_completion_criteria || "완료 기준이 아직 없습니다.";
  document.getElementById("currentQuestTitle").textContent =
    current.current_quest_title || "현재 퀘스트가 없습니다.";

  // 2. Mission Status Badge
  const unfinished = current.top_unfinished_summary || [];
  const recentVerdict = current.recent_verdict || {};
  const latestVerdictStatus = recentVerdict.verdict || "";
  const missionSummary = unfinished.find((item) => item.title === current.main_mission_title) || unfinished[0] || null;
  const missionStatus = missionSummary?.status || latestVerdictStatus || "pending";
  
  const mainMissionStatus = document.getElementById("mainMissionStatus");
  if (mainMissionStatus) {
    let badges = renderVerdictBadge(missionStatus);
    if (statusSummary.is_pending && missionStatus !== 'pending') {
      badges += renderVerdictBadge("pending");
    }
    mainMissionStatus.innerHTML = badges;
  }

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
  const cautionText = missionRiskText({
    missionStatus,
    nextCore,
    currentQuestTitle: current.current_quest_title,
  });
  
  const mainMissionRisk = document.getElementById("mainMissionRisk");
  if (mainMissionRisk) {
    mainMissionRisk.textContent = cautionText;
  }

  // Return values for other cards to use (like Caution Card)
  return { nextCore, cautionText };
}
