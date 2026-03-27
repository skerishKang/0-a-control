function renderMorning(state) {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const mission = pickMainMission(state);
  const urgentItems = pickUrgentUpcoming(state);
  const overdueItems = pickOverdue(state);
  const unfinishedItems = pickUnfinishedItems(state);
  const briefs = pickBriefs(state);
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
        ${overdueItems.length > 0 ? `
        <section class="v2-rail-section">
          <span class="v2-section-label" style="color: var(--v2-amber);">기한 지남 / 검토 필요</span>
          <div class="v2-rail-card" style="border-left: 3px solid var(--v2-amber);">
            ${renderList(overdueItems, "", (item) => ({ text: item.due_at || "기한 정보 없음", isDue: true }), renderOverdueActions)}
          </div>
        </section>
        ` : ""}

        <section class="v2-rail-section">
          <span class="v2-section-label">기한 임박</span>
          <div class="v2-rail-card">
            ${renderList(urgentItems, "마감 기한이 있는 항목이 없습니다.", (item) => ({ text: item.due_at || "기한 정보 없음", isDue: true }))}
          </div>
        </section>

        <section class="v2-rail-section">
          <span class="v2-section-label">최근 브리프</span>
          <div class="v2-rail-card">
            ${renderBriefList(briefs)}
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
          <div class="v2-start-actions" style="margin-top: 40px; max-width: 320px;">
            <button class="v2-btn v2-btn-primary" type="button" onclick="window.boardV2StartQuestFromMission()" ${hasCurrentQuest ? "disabled" : ""}>
              ${hasCurrentQuest ? "진행 중인 작업 있음" : "주 임무로 퀘스트 시작"}
            </button>
          </div>
        </div>
      </main>

      <aside class="v2-rail v2-rail-right">
        ${renderQuickInputSection()}

        <section class="v2-rail-section">
          <span class="v2-section-label">확정된 시작점</span>
          ${startHtml}
        </section>

        <section class="v2-rail-section">
          <span class="v2-section-label">전체 계획 및 보류</span>
          <div class="v2-rail-card">
            ${renderList(unfinishedItems, "남은 계획 항목이 없습니다.", (item) => ({ text: item.project_key || "No Project", isDue: false }))}
          </div>
        </section>
      </aside>
    </div>
  `;
}
