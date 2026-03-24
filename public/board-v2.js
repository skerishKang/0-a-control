async function loadBoardV2() {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  root.innerHTML = `<div class="v2-loading">데이터를 불러오는 중입니다...</div>`;

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
    root.innerHTML = `<div class="v2-loading">데이터 로드 실패</div>`;
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
  if (modal) modal.hidden = true;
};

document.addEventListener("DOMContentLoaded", loadBoardV2);
