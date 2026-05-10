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

    _cachedState = state;
    const phase = getEffectivePhase(state);
    renderPhaseTabs(phase);
    renderStatusLabel(state, phase);
    dispatchRender(state, phase);
    injectOverridesSection(state.__overrides);
    injectHandoffSection();
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

// ── Manual Overrides UI (read-only) ──
function renderOverridesSection(overrides) {
  const section = document.createElement("section");
  section.className = "v2-rail-section";

  const label = document.createElement("span");
  label.className = "v2-section-label";
  label.textContent = "수동 오버라이드";
  section.appendChild(label);

  const card = document.createElement("div");
  card.className = "v2-rail-card";

  // Create form for manual override
  const form = document.createElement("form");
  form.className = "v2-override-form";

  const typeSelect = document.createElement("select");
  typeSelect.id = "v2OverrideTargetType";
  typeSelect.className = "v2-override-select";
  typeSelect.setAttribute("aria-label", "타입 선택");
  const typeOptions = ["", "issue", "pr", "quest", "plan", "session", "source", "global"];
  typeOptions.forEach((opt) => {
    const option = document.createElement("option");
    option.value = opt;
    option.textContent = opt || "타입 선택";
    typeSelect.appendChild(option);
  });

  const idInput = document.createElement("input");
  idInput.type = "text";
  idInput.id = "v2OverrideTargetId";
  idInput.className = "v2-override-input";
  idInput.setAttribute("placeholder", "대상ID");
  idInput.setAttribute("maxlength", "50");

  const statusSelect = document.createElement("select");
  statusSelect.id = "v2OverrideManualStatus";
  statusSelect.className = "v2-override-select";
  statusSelect.setAttribute("aria-label", "상태");
  const statusOptions = ["", "READY", "IN_PROGRESS", "BLOCKED", "NEEDS_IMPLEMENTATION", "NEEDS_REVIEW", "NEEDS_VALIDATION", "DONE", "NO_ACTION", "PINNED", "WATCH", "IGNORE_UNTIL", "DO_NOT_MERGE", "DO_NOT_CLOSE"];
  statusOptions.forEach((opt) => {
    const option = document.createElement("option");
    option.value = opt;
    option.textContent = opt || "상태 선택";
    statusSelect.appendChild(option);
  });

  const reasonInput = document.createElement("input");
  reasonInput.type = "text";
  reasonInput.id = "v2OverrideReason";
  reasonInput.className = "v2-override-input";
  reasonInput.setAttribute("placeholder", "사유");
  reasonInput.setAttribute("maxlength", "200");

  const submitBtn = document.createElement("button");
  submitBtn.type = "submit";
  submitBtn.className = "v2-btn v2-btn-inline";
  submitBtn.textContent = "추가";

  form.appendChild(typeSelect);
  form.appendChild(idInput);
  form.appendChild(statusSelect);
  form.appendChild(reasonInput);
  form.appendChild(submitBtn);

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const target_type = typeSelect.value.trim();
    const target_id = idInput.value.trim();
    const manual_status = statusSelect.value.trim();
    const reason = reasonInput.value.trim();

    if (!target_type) {
      window.alert("타입을 선택해 주세요.");
      return;
    }
    if (!target_id) {
      window.alert("대상ID를 입력해 주세요.");
      return;
    }
    if (!manual_status) {
      window.alert("상태를 선택해 주세요.");
      return;
    }
    if (!reason) {
      window.alert("사유를 입력해 주세요.");
      return;
    }

    try {
      await boardApi.createOverride({ target_type, target_id, manual_status, reason });
      typeSelect.value = "";
      idInput.value = "";
      statusSelect.value = "";
      reasonInput.value = "";
      const root = document.getElementById("boardV2Root");
      if (root) {
        const state = await boardApi.fetchFullState();
        state.__overrides = await boardApi.fetchOverrides();
        _cachedState = state;
        injectOverridesSection(state.__overrides);
      }
    } catch (err) {
      window.alert("생성 중 오류가 발생했습니다.");
    }
  });

  card.appendChild(form);

  if (!overrides || overrides.length === 0) {
    const empty = document.createElement("p");
    empty.className = "v2-empty";
    empty.textContent = "수동 오버라이드가 없습니다.";
    card.appendChild(empty);
  } else {
    const list = document.createElement("ul");
    list.className = "v2-list";

    overrides.forEach((ov) => {
      const li = document.createElement("li");
      li.className = "v2-list-item";

      const contentDiv = document.createElement("div");
      contentDiv.className = "v2-override-row";

      const titleSpan = document.createElement("span");
      titleSpan.className = "v2-override-title";
      const overrideLabel =
        [ov.manual_status, [ov.target_type, ov.target_id].filter(Boolean).join("/")].filter(Boolean).join(" · ") ||
        ov.title ||
        "오버라이드";
      titleSpan.textContent = overrideLabel;

      const active = ov.is_active !== false;
      const badge = document.createElement("span");
      badge.className = active ? "v2-status-badge -auto" : "v2-status-badge";
      badge.textContent = active ? "활성" : "비활성";

      contentDiv.appendChild(titleSpan);
      contentDiv.appendChild(badge);

      if (active) {
        const deactivateBtn = document.createElement("button");
        deactivateBtn.type = "button";
        deactivateBtn.className = "v2-btn v2-btn-inline v2-btn-deactivate";
        deactivateBtn.textContent = "비활성화";
        deactivateBtn.addEventListener("click", async (e) => {
          e.stopPropagation();
          if (!window.confirm("이 오버라이드를 비활성화할까요?")) return;
          try {
            await boardApi.deactivateOverride(ov.id);
            const root = document.getElementById("boardV2Root");
            if (root) {
              const state = await boardApi.fetchFullState();
              state.__overrides = await boardApi.fetchOverrides();
              _cachedState = state;
              injectOverridesSection(state.__overrides);
            }
          } catch (err) {
            window.alert("오버라이드 비활성화에 실패했습니다.");
          }
        });
        contentDiv.appendChild(deactivateBtn);
      }

      li.appendChild(contentDiv);

      if (ov.reason) {
        const reasonSpan = document.createElement("span");
        reasonSpan.className = "v2-item-meta";
        reasonSpan.textContent = ov.reason;
        li.appendChild(reasonSpan);
      }

      if (ov.reason || ov.description || ov.impact_summary) {
        li.classList.add("v2-modal-clickable");
        li.addEventListener("click", (function(overrideTitle, overrideText) {
          return function() {
            window.boardV2OpenTextModal(overrideTitle, overrideText);
          };
        })(overrideLabel, ov.description || ov.reason || ov.impact_summary || ""));
      }

      list.appendChild(li);
    });

    card.appendChild(list);
  }

  section.appendChild(card);
  return section;
}

