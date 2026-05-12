// ── API Layer ──
// board-v2의 모든 서버 통신(fetch)을 전담합니다.
//
// Error convention (board-v2 API):
// 1. fetchFullState() never throws for individual resource failures.
//    Instead, it collects per-resource errors into state.__errors.
//    Each entry: { resource: string, message: string, timestamp: string }.
//    Failed resources still get an empty array/null so the UI can render
//    partial data. This is "partial-load reporting".
// 2. Optional-panel methods (fetchOperationsSummary, fetchSettingsStatus,
//    fetchGuardrailsStatus) return null on failure. Consumers check for
//    null to show "데이터를 불러오지 못했습니다" — this is the documented
//    null/error convention for optional panels.

const boardApi = {
  async fetchFullState() {
    const _errors = [];
    const _ts = new Date().toISOString();
    const _fail = (resource, message) => {
      _errors.push({ resource, message, timestamp: _ts });
    };

    // Internal helper: resolve a fetch Response into the expected array,
    // recording an error on failure and returning [] as safe fallback.
    const _resolveResource = async (response, resourceName) => {
      if (!response.ok) {
        _fail(resourceName, `HTTP ${response.status}`);
        return [];
      }
      try {
        const json = await response.json();
        return json[resourceName] || [];
      } catch (e) {
        _fail(resourceName, `JSON parse error: ${e.message}`);
        return [];
      }
    };

    const [stateResponse, briefsResponse, sessionsResponse, questsResponse, plansResponse] = await Promise.all([
      fetch("/api/current-state"),
      fetch("/api/briefs/latest?limit=3"),
      fetch("/api/sessions/recent?limit=50"),
      fetch("/api/quests"),
      fetch("/api/plans"),
    ]);

    // Process current state (non-fatal now — records error instead of throwing)
    let state = {};
    if (!stateResponse.ok) {
      _fail('current_state', `HTTP ${stateResponse.status}`);
    } else {
      try {
        const payload = await stateResponse.json();
        state = payload.current_state || {};
      } catch (e) {
        _fail('current_state', `JSON parse error: ${e.message}`);
      }
    }

    state.__briefs = await _resolveResource(briefsResponse, 'briefs');
    state.__sessions = await _resolveResource(sessionsResponse, 'sessions');
    state.__quests = await _resolveResource(questsResponse, 'quests');
    state.__plans = await _resolveResource(plansResponse, 'plans');

    if (_errors.length > 0) {
      state.__errors = _errors;
    }

    return state;
  },

  async fetchOverrides() {
    const response = await fetch("/api/ops-overrides");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const payload = await response.json();
    return payload.overrides || [];
  },

  async createOverride(data) {
    const response = await fetch("/api/ops-overrides", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return this._handleResponse(response, "오버라이드 생성에 실패했습니다.");
  },

  async deactivateOverride(id) {
    const response = await fetch(`/api/ops-overrides/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ is_active: false }),
    });
    return this._handleResponse(response, "오버라이드 비활성화에 실패했습니다.");
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

  async fetchOperationsSummary() {
    try {
      const response = await fetch("/api/operations/summary");
      if (!response.ok) {
        return null;
      }
      return await response.json();
    } catch (err) {
      console.warn("Operations summary fetch failed:", err);
      return null;
    }
  },

  async fetchSettingsStatus() {
    try {
      const response = await fetch("/api/settings/status");
      if (!response.ok) {
        return null;
      }
      return await response.json();
    } catch (err) {
      console.warn("Settings status fetch failed:", err);
      return null;
    }
  },

  async fetchGuardrailsStatus() {
    try {
      const response = await fetch("/api/guardrails/status");
      if (!response.ok) {
        return null;
      }
      return await response.json();
    } catch (err) {
      console.warn("Guardrails status fetch failed:", err);
      return null;
    }
  },

  async fetchWorkQueue() {
    try {
      const response = await fetch("/api/work-queue");
      if (!response.ok) {
        return null;
      }
      return await response.json();
    } catch (err) {
      console.warn("Work queue fetch failed:", err);
      return null;
    }
  },

  async _handleResponse(response, defaultErrorMsg) {
    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(result.error || defaultErrorMsg);
    }
    return result;
  }
};
