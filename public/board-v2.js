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
      reason: state.main_mission.priority_reason || state.main_mission_reason || "오늘 우선순위로 올린 항목입니다.",
    };
  }

  return {
    title: state.main_mission_title || "주 임무가 없습니다.",
    reason: state.main_mission_reason || "오늘 우선순위로 올린 항목입니다.",
  };
}

function pickDueItems(state) {
  return state.due_items || state.dated_pressure_summary || [];
}

function pickUnfinishedItems(state) {
  return state.unfinished_items || state.top_unfinished_summary || [];
}

function pickCurrentQuest(state) {
  const quest = state.current_quest && typeof state.current_quest === "object" ? state.current_quest : {};
  return {
    id: state.current_quest_id || quest.id || "",
    title: state.current_quest_title || quest.title || "현재 퀘스트가 없습니다.",
    completionCriteria:
      state.current_quest_completion_criteria ||
      quest.completion_criteria ||
      "완료 기준을 아직 적지 않았습니다.",
    restartPoint: state.restart_point || quest.restart_point || "다시 시작할 지점이 아직 없습니다.",
  };
}

function pickRecentVerdict(state) {
  return state.recent_verdict && Object.keys(state.recent_verdict).length
    ? state.recent_verdict
    : state.latest_decision_summary || null;
}