function injectOverridesSection(overrides) {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const layout = root.querySelector(".v2-layout");
  if (!layout) return;

  const existing = document.getElementById("v2-overrides-container");
  if (existing) existing.remove();

  const container = document.createElement("div");
  container.id = "v2-overrides-container";
  container.appendChild(renderOverridesSection(overrides));
  layout.appendChild(container);
}

// ── Executor Handoff Panel ──
const HANDOFF_SAFETY_RULES = [
  "main 직접 수정/push 금지",
  "PR merge 금지 unless explicitly instructed",
  "issue close 금지 unless explicitly instructed",
  "secret/token/session/private data/raw runtime payload 출력 금지",
  "runtime data stage 금지",
  "tests/__init__.py 추가 금지",
  "python scripts/server.py 직접 foreground 실행 금지",
  "use python scripts/smoke_server.py for smoke validation",
  "broad codebase exploration 금지",
  "line-ending/full-file rewrite churn 금지"
];

const TASK_SPECIFIC = {
  "Local Code Executor": [
    "branch creation/update",
    "code changes allowed only within scope",
    "CLI validation required",
    "no python scripts/server.py foreground",
    "no runtime data stage",
    "targeted diff only"
  ],
  "Browser QA Executor": [
    "URL tested",
    "source branch/HEAD confirmation",
    "no code changes",
    "screenshot redaction if needed",
    "console/network safety checks",
    "report PASS/HOLD/NOT_RUN"
  ],
  "GitHub Ops Executor": [
    "issue/PR metadata actions only",
    "no code changes",
    "no merge/issue close unless explicitly instructed",
    "verify repo and issue/PR number before mutation",
    "report URLs and blocked actions"
  ],
  "Long-running Local Loop Executor": [
    "repeat same PR fixes only",
    "max loop limit: 3 cycles",
    "stop conditions:",
    "  - validation failure not obvious",
    "  - scope expansion",
    "  - server/storage changes needed",
    "  - full-file churn",
    "  - runtime data staged",
    "report after each cycle"
  ],
  "Diff Cleanup Executor": [
    "no feature expansion",
    "restore line endings/formatting",
    "reduce full-file replacement to targeted hunks",
    "preserve existing functional fixes",
    "validate diff before commit"
  ]
};

