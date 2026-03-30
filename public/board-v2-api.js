// ── API Layer ──
// board-v2의 모든 서버 통신(fetch)을 전담합니다.

const boardApi = {
  async fetchFullState() {
    const [stateResponse, briefsResponse, sessionsResponse, questsResponse, plansResponse] = await Promise.all([
      fetch("/api/current-state"),
      fetch("/api/briefs/latest?limit=3"),
      fetch("/api/sessions/recent?limit=50"),
      fetch("/api/quests"),
      fetch("/api/plans"),
    ]);

    if (!stateResponse.ok) {
      throw new Error(`HTTP ${stateResponse.status}`);
    }

    const payload = await stateResponse.json();
    const state = payload.current_state || {};
    state.__briefs = briefsResponse.ok ? ((await briefsResponse.json()).briefs || []) : [];
    state.__sessions = sessionsResponse.ok ? ((await sessionsResponse.json()).sessions || []) : [];
    state.__quests = questsResponse.ok ? ((await questsResponse.json()).quests || []) : [];
    state.__plans = plansResponse.ok ? ((await plansResponse.json()).plans || []) : [];

    return state;
  },

  async promoteStartingPoint() {
    const response = await fetch("/api/tomorrow-first-quest/promote", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    return this._handleResponse(response, "작업 시작에 실패했습니다.");
  },

  async clearStartingPoint() {
    const response = await fetch("/api/tomorrow-first-quest/clear", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    return this._handleResponse(response, "비우기에 실패했습니다.");
  },

  async confirmStartingPoint(title, reason, source) {
    const response = await fetch("/api/tomorrow-first-quest/confirm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, reason, source }),
    });
    return this._handleResponse(response, "확정에 실패했습니다.");
  },

  async reportQuest(questId, summary, assessment) {
    const response = await fetch("/api/quests/report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        quest_id: questId,
        work_summary: summary,
        self_assessment: assessment,
        remaining_work: "",
        blocker: "",
      }),
    });
    return this._handleResponse(response, "보고에 실패했습니다.");
  },

  async startQuestFromMission() {
    const response = await fetch("/api/current-quest/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    return this._handleResponse(response, "퀘스트 시작에 실패했습니다.");
  },

  async evaluateQuest(questId, verdict) {
    const response = await fetch("/api/quests/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        quest_id: questId,
        verdict: verdict,
        reason: "사용자 수동 판정",
        restart_point: "",
        next_quest_hint: "",
        plan_impact: "",
      }),
    });
    return this._handleResponse(response, "판정 저장에 실패했습니다.");
  },

  async deferQuest() {
    const response = await fetch("/api/current-quest/defer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    return this._handleResponse(response, "미루기에 실패했습니다.");
  },

  async submitQuickInput(text) {
    const response = await fetch("/api/bridge/quick-input", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    return this._handleResponse(response, "입력 처리에 실패했습니다.");
  },

  async fetchWorkfileMapping() {
    const response = await fetch('/작업철/_mapping.json');
    if (response.ok) {
        return await response.json();
    }
    return null;
  },

  async fetchWorkfileContent(path) {
    const response = await fetch('/' + encodeURI(path));
    if (!response.ok) {
        throw new Error("File not found");
    }
    return await response.text();
  },

  async _handleResponse(response, defaultErrorMsg) {
    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(result.error || defaultErrorMsg);
    }
    return result;
  }
};