function pickDoneItems(state) {
  return state.today_done_quests || [];
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
  const canClear = Boolean(confirmed && confirmed.title);

  const startHtml = startPoint && startPoint.title
    ? `
      <div class="v2-start-card">
        <span class="v2-start-badge">${confirmed ? "확정됨" : "추천"}</span>
        <span class="v2-item-title">${escapeHtml(startPoint.title)}</span>
        <span class="v2-item-meta">${escapeHtml(startPoint.reason || "")}</span>
        <div class="v2-start-actions">
          <button class="v2-btn v2-btn-primary" type="button" onclick="window.boardV2PromoteStartingPoint()" ${hasCurrentQuest ? "disabled" : ""}>${hasCurrentQuest ? "진행 중인 작업 있음" : "이 약속으로 작업 시작"}</button>
          ${canClear ? `<button class="v2-btn v2-btn-secondary" type="button" onclick="window.boardV2ClearStartingPoint()">이 약속 비우기</button>` : ""}
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

function renderInProgress(state) {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const quest = pickCurrentQuest(state);
  const unfinishedItems = pickUnfinishedItems(state);
  const recentVerdict = pickRecentVerdict(state);
  const nextQuest = state.recommended_next_quest || state.tomorrow_first_quest?.title || "";
  const questStatus = state.quest_status_summary || {};
  const progress = state.day_progress_summary || {};

  const questTitle = quest.id || quest.title !== "현재 퀘스트가 없습니다."
    ? quest.title
    : state.main_mission_title || "현재 퀘스트가 없습니다.";

  const verdictHtml = recentVerdict
    ? `
      <div class="v2-rail-card">
        <span class="v2-item-title">${escapeHtml(recentVerdict.title || "최근 판단")}</span>
        <span class="v2-item-meta">${escapeHtml(recentVerdict.reason || recentVerdict.impact_summary || "최근 판단 요약이 없습니다.")}</span>
      </div>
    `
    : `<div class="v2-rail-card"><p class="v2-empty">최근 판단이 없습니다.</p></div>`;

  const nextQuestHtml = nextQuest
    ? `<div class="v2-inline-card"><span class="v2-inline-label">다음 퀘스트 후보</span><strong>${escapeHtml(nextQuest)}</strong></div>`
    : `<div class="v2-inline-card"><span class="v2-inline-label">다음 퀘스트 후보</span><strong>아직 제안이 없습니다.</strong></div>`;

  root.innerHTML = `
    <div class="v2-layout">
      <aside class="v2-rail v2-rail-left">
        <section class="v2-rail-section">
          <span class="v2-section-label">최근 판단</span>
          ${verdictHtml}
        </section>

        <section class="v2-rail-section">
          <span class="v2-section-label">변화 요약</span>
          <div class="v2-rail-card v2-rail-card-accent">
            <span class="v2-item-title">오늘 진행 요약</span>
            <span class="v2-item-meta">완료 ${progress.done || 0} · 부분 ${progress.partial || 0} · 보류 ${progress.hold || 0}</span>
          </div>
        </section>
      </aside>

      <main class="v2-main v2-main-progress">
        <span class="v2-day-label">${escapeHtml(getDayLabel())}</span>
        <div class="v2-mission-wrap">
          <span class="v2-section-label">현재 퀘스트</span>
          <h1 class="v2-mission-title v2-quest-title">${escapeHtml(questTitle)}</h1>

          <div class="v2-progress-stack">
            <div class="v2-inline-card">
              <span class="v2-inline-label">완료 기준</span>
              <strong>${escapeHtml(quest.completionCriteria)}</strong>
            </div>
            <div class="v2-inline-card">
              <span class="v2-inline-label">재시작 포인트</span>
              <strong>${escapeHtml(quest.restartPoint)}</strong>
            </div>
            ${nextQuestHtml}
          </div>
        </div>
      </main>

      <aside class="v2-rail v2-rail-right">
        <section class="v2-rail-section">
          <span class="v2-section-label">진행 상태</span>
          <div class="v2-rail-card">
            <span class="v2-item-title">${questStatus.is_pending ? "판정 대기 중" : "진행 중"}</span>
            <span class="v2-item-meta">${escapeHtml(questStatus.preliminary_reason || state.day_phase_reason || "현재 퀘스트 중심으로 진행 중입니다.")}</span>
          </div>
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

function renderEndOfDay(state) {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const progress = state.day_progress_summary || {};
  const doneItems = pickDoneItems(state);
  const unfinishedItems = pickUnfinishedItems(state);
  const tomorrowFirst = state.tomorrow_first_quest || null;
  const confirmed = state.confirmed_starting_point || null;
  const decision = state.latest_decision_summary || null;

  const tomorrowCard = tomorrowFirst && tomorrowFirst.title
    ? `
      <div class="v2-start-card">
        <span class="v2-start-badge">내일 첫 퀘스트</span>
        <span class="v2-item-title">${escapeHtml(tomorrowFirst.title)}</span>
        <span class="v2-item-meta">${escapeHtml(tomorrowFirst.reason || "")}</span>
      </div>
    `
    : `<p class="v2-empty">내일 제안이 아직 없습니다.</p>`;

  const confirmedHtml = confirmed && confirmed.title
    ? `
      <div class="v2-rail-card">
        <span class="v2-item-title">${escapeHtml(confirmed.title)}</span>
        <span class="v2-item-meta">${escapeHtml(confirmed.reason || "")}</span>
      </div>
    `
    : `<div class="v2-rail-card"><p class="v2-empty">확정된 시작점이 없습니다.</p></div>`;

  const decisionHtml = decision
    ? `
      <div class="v2-rail-card">
        <span class="v2-item-title">${escapeHtml(decision.title || "오늘 결정")}</span>
        <span class="v2-item-meta">${escapeHtml(decision.impact_summary || decision.reason || "")}</span>
      </div>
    `
    : `<div class="v2-rail-card"><p class="v2-empty">오늘 결정 요약이 없습니다.</p></div>`;

  root.innerHTML = `
    <div class="v2-layout">
      <aside class="v2-rail v2-rail-left">
        <section class="v2-rail-section">
          <span class="v2-section-label">오늘 결과</span>
          <div class="v2-rail-card">
            ${renderList(doneItems, "완료한 퀘스트가 없습니다.", (item) => ({ text: item.completed_at || "완료 시각 없음", isDue: false }))}
          </div>
        </section>

        <section class="v2-rail-section">
          <span class="v2-section-label">진행 요약</span>
          <div class="v2-rail-card v2-rail-card-accent">
            <span class="v2-item-title">완료 ${progress.done || 0} · 부분 ${progress.partial || 0} · 보류 ${progress.hold || 0}</span>
            <span class="v2-item-meta">오늘 하루의 실제 진행을 기준으로 정리합니다.</span>
          </div>
        </section>
      </aside>

      <main class="v2-main v2-main-progress">
        <span class="v2-day-label">${escapeHtml(getDayLabel())}</span>
        <div class="v2-mission-wrap">
          <span class="v2-section-label">오늘 마감</span>
          <h1 class="v2-mission-title v2-quest-title">오늘 한 일과 내일의 첫 단추를 정리합니다.</h1>

          <div class="v2-progress-stack">
            <div class="v2-inline-card v2-inline-card-accent">
              <span class="v2-inline-label">남은 항목</span>
              <strong>${unfinishedItems.length ? `${unfinishedItems.length}개 항목이 다시 이어갈 대상으로 남아 있습니다.` : "다시 이어갈 항목이 없습니다."}</strong>
            </div>
            ${tomorrowCard}
          </div>
        </div>
      </main>

      <aside class="v2-rail v2-rail-right">
        <section class="v2-rail-section">
          <span class="v2-section-label">확정된 시작점</span>
          ${confirmedHtml}
        </section>

        <section class="v2-rail-section">
          <span class="v2-section-label">남은 전략</span>
          <div class="v2-rail-card">
            ${renderList(unfinishedItems, "미완료 항목이 없습니다.", (item) => ({ text: item.status || item.bucket || "상태 미정", isDue: false }))}
          </div>
        </section>

        <section class="v2-rail-section">
          <span class="v2-section-label">결정 요약</span>
          ${decisionHtml}
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
    const state = payload.current_state || {};
    const phase = state.day_phase || "morning";

    if (phase === "end-of-day") {
      renderEndOfDay(state);
      return;
    }

    if (phase === "in-progress" || phase === "verdict-pending" || state.current_quest_id || (state.current_quest && state.current_quest.id)) {
      renderInProgress(state);
      return;
    }

    renderMorning(state);
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

document.addEventListener("DOMContentLoaded", loadBoardV2);