function getHandoffPrompt(taskType, context) {
  const header = `[CTO → ${taskType}] 실행자 핸드오프 프롬프트`;
  const safety = HANDOFF_SAFETY_RULES.map(r => `- ${r}`).join("\n");
  const taskSpec = (TASK_SPECIFIC[taskType] || []).map(r => `- ${r}`).join("\n");
  const reportTemplate = `Report:
- Branch:
- PR URL:
- HEAD SHA:
- Changed files:
- Implementation summary:
- Prompt types included:
- Copy behavior:
- Diff targeted, no full-file churn: YES/NO
- Validation results:
- Runtime data staged: NO/YES
- Browser verification: PASS/NOT_RUN/FAIL
- Final recommendation:
  - PASS → CTO review
  - HOLD → sanitized blocker`;

  const contextParts = [];
  if (context.repo) contextParts.push(`- Repo: ${context.repo}`);
  if (context.issueNumber) contextParts.push(`- Issue: #${context.issueNumber}`);
  if (context.prNumber) contextParts.push(`- PR: #${context.prNumber}`);
  if (context.branch) contextParts.push(`- Branch: ${context.branch}`);
  if (context.expectedHead) contextParts.push(`- Expected HEAD: ${context.expectedHead}`);
  if (context.taskName) contextParts.push(`- Task: ${context.taskName}`);

  const contextBlock = contextParts.length > 0 ? `\n\n- Context:\n${contextParts.join("\n")}` : "";

  return taskSpec
    ? `${header}${contextBlock}\n\n- Safety rules:\n${safety}\n\n- Task-specific:\n${taskSpec}\n\n${reportTemplate}`
    : `${header}${contextBlock}\n\n${safety}\n\n${reportTemplate}`;
}

