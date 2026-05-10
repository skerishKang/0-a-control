// ── 전역 상태 ──
let _pollingInterval = null;

async function loadBoardV2() {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  // 초기 로드 시에만 로딩 메시지 표시 (폴링 시에는 기존 UI 유지)
  if (!root.querySelector(".v2-layout") && !root.querySelector(".v2-loading")) {
    root.innerHTML = `<div class="v2-loading">데이터를 불러오는 중입니다...</div>`;
  }

  try {
    const state = await boardApi.fetchFullState();

    // Load manual overrides (non-fatal, quiet failure allowed)
    try {
      state.__overrides = await boardApi.fetchOverrides();
    } catch (overrideErr) {
      console.warn("Manual overrides fetch failed, continuing without:", overrideErr);
      state.__overrides = [];
    }

    // Load ops panels non-fatally
    try {
      state.__operations = await boardApi.fetchOperationsSummary();
    } catch (opsErr) {
      console.warn("Operations summary fetch failed, continuing without:", opsErr);
      state.__operations = null;
    }

    try {
      state.__settings = await boardApi.fetchSettingsStatus();
    } catch (settingsErr) {
      console.warn("Settings status fetch failed, continuing without:", settingsErr);
      state.__settings = null;
    }

    try {
      state.__guardrails = await boardApi.fetchGuardrailsStatus();
    } catch (guardrailsErr) {
      console.warn("Guardrails status fetch failed, continuing without:", guardrailsErr);
      state.__guardrails = null;
    }

    _cachedState = state;
    const phase = getEffectivePhase(state);
    renderPhaseTabs(phase);
    renderStatusLabel(state, phase);
    dispatchRender(state, phase);
    injectOverridesSection(state.__overrides);
    injectHandoffSection();
    injectOpsSection(state.__operations);
    injectGuardrailsSection(state.__settings, state.__guardrails);
  } catch (error) {
    console.error("Failed to load board-v2 state:", error);
    // 에러 발생 시 UI가 아예 없으면 실패 메시지 표시
    if (!root.querySelector(".v2-layout")) {
      root.innerHTML = `<div class="v2-loading">데이터 로드 실패</div>`;
    }
  }
}

function startBoardV2Polling() {
  if (_pollingInterval) return;
  _pollingInterval = setInterval(() => {
    if (!isUserInteracting()) {
      loadBoardV2();
    }
  }, 30000); // 30초 간격
}

function isUserInteracting() {
  // 1. 상세 모달이 열려 있는지 확인
  const modal = document.getElementById("v2Modal");
  if (modal && !modal.hidden) return true;

  // 2. 결과 보고 폼 입력 중인지 확인
  const summary = document.getElementById("v2WorkSummary");
  if (summary) {
    const isFocused = document.activeElement === summary || document.activeElement?.id === "v2SelfAssessment";
    const hasContent = summary.value.trim().length > 0;
    if (isFocused || hasContent) return true;
  }

  // 3. 퀵 인풋 입력 중인지 확인
  const quickInput = document.getElementById("v2QuickInput");
  if (quickInput) {
    const isFocused = document.activeElement === quickInput;
    const hasContent = quickInput.value.trim().length > 0;
    if (isFocused || hasContent) return true;
  }

  // 4. 수동 오버라이드 생성 폼 입력 중인지 확인 (포커스 또는 미전송 내용)
  const overrideType = document.getElementById("v2OverrideTargetType");
  const overrideId = document.getElementById("v2OverrideTargetId");
  const overrideStatus = document.getElementById("v2OverrideManualStatus");
  const overrideReason = document.getElementById("v2OverrideReason");
  if (overrideType || overrideId || overrideStatus || overrideReason) {
    const isFocused =
      document.activeElement === overrideType ||
      document.activeElement === overrideId ||
      document.activeElement === overrideStatus ||
      document.activeElement === overrideReason;
    const hasContent =
      (overrideType && overrideType.value.trim().length > 0) ||
      (overrideId && overrideId.value.trim().length > 0) ||
      (overrideStatus && overrideStatus.value.trim().length > 0) ||
      (overrideReason && overrideReason.value.trim().length > 0);
    if (isFocused || hasContent) return true;
  }

  // 5. 실행자 핸드오프 패널 입력 중인지 확인
  const handoffSelect = document.getElementById("v2HandoffTaskType");
  const handoffPrompt = document.getElementById("v2HandoffPrompt");
  const handoffRepo = document.getElementById("v2HandoffRepo");
  const handoffIssue = document.getElementById("v2HandoffIssue");
  const handoffPR = document.getElementById("v2HandoffPR");
  const handoffBranch = document.getElementById("v2HandoffBranch");
  const handoffHead = document.getElementById("v2HandoffHead");
  const handoffTask = document.getElementById("v2HandoffTask");
  if (handoffSelect || handoffPrompt || handoffRepo || handoffIssue || handoffPR || handoffBranch || handoffHead || handoffTask) {
    const isFocused =
      document.activeElement === handoffSelect ||
      document.activeElement === handoffPrompt ||
      document.activeElement === handoffRepo ||
      document.activeElement === handoffIssue ||
      document.activeElement === handoffPR ||
      document.activeElement === handoffBranch ||
      document.activeElement === handoffHead ||
      document.activeElement === handoffTask;
    if (isFocused) return true;
    const hasContent =
      (handoffRepo && handoffRepo.value.trim().length > 0) ||
      (handoffIssue && handoffIssue.value.trim().length > 0) ||
      (handoffPR && handoffPR.value.trim().length > 0) ||
      (handoffBranch && handoffBranch.value.trim().length > 0) ||
      (handoffHead && handoffHead.value.trim().length > 0) ||
      (handoffTask && handoffTask.value.trim().length > 0);
    if (hasContent) return true;
  }

  return false;
}

