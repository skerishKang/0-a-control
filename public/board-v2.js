// ── 전역 상태 ──
let _pollingInterval = null;

/**
 * Render a small error indicator in the topbar when some board-v2 resources
 * failed to load. Shows a count badge; hover reveals per-resource details.
 * Removes itself when errors are cleared (no __errors or empty array).
 */
function renderErrorIndicator(errors) {
  const existing = document.getElementById("v2-error-indicator");
  if (existing) existing.remove();

  if (!errors || errors.length === 0) return;

  const el = document.createElement("span");
  el.id = "v2-error-indicator";
  el.style.cssText =
    "display:inline-flex;align-items:center;gap:3px;font-size:11px;font-weight:700;" +
    "color:#b91c1c;background:rgba(185,28,28,0.08);padding:2px 7px;border-radius:4px;" +
    "cursor:help;white-space:nowrap;";

  // Count badge
  const count = document.createElement("span");
  count.textContent = `⚠ ${errors.length}`;
  el.appendChild(count);

  // Tooltip on hover (title attribute for native tooltip)
  el.title = errors
    .map((e) => `[${e.resource}] ${e.message}`)
    .join("\n");

  // Insert after the status label inside the topbar center
  const center = document.querySelector(".v2-topbar-center");
  if (center) {
    // Place after v2StatusLabel to keep visual flow
    const statusLabel = document.getElementById("v2StatusLabel");
    if (statusLabel && statusLabel.nextSibling) {
      center.insertBefore(el, statusLabel.nextSibling);
    } else {
      center.appendChild(el);
    }
  }
}

async function loadBoardV2() {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  // 초기 로드 시에만 로딩 메시지 표시 (폴링 시에는 기존 UI 유지)
  if (!root.querySelector(".v2-layout") && !root.querySelector(".v2-loading")) {
    root.innerHTML = `<div class="v2-loading">데이터를 불러오는 중입니다...</div>`;
  }

  try {
    const state = await boardApi.fetchFullState();

    // Ensure __errors exists for optional-panel failures too
    if (!state.__errors) state.__errors = [];
    const _ts = new Date().toISOString();
    const _fail = (resource, message) => {
      state.__errors.push({ resource, message, timestamp: _ts });
    };

    renderErrorIndicator(state.__errors);

    // Load manual overrides (non-fatal, quiet failure allowed)
    try {
      state.__overrides = await boardApi.fetchOverrides();
    } catch (overrideErr) {
      console.warn("Manual overrides fetch failed, continuing without:", overrideErr);
      _fail('overrides', overrideErr.message);
      state.__overrides = [];
    }

    // Load ops panels non-fatally
    try {
      state.__operations = await boardApi.fetchOperationsSummary();
    } catch (opsErr) {
      console.warn("Operations summary fetch failed, continuing without:", opsErr);
      _fail('operations', opsErr.message);
      state.__operations = null;
    }

    try {
      state.__settings = await boardApi.fetchSettingsStatus();
    } catch (settingsErr) {
      console.warn("Settings status fetch failed, continuing without:", settingsErr);
      _fail('settings', settingsErr.message);
      state.__settings = null;
    }

    try {
      state.__guardrails = await boardApi.fetchGuardrailsStatus();
    } catch (guardrailsErr) {
      console.warn("Guardrails status fetch failed, continuing without:", guardrailsErr);
      _fail('guardrails', guardrailsErr.message);
      state.__guardrails = null;
    }

    // Load work queue non-fatally
    try {
      state.__workQueue = await boardApi.fetchWorkQueue();
    } catch (wqErr) {
      console.warn("Work queue fetch failed, continuing without:", wqErr);
      state.__workQueue = null;
    }

    // Load validation checklists non-fatally
    try {
      state.__validationChecklists = await fetchValidationChecklists();
    } catch (vcErr) {
      console.warn("Validation checklists fetch failed, continuing without:", vcErr);
      state.__validationChecklists = null;
    }

    _cachedState = state;
    const phase = getEffectivePhase(state);
    renderPhaseTabs(phase);
    renderStatusLabel(state, phase);
    dispatchRender(state, phase);
    injectOverridesSection(state.__overrides);
    injectHandoffSection();
    window.injectOpsSection(state.__operations);
    window.injectGuardrailsSection(state.__settings, state.__guardrails);
    window.injectWorkQueueSection(state.__workQueue);
    window.injectValidationChecklists(state.__validationChecklists);
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
    window.alert("오늘의 주 임무를 현재 퀘스트로 시작했습니다.");
    // 제출 성공 후 초안 초기화
    _reportDraft.summary = "";
    _reportDraft.assessment = "partial";
    } catch (error) {
    console.error("Failed to start quest from mission:", error);
    window.alert(`퀘스트 시작 실패: ${error.message}`);
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
  // Default to textContent for untrusted text content.
  // Pass { html: '...' } for intentional HTML rendering.
  if (content && typeof content === 'object' && content.html) {
    bodyEl.innerHTML = content.html;
  } else {
    bodyEl.textContent = String(content ?? '');
  }
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

// Safe model output display — uses textContent to prevent XSS
window.boardV2ShowModelOutput = function boardV2ShowModelOutput(title, formattedText) {
  const modal = document.getElementById("v2Modal");
  const titleEl = document.getElementById("v2ModalTitle");
  const bodyEl = document.getElementById("v2ModalBody");
  if (!modal || !titleEl || !bodyEl) return;

  titleEl.textContent = title;
  bodyEl.textContent = formattedText;
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

function setupBoardV2EventDelegation() {
  // Event delegation for data-v2-modal attributes and modal backdrop/close clicks.
  // This replaces inline onclick handlers with centralized handling.
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  // Click delegation for modal open via data attributes
  root.addEventListener("click", function (e) {
    const trigger = e.target.closest("[data-v2-modal]");
    if (trigger) {
      e.preventDefault();
      const title = trigger.getAttribute("data-v2-modal-title") || "";
      const content = trigger.getAttribute("data-v2-modal-content") || "";
      window.boardV2OpenModal(title, content);
      return;
    }
  });

  // Modal close: backdrop click or close button
  document.addEventListener("click", function (e) {
    if (e.target.classList.contains("v2-modal-backdrop") || e.target.closest(".v2-modal-close")) {
      window.boardV2CloseModal();
    }
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  startClock();
  await loadBoardV2();
  startBoardV2Polling();
  setupBoardV2EventDelegation();
});

window.addEventListener("beforeunload", stopBoardV2Polling);