function renderHandoffSection() {
  const section = document.createElement("section");
  section.className = "v2-rail-section";

  const label = document.createElement("span");
  label.className = "v2-section-label";
  label.textContent = "실행자 핸드오프";
  section.appendChild(label);

  const card = document.createElement("div");
  card.className = "v2-rail-card";

  // Task type selector
  const select = document.createElement("select");
  select.id = "v2HandoffTaskType";
  select.className = "v2-override-select";
  const taskTypes = [
    "Local Code Executor",
    "Browser QA Executor",
    "GitHub Ops Executor",
    "Long-running Local Loop Executor",
    "Diff Cleanup Executor"
  ];
  taskTypes.forEach(tt => {
    const option = document.createElement("option");
    option.value = tt;
    option.textContent = tt;
    select.appendChild(option);
  });

  // Context fields
  const ctxRepo = document.createElement("input");
  ctxRepo.type = "text";
  ctxRepo.id = "v2HandoffRepo";
  ctxRepo.className = "v2-override-input";
  ctxRepo.setAttribute("placeholder", "Repo (e.g. owner/repo)");
  ctxRepo.setAttribute("maxlength", "100");

  const ctxIssue = document.createElement("input");
  ctxIssue.type = "text";
  ctxIssue.id = "v2HandoffIssue";
  ctxIssue.className = "v2-override-input";
  ctxIssue.setAttribute("placeholder", "Issue #");
  ctxIssue.setAttribute("maxlength", "20");

  const ctxPR = document.createElement("input");
  ctxPR.type = "text";
  ctxPR.id = "v2HandoffPR";
  ctxPR.className = "v2-override-input";
  ctxPR.setAttribute("placeholder", "PR #");
  ctxPR.setAttribute("maxlength", "20");

  const ctxBranch = document.createElement("input");
  ctxBranch.type = "text";
  ctxBranch.id = "v2HandoffBranch";
  ctxBranch.className = "v2-override-input";
  ctxBranch.setAttribute("placeholder", "Branch");
  ctxBranch.setAttribute("maxlength", "100");

  const ctxHead = document.createElement("input");
  ctxHead.type = "text";
  ctxHead.id = "v2HandoffHead";
  ctxHead.className = "v2-override-input";
  ctxHead.setAttribute("placeholder", "Expected HEAD SHA");
  ctxHead.setAttribute("maxlength", "40");

  const ctxTask = document.createElement("input");
  ctxTask.type = "text";
  ctxTask.id = "v2HandoffTask";
  ctxTask.className = "v2-override-input";
  ctxTask.setAttribute("placeholder", "Task name");
  ctxTask.setAttribute("maxlength", "200");

  // Prompt output
  const output = document.createElement("textarea");
  output.id = "v2HandoffPrompt";
  output.className = "v2-textarea v2-handoff-prompt";
  output.rows = 8;
  output.readOnly = true;
  output.value = getHandoffPrompt(taskTypes[0], {});

  // Copy button row
  const copyRow = document.createElement("div");
  copyRow.className = "v2-handoff-copy-row";

  const copyBtn = document.createElement("button");
  copyBtn.type = "button";
  copyBtn.className = "v2-btn v2-btn-secondary v2-btn-inline";
  copyBtn.textContent = "복사";

  const copyFeedback = document.createElement("span");
  copyFeedback.id = "v2HandoffFeedback";
  copyFeedback.className = "v2-handoff-feedback";
  copyFeedback.textContent = "";

  // Helper to get current context
  function getCurrentContext() {
    return {
      repo: ctxRepo.value.trim(),
      issueNumber: ctxIssue.value.trim(),
      prNumber: ctxPR.value.trim(),
      branch: ctxBranch.value.trim(),
      expectedHead: ctxHead.value.trim(),
      taskName: ctxTask.value.trim()
    };
  }

  // Helper to update prompt
  function updatePrompt() {
    output.value = getHandoffPrompt(select.value, getCurrentContext());
    copyFeedback.textContent = "";
  }

  // Event handlers
  select.addEventListener("change", updatePrompt);

  ctxRepo.addEventListener("input", updatePrompt);
  ctxIssue.addEventListener("input", updatePrompt);
  ctxPR.addEventListener("input", updatePrompt);
  ctxBranch.addEventListener("input", updatePrompt);
  ctxHead.addEventListener("input", updatePrompt);
  ctxTask.addEventListener("input", updatePrompt);

  copyBtn.addEventListener("click", async () => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(output.value);
        copyFeedback.textContent = "복사됨";
      } else {
        output.select();
        document.execCommand("copy");
        copyFeedback.textContent = "복사됨";
      }
      setTimeout(() => { copyFeedback.textContent = ""; }, 2000);
    } catch (e) {
      output.select();
      copyFeedback.textContent = "수동으로 복사해주세요";
    }
  });

  copyRow.appendChild(copyBtn);
  copyRow.appendChild(copyFeedback);

  card.appendChild(select);
  card.appendChild(ctxRepo);
  card.appendChild(ctxIssue);
  card.appendChild(ctxPR);
  card.appendChild(ctxBranch);
  card.appendChild(ctxHead);
  card.appendChild(ctxTask);
  card.appendChild(output);
  card.appendChild(copyRow);

  section.appendChild(card);
  return section;
}

function injectHandoffSection() {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const existing = document.getElementById("v2-handoff-container");
  if (existing) existing.remove();

  const container = document.createElement("div");
  container.id = "v2-handoff-container";
  container.appendChild(renderHandoffSection());

  const layout = root.querySelector(".v2-layout");
  if (layout) {
    layout.appendChild(container);
    return;
  }

  root.appendChild(container);
}
