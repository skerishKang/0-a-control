// ── Action Layer ──
// 사용자 UI 상호작용(버튼 클릭 등) 이벤트와 비즈니스 흐름을 담당합니다.

window.boardV2PromoteStartingPoint = async function () {
  if (!window.confirm("이 약속으로 작업을 시작할까요?")) return;

  try {
    await boardApi.promoteStartingPoint();
    _localPreviewPhase = null;
    await loadBoardV2();
    window.alert("확정한 시작점을 현재 퀘스트로 전환했습니다.");
  } catch (error) {
    console.error("Failed to promote starting point:", error);
    window.alert(`작업 시작 실패: ${error.message}`);
  }
};

window.boardV2ClearStartingPoint = async function () {
  if (!window.confirm("확정된 시작점을 비울까요?")) return;

  try {
    await boardApi.clearStartingPoint();
    await loadBoardV2();
    window.alert("확정된 시작점을 비웠습니다.");
  } catch (error) {
    console.error("Failed to clear starting point:", error);
    window.alert(`비우기 실패: ${error.message}`);
  }
};

window.boardV2ConfirmStartingPoint = async function (title, reason, source) {
  if (!window.confirm(`[${title}]을 내일의 첫 번째 퀘스트로 확정할까요?`)) return;

  try {
    await boardApi.confirmStartingPoint(title, reason, source);
    await loadBoardV2();
    window.alert("내일의 첫 번째 퀘스트로 확정되었습니다.");
  } catch (error) {
    console.error("Failed to confirm starting point:", error);
    window.alert(`확정 실패: ${error.message}`);
  }
};

window.boardV2ReportQuest = async function (questId) {
  const summary = document.getElementById("v2WorkSummary")?.value.trim();
  const assessment = document.getElementById("v2SelfAssessment")?.value;

  if (!summary) {
    window.alert("작업 내용을 입력해 주세요.");
    return;
  }

  if (!window.confirm("작업 결과를 보고하고 AI 판정을 요청할까요?")) return;

  try {
    await boardApi.reportQuest(questId, summary, assessment);
    await loadBoardV2();
    window.alert("보고가 완료되었습니다. AI 판정을 기다려 주세요.");
  } catch (error) {
    console.error("Failed to report quest:", error);
    window.alert(`보고 실패: ${error.message}`);
  }
};

window.boardV2StartQuestFromMission = async function () {
  if (!window.confirm("오늘의 주 임무로 작업을 시작할까요?")) return;

  try {
    await boardApi.startQuestFromMission();
    await loadBoardV2();
    window.alert("퀘스트가 시작되었습니다.");
    // 초안 초기화
    _reportDraft.summary = "";
    _reportDraft.assessment = "partial";
  } catch (error) {
    console.error("Failed to start quest:", error);
    window.alert(`시작 실패: ${error.message}`);
  }
};

window.boardV2EvaluateQuest = async function (questId, verdict) {
  const label = { done: "완료", partial: "부분 완료", hold: "보류" }[verdict];
  if (!window.confirm(`현재 퀘스트를 [${label}] 상태로 직접 판정할까요?`)) return;

  try {
    await boardApi.evaluateQuest(questId, verdict);
    await loadBoardV2();
    window.alert(`퀘스트가 [${label}] 상태로 종료되었습니다.`);
    // 초안 초기화
    _reportDraft.summary = "";
    _reportDraft.assessment = "partial";
  } catch (error) {
    console.error("Failed to evaluate quest:", error);
    window.alert(`판정 실패: ${error.message}`);
  }
};

window.boardV2DeferQuest = async function () {
  if (!window.confirm("현재 퀘스트를 오늘 목록에서 내리고 단기 플랜으로 미룰까요?")) return;

  try {
    await boardApi.deferQuest();
    await loadBoardV2();
    window.alert("퀘스트를 단기 플랜으로 이동했습니다.");
  } catch (error) {
    console.error("Failed to defer quest:", error);
    window.alert(`미루기 실패: ${error.message}`);
  }
};