function stopBoardV2Polling() {
  if (_pollingInterval) {
    clearInterval(_pollingInterval);
    _pollingInterval = null;
  }
}

window.boardV2PromoteStartingPoint = async function boardV2PromoteStartingPoint() {
  if (!window.confirm("이 약속으로 작업을 시작할까요?")) return;

  try {
    const response = await fetch("/api/tomorrow-first-quest/promote", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "작업 시작에 실패했습니다.");
    }
    _localPreviewPhase = null;
    await loadBoardV2();
    window.alert("확정한 시작점을 현재 퀘스트로 전환했습니다.");
  } catch (error) {
    console.error("Failed to promote starting point:", error);
    window.alert(`작업 시작 실패: ${error.message}`);
  }
};

window.boardV2ClearStartingPoint = async function boardV2ClearStartingPoint() {
  if (!window.confirm("확정된 시작점을 비울까요?")) return;

  try {
    const response = await fetch("/api/tomorrow-first-quest/clear", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "비우기에 실패했습니다.");
    }
    await loadBoardV2();
    window.alert("확정된 시작점을 비웠습니다.");
  } catch (error) {
    console.error("Failed to clear starting point:", error);
    window.alert(`비우기 실패: ${error.message}`);
  }
};

window.boardV2ConfirmStartingPoint = async function boardV2ConfirmStartingPoint(title, reason, source) {
  if (!window.confirm(`[${title}]을 내일의 첫 번째 퀘스트로 확정할까요?`)) return;

  try {
    const response = await fetch("/api/tomorrow-first-quest/confirm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, reason, source }),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "확정에 실패했습니다.");
    }
    await loadBoardV2();
    window.alert("내일의 첫 번째 퀘스트로 확정되었습니다.");
  } catch (error) {
    console.error("Failed to confirm starting point:", error);
    window.alert(`확정 실패: ${error.message}`);
  }
};

window.boardV2ReportQuest = async function boardV2ReportQuest(questId) {
  const summary = document.getElementById("v2WorkSummary")?.value.trim();
  const assessment = document.getElementById("v2SelfAssessment")?.value;

  if (!summary) {
    window.alert("작업 내용을 입력해 주세요.");
    return;
  }

  if (!window.confirm("작업 결과를 보고하고 AI 판정을 요청할까요?")) return;

  try {
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

    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "보고에 실패했습니다.");
    }

    await loadBoardV2();
    window.alert("보고가 완료되었습니다. AI 판정을 기다려 주세요.");
  } catch (error) {
    console.error("Failed to report quest:", error);
    window.alert(`보고 실패: ${error.message}`);
  }
};

