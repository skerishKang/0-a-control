/**
 * app-quest-ops.js — Quest evaluation, hold, start, defer, and Telegram sync operations
 * Extracted from app.js (lines 337-497) to reduce file size below 500-line limit
 */

async function handleQuestEvaluation(event) {
  event.preventDefault();
  const current = state.currentState || {};
  if (!current.current_quest_id) {
    alert("현재 퀘스트가 없습니다.");
    return;
  }

  const payload = {
    quest_id: current.current_quest_id,
    work_summary: document.getElementById("questWorkSummary").value.trim(),
    remaining_work: document.getElementById("questRemainingWork").value.trim(),
    blocker: document.getElementById("questBlocker").value.trim(),
    self_assessment: document.getElementById("questSelfAssessment").value.trim(),
    session_id: state.activeSession?.id || "",
  };

  try {
    await fetchJson("/api/quests/report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (e) {
    alert(e.message || "보고 실패");
    return;
  }

  event.target.reset();
  document.getElementById("questSelfAssessment").value = "partial";
  closeReportPanel();
  await loadAll();
}

async function handleHoldCurrentQuest() {
  const current = state.currentState || {};
  if (!current.current_quest_id) {
    alert("현재 퀘스트가 없습니다.");
    return;
  }

  const btn = document.getElementById("holdCurrentQuestBtn");
  if (btn) {
    btn.disabled = true;
    btn.textContent = "정리 중...";
  }

  try {
    await fetchJson("/api/current-quest/hold", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    await loadAll();
  } catch (error) {
    alert(`미완료 처리 실패: ${error.message}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "미완료로 남기기";
    }
  }
}

async function handleStartCurrentQuest() {
  const current = state.currentState || {};
  if (current.current_quest_id) {
    await loadAll();
    return;
  }

  const btn = document.getElementById("startCurrentQuestBtn");
  if (btn) {
    btn.disabled = true;
    btn.textContent = "생성 중...";
  }

  try {
    await fetchJson("/api/current-quest/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    await loadAll();
  } catch (error) {
    alert(`퀘스트 시작 실패: ${error.message}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "지금 퀘스트 잡기";
    }
  }
}

async function handleDeferCurrentQuest() {
  const current = state.currentState || {};
  if (!current.current_quest_id) {
    alert("현재 퀘스트가 없습니다.");
    return;
  }

  const btn = document.getElementById("deferCurrentQuestBtn");
  if (btn) {
    btn.disabled = true;
    btn.textContent = "정리 중...";
  }

  try {
    await fetchJson("/api/current-quest/defer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    await loadAll();
  } catch (error) {
    alert(`단기 플랜 이동 실패: ${error.message}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "단기 플랜으로";
    }
  }
}

async function handleTelegramSync() {
  const btn = document.getElementById("syncTelegramBtn");
  const banner = document.getElementById("syncStatusBanner");
  if (!btn) return;

  state.telegramSyncRunning = true;
  btn.disabled = true;
  btn.textContent = "동기화 중...";
  renderTelegramSyncStatus();
  if (banner) banner.style.opacity = "0.65";

  try {
    const res = await fetchJson("/api/telegram/sync-core", { method: "POST" });
    state.lastTelegramSyncRun = {
      ...res,
      executed_at: new Date().toISOString(),
    };
    await loadAll();
    await refreshExternalContextPanelData();
  } catch (error) {
    console.error("Telegram sync failed:", error);
    state.lastTelegramSyncRun = {
      ok: false,
      error: error.message,
      failed_at: new Date().toISOString(),
    };
    renderTelegramSyncStatus();
    alert(`Telegram 동기화 실패: ${error.message}`);
  } finally {
    state.telegramSyncRunning = false;
    btn.disabled = false;
    btn.textContent = "지금 동기화";
    if (banner) banner.style.opacity = "1";
    renderTelegramSyncStatus();
  }
}