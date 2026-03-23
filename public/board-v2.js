function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function getDayLabel() {
  const now = new Date();
  const weekdays = ["일", "월", "화", "수", "목", "금", "토"];
  const yyyy = now.getFullYear();
  const mm = String(now.getMonth() + 1).padStart(2, "0");
  const dd = String(now.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd} (${weekdays[now.getDay()]})`;
}

function pickMainMission(state) {
  if (state.main_mission && typeof state.main_mission === "object") {
    return {
      title: state.main_mission.title || state.main_mission_title || "주 임무가 없습니다.",
      reason: state.main_mission.priority_reason || state.main_mission_reason || "이유 정보 없음",
    };
  }

  return {
    title: state.main_mission_title || "주 임무가 없습니다.",
    reason: state.main_mission_reason || "이유 정보 없음",
  };
}

function pickDueItems(state) {
  return state.due_items || state.dated_pressure_summary || [];
}

function pickUnfinishedItems(state) {
  return state.unfinished_items || state.top_unfinished_summary || [];
}

function renderList(items, emptyText, metaFormatter) {
  if (!items || !items.length) {
    return `<p class="v2-empty">${escapeHtml(emptyText)}</p>`;
  }

  return `
    <ul class="v2-list">
      ${items.map((item) => `
        <li class="v2-list-item">
          <span class="v2-item-title">${escapeHtml(item.title)}</span>
          <span class="v2-item-meta${metaFormatter(item).isDue ? ' -due' : ''}">${escapeHtml(metaFormatter(item).text)}</span>
        </li>
      `).join("")}
    </ul>
  `;
}

function renderMorning(state) {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const mission = pickMainMission(state);
  const dueItems = pickDueItems(state);
  const unfinishedItems = pickUnfinishedItems(state);
  const confirmed = state.confirmed_starting_point || null;
  const suggested = state.tomorrow_first_quest || null;
  const startPoint = confirmed || suggested;
  const hasCurrentQuest = Boolean(state.current_quest_id || (state.current_quest && state.current_quest.id));

  const startHtml = startPoint && startPoint.title
    ? `
      <div class="v2-start-card">
        <span class="v2-start-badge">${confirmed ? "확정됨" : "추천"}</span>
        <span class="v2-item-title">${escapeHtml(startPoint.title)}</span>
        <span class="v2-item-meta">${escapeHtml(startPoint.reason || "")}</span>
        <div class="v2-start-actions">
          <button class="v2-btn v2-btn-primary" type="button" onclick="window.promoteStartingPoint && window.promoteStartingPoint()" ${hasCurrentQuest ? "disabled" : ""}>${hasCurrentQuest ? "진행 중인 작업 있음" : "이 약속으로 작업 시작"}</button>
        </div>
      </div>
    `
    : `<p class="v2-empty">확정된 시작점이 없습니다.</p>`;

  root.innerHTML = `
    <div class="v2-layout">
      <aside class="v2-rail v2-rail-left">
        <section class="v2-rail-section">
          <span class="v2-section-label">기한 임박</span>
          <div class="v2-rail-card">
            ${renderList(dueItems, "마감 기한이 있는 항목이 없습니다.", (item) => ({ text: item.due_at || "기한 정보 없음", isDue: true }))}
          </div>
        </section>
      </aside>

      <main class="v2-main">
        <span class="v2-day-label">${escapeHtml(getDayLabel())}</span>
        <div class="v2-mission-wrap">
          <span class="v2-section-label">오늘의 주 임무</span>
          <h1 class="v2-mission-title">${escapeHtml(mission.title)}</h1>
          <div class="v2-mission-reason-wrap">
            <span class="v2-mission-reason-label">이유</span>
            <p class="v2-mission-reason">${escapeHtml(mission.reason)}</p>
          </div>
        </div>
      </main>

      <aside class="v2-rail v2-rail-right">
        <section class="v2-rail-section">
          <span class="v2-section-label">확정된 시작점</span>
          ${startHtml}
        </section>

        <section class="v2-rail-section">
          <span class="v2-section-label">미완료 항목</span>
          <div class="v2-rail-card">
            ${renderList(unfinishedItems, "미완료 항목이 없습니다.", (item) => ({ text: item.bucket || "상태 미정", isDue: false }))}
          </div>
        </section>
      </aside>
    </div>
  `;
}

async function loadBoardV2() {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  root.innerHTML = `<div class="v2-loading">데이터를 불러오는 중입니다...</div>`;

  try {
    const response = await fetch("/api/current-state");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const payload = await response.json();
    renderMorning(payload.current_state || {});
  } catch (error) {
    console.error("Failed to load board-v2 state:", error);
    root.innerHTML = `<div class="v2-loading">데이터 로드 실패</div>`;
  }
}

document.addEventListener("DOMContentLoaded", loadBoardV2);