window.boardV2StartQuestFromMission = async function boardV2StartQuestFromMission() {
  if (!window.confirm("오늘의 주 임무로 작업을 시작할까요?")) return;

  try {
    const response = await fetch("/api/current-quest/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "퀘스트 시작에 실패했습니다.");
    }
    await loadBoardV2();
    window.alert("보고가 완료되었습니다. AI 판정을 기다려 주세요.");
    // 제출 성공 후 초안 초기화
    _reportDraft.summary = "";
    _reportDraft.assessment = "partial";
    } catch (error) {
    console.error("Failed to report quest:", error);
    window.alert(`보고 실패: ${error.message}`);
    }
    };

    window.boardV2EvaluateQuest = async function boardV2EvaluateQuest(questId, verdict) {
      const label = { done: "완료", partial: "부분 완료", hold: "보류" }[verdict];
      if (!window.confirm(`현재 퀘스트를 [${label}] 상태로 직접 판정할까요?`)) return;

      try {
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

        const result = await response.json();
        if (!response.ok) {
          throw new Error(result.error || "판정 저장에 실패했습니다.");
        }

        await loadBoardV2();
        window.alert(`퀘스트가 [${label}] 상태로 종료되었습니다.`);
        // 제출 성공 후 초안 초기화
        _reportDraft.summary = "";
        _reportDraft.assessment = "partial";
      } catch (error) {
        console.error("Failed to evaluate quest:", error);
        window.alert(`판정 실패: ${error.message}`);
      }
    };

    window.boardV2DeferQuest = async function boardV2DeferQuest() {
      if (!window.confirm("현재 퀘스트를 오늘 목록에서 내리고 단기 플랜으로 미룰까요?")) return;

      try {
        const response = await fetch("/api/current-quest/defer", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        });
        const result = await response.json();
        if (!response.ok) {
          throw new Error(result.error || "미루기에 실패했습니다.");
        }
        await loadBoardV2();
        window.alert("퀘스트를 단기 플랜으로 이동했습니다.");
      } catch (error) {
        console.error("Failed to defer quest:", error);
        window.alert(`미루기 실패: ${error.message}`);
      }
    };

    window.boardV2SyncDraft = function boardV2SyncDraft() {
      const summaryEl = document.getElementById("v2WorkSummary");
      const assessmentEl = document.getElementById("v2SelfAssessment");
      if (summaryEl) _reportDraft.summary = summaryEl.value;
      if (assessmentEl) _reportDraft.assessment = assessmentEl.value;
    };

    window.boardV2SyncQuickInputDraft = function boardV2SyncQuickInputDraft() {
      const el = document.getElementById("v2QuickInput");
      if (el) _quickInputDraft = el.value;
    };

    window.boardV2SubmitQuickInput = async function boardV2SubmitQuickInput() {
      const text = _quickInputDraft.trim();
      if (!text) return;

      try {
        const response = await fetch("/api/bridge/quick-input", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        });
        const result = await response.json();
        if (!response.ok) {
          throw new Error(result.error || "입력 처리에 실패했습니다.");
        }

        _quickInputDraft = "";
        await loadBoardV2();
        window.alert("입력이 처리되었습니다.");
      } catch (error) {
        console.error("Failed to submit quick input:", error);
        window.alert(`입력 실패: ${error.message}`);
      }
    };

    window.boardV2OpenModal = function boardV2OpenModal(title, content) {
  const modal = document.getElementById("v2Modal");
  const titleEl = document.getElementById("v2ModalTitle");
  const bodyEl = document.getElementById("v2ModalBody");

  if (!modal || !titleEl || !bodyEl) return;

  titleEl.textContent = title;
  bodyEl.innerHTML = content;
  modal.hidden = false;
};

window.boardV2CloseModal = function boardV2CloseModal() {
  const modal = document.getElementById("v2Modal");
  if (modal) {
    modal.hidden = true;
    loadBoardV2(); // 모달을 닫는 즉시 최신 상태 반영
  }
};

window.boardV2OpenTextModal = function boardV2OpenTextModal(title, text) {
  const modal = document.getElementById("v2Modal");
  const titleEl = document.getElementById("v2ModalTitle");
  const bodyEl = document.getElementById("v2ModalBody");
  if (!modal || !titleEl || !bodyEl) return;

  titleEl.textContent = title;
  bodyEl.textContent = text;
  modal.hidden = false;
};

