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
    const [stateResponse, briefsResponse, sessionsResponse] = await Promise.all([
      fetch("/api/current-state"),
      fetch("/api/briefs/latest?limit=3"),
      fetch("/api/sessions/recent?limit=3"),
    ]);

    if (!stateResponse.ok) {
      throw new Error(`HTTP ${stateResponse.status}`);
    }

    const payload = await stateResponse.json();
    const state = payload.current_state || {};
    state.__briefs = briefsResponse.ok ? ((await briefsResponse.json()).briefs || []) : [];
    state.__sessions = sessionsResponse.ok ? ((await sessionsResponse.json()).sessions || []) : [];

    _cachedState = state;
    const phase = getEffectivePhase(state);
    renderPhaseTabs(phase);
    renderStatusLabel(phase);
    dispatchRender(state, phase);
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

document.addEventListener("DOMContentLoaded", async () => {
  await loadBoardV2();
  startBoardV2Polling();
});

window.addEventListener("beforeunload", stopBoardV2Polling);
