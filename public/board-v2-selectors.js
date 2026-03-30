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
  // Try state.current_quest first
  const quest = state.current_quest && typeof state.current_quest === "object" ? state.current_quest : {};
  const id = state.current_quest_id || quest.id || "";
  const title = state.current_quest_title || quest.title || "";
  
  // Fallback: find active quest from __quests if current_quest_id is empty
  if (!id && Array.isArray(state.__quests)) {
    const active = state.__quests.find(q => q.status === "active" || q.status === "in_progress");
    if (active) {
      return {
        id: active.id || "",
        title: active.title || "현재 퀘스트가 없습니다.",
        whyNow: active.why_now || "",
        parentTitle: active.parent_title || "",
        completionCriteria: active.completion_criteria || "완료 기준을 아직 적지 않았습니다.",
        restartPoint: active.restart_point || "",
      };
    }
  }

  return {
    id: id,
    title: title || "현재 퀘스트가 없습니다.",
    whyNow: quest.why_now || "",
    parentTitle: quest.parent_title || "",
    completionCriteria:
      state.current_quest_completion_criteria ||
      quest.completion_criteria ||
      "완료 기준을 아직 적지 않았습니다.",
    restartPoint: state.restart_point || quest.restart_point || "",
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
  return Array.isArray(state.__sessions) ? state.__sessions.slice(0, 3) : [];
}

function pickUrgentUpcoming(state) {
  const allDue = pickDueItems(state);
  const nowStr = new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Seoul' });
  
  return allDue.filter(item => {
    if (!item.due_at) return true;
    const itemDate = item.due_at.split('T')[0];
    return itemDate >= nowStr;
  });
}

function pickOverdue(state) {
  const allDue = pickDueItems(state);
  const nowStr = new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Seoul' });
  
  return allDue.filter(item => {
    if (!item.due_at) return false;
    const itemDate = item.due_at.split('T')[0];
    return itemDate < nowStr;
  });
}

function pickCompletedItems(state) {
  const allQuests = state.__quests || [];
  const allSessions = Array.isArray(state.__sessions) ? state.__sessions : [];
  const allPlans = state.__plans || [];
  const todayDoneQuestsRaw = state.today_done_quests || [];

  const tasks = [];
  const logs = [];

  const questIdsInCompleted = new Set();
  const planIdsInCompleted = new Set();

  // 1. Quests from __quests
  allQuests.forEach(q => {
    if (q.status === 'done' || q.status === 'partial') {
      questIdsInCompleted.add(q.id);
      if (q.plan_item_id) planIdsInCompleted.add(q.plan_item_id);
      
      let subtextVal = q.why_now || q.parent_title || "";
      if (!subtextVal && q.completion_criteria) {
        subtextVal = q.completion_criteria.length > 28 ? q.completion_criteria.slice(0, 28) + "..." : q.completion_criteria;
      }

      tasks.push({
        id: `q-${q.id}`,
        title: q.title,
        completedAt: q.updated_at,
        type: 'Quest',
        verdict: q.status,
        priority: q.status === 'done' ? 10 : 30, // 10: Done Quest, 30: Partial
        description: q.verdict_reason || q.reason || q.completion_criteria || "상세 내용 없음",
        subtext: subtextVal
      });
    }
  });

  // 2. Plan Items from __plans (that are NOT already represented by a quest)
  allPlans.forEach(p => {
    if ((p.status === 'done' || p.status === 'completed') && !planIdsInCompleted.has(p.id)) {
      tasks.push({
        id: `p-${p.id}`,
        title: p.title,
        completedAt: p.updated_at || p.created_at,
        type: 'Plan',
        verdict: 'done',
        priority: 20, // 20: Done Plan Item
        description: p.description || p.priority_reason || "플랜 항목 완료",
        subtext: p.project_key ? `[${p.project_key}] Plan Item` : "Plan Item"
      });
    }
  });

  // 3. Fallback to today_done_quests (Raw)
  todayDoneQuestsRaw.forEach(q => {
    if (!questIdsInCompleted.has(q.id)) {
      tasks.push({
        id: `q-raw-${q.id}`,
        title: q.title,
        completedAt: q.done_at || q.updated_at || new Date().toISOString(),
        type: 'Quest',
        verdict: 'done',
        priority: 10,
        description: q.summary || "상세 내용 없음",
        subtext: "Today's Done List"
      });
    }
  });

  // 4. Sessions
  allSessions.forEach(s => {
    const hasVerdict = s.quest_verdict_status === 'done' || s.quest_verdict_status === 'partial';
    const isClosed = s.status === 'closed';
    const hasSummary = Boolean(s.summary_md);

    if (hasVerdict) {
      let sessionProject = s.project_key || "";
      if (/^[a-fA-F0-9-]{12,}$/.test(sessionProject) || sessionProject.startsWith('p-')) {
        sessionProject = "";
      }
      let subtextVal = (sessionProject && s.agent_name) ? `[${sessionProject}] ${s.agent_name}` : (sessionProject || s.agent_name || "");

      tasks.push({
        id: `s-${s.id}`,
        title: s.title || s.project_key || '세션',
        completedAt: s.ended_at || s.updated_at || s.started_at,
        type: 'Session',
        verdict: s.quest_verdict_status,
        priority: s.quest_verdict_status === 'done' ? 15 : 35, // Session versions of tasks
        description: s.summary_md || `Agent: ${s.agent_name || 'unknown'}`,
        subtext: subtextVal
      });
    } else if (isClosed && hasSummary) {
      let sessionProject = s.project_key || "";
      if (/^[a-fA-F0-9-]{12,}$/.test(sessionProject) || sessionProject.startsWith('p-')) {
        sessionProject = "";
      }
      let subtextVal = (sessionProject && s.agent_name) ? `[${sessionProject}] ${s.agent_name}` : (sessionProject || s.agent_name || "");

      logs.push({
        id: `log-${s.id}`,
        title: s.title || s.project_key || '세션 로그',
        completedAt: s.ended_at || s.updated_at || s.started_at,
        type: 'Log',
        verdict: 'done',
        priority: 100, // 100: Logs (last)
        description: s.summary_md || `Agent: ${s.agent_name || 'unknown'}`,
        subtext: `(기록) ${subtextVal}`,
        isLog: true
      });
    }
  });

  // Sort and Partition
  // Primary: Priority (ascending), Secondary: Date (descending)
  const masterSort = (a, b) => {
    if (a.priority !== b.priority) return a.priority - b.priority;
    return new Date(b.completedAt) - new Date(a.completedAt);
  };
  
  tasks.sort(masterSort);
  logs.sort(masterSort);

  const formatter = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Seoul', year: 'numeric', month: '2-digit', day: '2-digit' });
  const nowStr = formatter.format(new Date());

  const partitionItems = (items) => {
    const today = [];
    const recent = [];
    items.forEach(item => {
      let itemDateStr = '';
      if (item.completedAt) {
        const d = new Date(item.completedAt);
        if (!isNaN(d)) itemDateStr = formatter.format(d);
      }
      if (itemDateStr === nowStr) today.push(item);
      else recent.push(item);
    });
    return { today, recent };
  };

  const tasksP = partitionItems(tasks);
  const logsP = partitionItems(logs);

  return {
    todayTasks: tasksP.today,
    recentTasks: tasksP.recent.slice(0, 15),
    todayLogs: logsP.today,
    recentLogs: logsP.recent.slice(0, 15),
    allTasks: tasks,
    allLogs: logs
  };
}