window.boardV2Refresh = async () => {
  await loadBoardV2();
};

window.boardV2ActionOverdueDone = async (id, title) => {
  // Mechanism: Send command like "done [title]" to natural language parser
  try {
    const text = `done ${title}`;
    const resp = await fetch('/api/bridge/quick-input', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    if (resp.ok) await window.boardV2Refresh();
  } catch (err) {
    console.error("Action Done failed:", err);
  }
};

window.boardV2ActionOverdueReschedule = async (id, title) => {
  // Move to today: "today [title]"
  try {
    const text = `today ${title}`;
    const resp = await fetch('/api/bridge/quick-input', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    if (resp.ok) await window.boardV2Refresh();
  } catch (err) {
    console.error("Action Reschedule failed:", err);
  }
};

window.boardV2ActionOverdueHold = async (id, title) => {
  // Move to hold: "hold [title]"
  try {
    const text = `hold ${title}`;
    const resp = await fetch('/api/bridge/quick-input', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    if (resp.ok) await window.boardV2Refresh();
  } catch (err) {
    console.error("Action Hold failed:", err);
  }
};

function startClock() {
  const clockEl = document.getElementById("v2Clock");
  if (!clockEl) return;

  function update() {
    const now = new Date();
    // Asia/Seoul formatting
    const dateStr = now.toLocaleDateString('ko-KR', { 
      timeZone: 'Asia/Seoul', 
      month: 'long', 
      day: 'numeric', 
      weekday: 'short' 
    });
    const timeStr = now.toLocaleTimeString('ko-KR', { 
      timeZone: 'Asia/Seoul', 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit',
      hour12: false 
    });
    clockEl.textContent = `${dateStr} ${timeStr}`;
  }

  console.log("Board V2 Clock started.");
  update();
  setInterval(update, 1000);
}

document.addEventListener("DOMContentLoaded", async () => {
  startClock();
  await loadBoardV2();
  startBoardV2Polling();
});

window.addEventListener("beforeunload", stopBoardV2Polling);

// ── Read-only Ops Panel ──
function renderOpsSection(data) {
  const section = document.createElement("section");
  section.className = "v2-rail-section";

  const label = document.createElement("span");
  label.className = "v2-section-label";
  label.textContent = "운영 요약";
  section.appendChild(label);

  const card = document.createElement("div");
  card.className = "v2-rail-card";

  if (!data) {
    const empty = document.createElement("p");
    empty.className = "v2-empty";
    empty.textContent = "운영 요약을 불러오지 못했습니다";
    card.appendChild(empty);
    section.appendChild(card);
    return section;
  }

  const list = document.createElement("ul");
  list.className = "v2-list v2-list-compact";

  const addRow = (fieldLabel, value) => {
    if (value === null || value === undefined) return;
    if (typeof value === "object") return;

    const li = document.createElement("li");
    li.className = "v2-list-item";

    const labelSpan = document.createElement("span");
    labelSpan.className = "v2-item-meta";
    labelSpan.textContent = fieldLabel + ":";

    const valueSpan = document.createElement("span");
    valueSpan.className = "v2-item-title";
    valueSpan.textContent = String(value);

    li.appendChild(labelSpan);
    li.appendChild(valueSpan);
    list.appendChild(li);
  };

  if (data.ok !== undefined) {
    addRow("OK", data.ok ? "예" : "아니오");
  }

  if (data.source_status) {
    if (typeof data.source_status === "object") {
      if (data.source_status.github !== undefined) {
        addRow("GitHub", String(data.source_status.github));
      }
      if (data.source_status.classifier !== undefined) {
        addRow("분류기", String(data.source_status.classifier));
      }
    }
  }

  if (data.counts && typeof data.counts === "object") {
    Object.entries(data.counts).forEach(([key, value]) => {
      if (value !== null && value !== undefined && !isNaN(Number(value))) {
        addRow(key.replace(/_/g, " "), Number(value));
      }
    });
  }

  if (data.open_issues && Array.isArray(data.open_issues)) {
    addRow("오픈 이슈", data.open_issues.length);
  }

  if (data.open_pull_requests && Array.isArray(data.open_pull_requests)) {
    addRow("오픈 PR", data.open_pull_requests.length);
  }

  if (data.recent_closed_pull_requests && Array.isArray(data.recent_closed_pull_requests)) {
    addRow("최근 닫힌 PR", data.recent_closed_pull_requests.length);
  }

  if (data.generated_at) {
    addRow("생성", new Date(data.generated_at).toLocaleString("ko-KR", { timeZone: "Asia/Seoul" }));
  }

  if (list.children.length === 0) {
    const empty = document.createElement("p");
    empty.className = "v2-empty";
    empty.textContent = "정보 없음";
    card.appendChild(empty);
  } else {
    card.appendChild(list);
  }

  section.appendChild(card);
  return section;
}

function injectOpsSection(data) {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const existing = document.getElementById("v2-ops-container");
  if (existing) existing.remove();

  const container = document.createElement("div");
  container.id = "v2-ops-container";
  container.appendChild(renderOpsSection(data));

  const layout = root.querySelector(".v2-layout");
  if (layout) {
    layout.appendChild(container);
    return;
  }

  root.appendChild(container);
}

// ── Read-only Settings/Guardrails Panel ──
function renderGuardrailsSection(settings, guardrails) {
  const section = document.createElement("section");
  section.className = "v2-rail-section";

  const label = document.createElement("span");
  label.className = "v2-section-label";
  label.textContent = "설정/가이드레일";
  section.appendChild(label);

  const card = document.createElement("div");
  card.className = "v2-rail-card";

  if (!settings && !guardrails) {
    const empty = document.createElement("p");
    empty.className = "v2-empty";
    empty.textContent = "설정·가이드레일 정보를 불러오지 못했습니다";
    card.appendChild(empty);
    section.appendChild(card);
    return section;
  }

  const list = document.createElement("ul");
  list.className = "v2-list v2-list-compact";

  const addRow = (fieldLabel, value) => {
    if (value === null || value === undefined) return;
    if (typeof value === "object") return;

    const li = document.createElement("li");
    li.className = "v2-list-item";

    const labelSpan = document.createElement("span");
    labelSpan.className = "v2-item-meta";
    labelSpan.textContent = fieldLabel + ":";

    const valueSpan = document.createElement("span");
    valueSpan.className = "v2-item-title";
    valueSpan.textContent = String(value);

    li.appendChild(labelSpan);
    li.appendChild(valueSpan);
    list.appendChild(li);
  };

  if (settings) {
    addRow("호스트", settings.host || "N/A");
    addRow("포트", settings.port);
    addRow("디버그", settings.debug_enabled ? "활성" : "비활성");
    addRow("Python", settings.python_version || "N/A");

    if (settings.telegram && typeof settings.telegram === "object") {
      addRow("Telegram", settings.telegram.configured ? "설정됨" : "미설정");
      addRow("TG API ID", settings.telegram.api_id_configured ? "예" : "아니오");
      addRow("TG API Hash", settings.telegram.api_hash_configured ? "예" : "아니오");
      addRow("TG 세션", settings.telegram.session_path_configured ? "있음" : "없음");
    }
  }

  if (guardrails) {
    addRow("적용 수준", guardrails.overall_level || "N/A");

    if (guardrails.checks && Array.isArray(guardrails.checks)) {
      addRow("체크 수", guardrails.checks.length);

      const levelCounts = {};
      guardrails.checks.forEach(check => {
        if (check.level) {
          levelCounts[check.level] = (levelCounts[check.level] || 0) + 1;
        }
      });
      Object.entries(levelCounts).forEach(([level, count]) => {
        addRow(`Level ${level}`, count + "개");
      });
    }
  }

  if (list.children.length === 0) {
    const empty = document.createElement("p");
    empty.className = "v2-empty";
    empty.textContent = "정보 없음";
    card.appendChild(empty);
  } else {
    card.appendChild(list);
  }

  section.appendChild(card);
  return section;
}

function injectGuardrailsSection(settings, guardrails) {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const existing = document.getElementById("v2-guardrails-container");
  if (existing) existing.remove();

  const container = document.createElement("div");
  container.id = "v2-guardrails-container";
  container.appendChild(renderGuardrailsSection(settings, guardrails));

  const layout = root.querySelector(".v2-layout");
  if (layout) {
    layout.appendChild(container);
    return;
  }

  root.appendChild(container);
}
