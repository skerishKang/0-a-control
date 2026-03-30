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

    _cachedState = state;
    const phase = getEffectivePhase(state);
    renderPhaseTabs(phase);
    renderStatusLabel(state, phase);
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

// Action functions have been moved to board-v2-actions.js

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
