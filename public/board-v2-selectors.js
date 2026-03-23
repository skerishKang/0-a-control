function pickMainMission(state) {
  if (state.main_mission && typeof state.main_mission === "object") {
    return {
      title: state.main_mission.title || state.main_mission_title || "주 임무가 없습니다.",
      reason: state.main_mission.priority_reason || state.main_mission_reason || "오늘 우선순위로 올린 항목입니다.",
    };
  }

  return {
    title: state.main_mission_title || "주 임무가 없습니다.",
    reason: state.main_mission_reason || "오늘 우선순위로 올린 항목입니다.",
  };
}

function pickDueItems(state) {
  return state.due_items || state.dated_pressure_summary || [];
}

function pickUnfinishedItems(state) {
  return state.unfinished_items || state.top_unfinished_summary || [];
}

function pickCurrentQuest(state) {
  const quest = state.current_quest && typeof state.current_quest === "object" ? state.current_quest : {};
  return {
    id: state.current_quest_id || quest.id || "",
    title: state.current_quest_title || quest.title || "현재 퀘스트가 없습니다.",
    completionCriteria:
      state.current_quest_completion_criteria ||
      quest.completion_criteria ||
      "완료 기준을 아직 적지 않았습니다.",
    restartPoint: state.restart_point || quest.restart_point || "다시 시작할 지점이 아직 없습니다.",
  };
}

function pickRecentVerdict(state) {
  return state.recent_verdict && Object.keys(state.recent_verdict).length
    ? state.recent_verdict
    : state.latest_decision_summary || null;
}

function pickDoneItems(state) {
  return state.today_done_quests || [];
}

function pickBriefs(state) {
  if (Array.isArray(state.__briefs) && state.__briefs.length) {
    return state.__briefs;
  }
  if (state.latest_morning_brief && Object.keys(state.latest_morning_brief).length) {
    return [state.latest_morning_brief];
  }
  return [];
}

function pickSessions(state) {
  return Array.isArray(state.__sessions) ? state.__sessions : [];
}