window.boardV2SyncDraft = function () {
  const summaryEl = document.getElementById("v2WorkSummary");
  const assessmentEl = document.getElementById("v2SelfAssessment");
  if (summaryEl) _reportDraft.summary = summaryEl.value;
  if (assessmentEl) _reportDraft.assessment = assessmentEl.value;
};

window.boardV2SyncQuickInputDraft = function () {
  const el = document.getElementById("v2QuickInput");
  if (el) _quickInputDraft = el.value;
};

window.boardV2SubmitQuickInput = async function () {
  const text = _quickInputDraft.trim();
  if (!text) return;

  try {
    await boardApi.submitQuickInput(text);
    _quickInputDraft = "";
    await loadBoardV2();
    window.alert("입력이 처리되었습니다.");
  } catch (error) {
    console.error("Failed to submit quick input:", error);
    window.alert(`입력 실패: ${error.message}`);
  }
};

// 모달 동작
window.boardV2OpenModal = function (title, content) {
  const modal = document.getElementById("v2Modal");
  const titleEl = document.getElementById("v2ModalTitle");
  const bodyEl = document.getElementById("v2ModalBody");

  if (!modal || !titleEl || !bodyEl) return;

  titleEl.textContent = title;
  bodyEl.innerHTML = content;
  modal.hidden = false;
};

window.boardV2CloseModal = function () {
  const modal = document.getElementById("v2Modal");
  if (modal) {
    modal.hidden = true;
    loadBoardV2(); // 모달을 닫는 즉시 최신 상태 반영
  }
};

// 작업철(Workfile) Helper
window.boardV2OpenWorkfile = async function (questId, fallbackTitle) {
  let workfilePath = null;
  
  // 1. Try explicit mapping first
  try {
    const mapping = await boardApi.fetchWorkfileMapping();
    if (mapping) {
      workfilePath = mapping[questId] || null;
    }
  } catch (e) {}

  // 2. Fallback: title-based guess
  if (!workfilePath && fallbackTitle) {
    const slug = fallbackTitle.replace(/[^\w\s가-힣]/g, '').trim().split(/\s+/).slice(0, 3).join('-');
    workfilePath = `작업철/${slug}.md`;
  }

  if (!workfilePath) {
    window.alert('작업철이 연결되어 있지 않습니다.');
    return;
  }

  try {
    const content = await boardApi.fetchWorkfileContent(workfilePath);
    window.boardV2OpenModal('작업철: ' + fallbackTitle, `<pre style="white-space:pre-wrap;font-size:14px;">${content}</pre>`);
  } catch (e) {
    // Retry with simpler fallback name if the first one fails
    if (fallbackTitle) {
        const simpleSlug = fallbackTitle.replace(/[^\w가-힣]/g, '').slice(0, 10);
        try {
            const content2 = await boardApi.fetchWorkfileContent(`작업철/${simpleSlug}.md`);
            window.boardV2OpenModal('작업철: ' + fallbackTitle, `<pre style="white-space:pre-wrap;font-size:14px;">${content2}</pre>`);
            return;
        } catch(err) {
            // ignore
        }
    }
    window.alert('작업철 파일이 없습니다: ' + workfilePath);
  }
};

// NLP 액션 헬퍼
window.boardV2Refresh = async () => {
  await loadBoardV2();
};

window.boardV2ActionOverdueDone = async (id, title) => {
  try {
    await boardApi.submitQuickInput(`done ${title}`);
    await loadBoardV2();
  } catch (err) {
    console.error("Action Done failed:", err);
  }
};

window.boardV2ActionOverdueReschedule = async (id, title) => {
  try {
    await boardApi.submitQuickInput(`today ${title}`);
    await loadBoardV2();
  } catch (err) {
    console.error("Action Reschedule failed:", err);
  }
};

window.boardV2ActionOverdueHold = async (id, title) => {
  try {
    await boardApi.submitQuickInput(`hold ${title}`);
    await loadBoardV2();
  } catch (err) {
    console.error("Action Hold failed:", err);
  }
};
