function renderEndOfDay(state) {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const progress = state.day_progress_summary || {};
  const doneItems = pickDoneItems(state);
  const unfinishedItems = pickUnfinishedItems(state);
  const dueItems = pickDueItems(state);
  const briefs = pickBriefs(state);
  const sessions = pickSessions(state);
  const tomorrowFirst = state.tomorrow_first_quest || null;
  const confirmed = state.confirmed_starting_point || null;
  const decision = state.latest_decision_summary || null;

  let tomorrowHtml = "";
  if (confirmed && confirmed.title) {
    tomorrowHtml = `
      <div class="v2-start-confirmed-card">
        <span class="v2-start-badge -confirmed">내일 시작 확정</span>
        <span class="v2-item-title" style="font-size: 18px; margin-bottom: 4px;">${escapeHtml(confirmed.title)}</span>
        <span class="v2-item-meta" style="font-size: 14px; opacity: 0.9;">${escapeHtml(confirmed.reason || "")}</span>
        ${confirmed.restart_point ? `
          <div class="v2-restart-label">
            <b>재시작 지점:</b> ${escapeHtml(confirmed.restart_point)}
          </div>
        ` : ""}
      </div>
    `;
  } else if (tomorrowFirst && tomorrowFirst.title) {
    tomorrowHtml = `
      <div class="v2-start-suggestion-card">
        <span class="v2-start-badge -suggestion">내일의 제안</span>
        <span class="v2-item-title">${escapeHtml(tomorrowFirst.title)}</span>
        <span class="v2-item-meta">${escapeHtml(tomorrowFirst.reason || "")}</span>
        <div class="v2-start-actions">
          <button class="v2-btn v2-btn-primary" type="button" 
            onclick="window.boardV2ConfirmStartingPoint('${escapeHtml(tomorrowFirst.title)}', '${escapeHtml(tomorrowFirst.reason || "")}', '${escapeHtml(tomorrowFirst.source || "suggestion")}')">
            이 제안으로 내일 시작 확정
          </button>
        </div>
      </div>
    `;
  } else {
    tomorrowHtml = `<p class="v2-empty" style="padding: 20px; text-align: center; border: 1px dashed var(--v2-border);">내일의 시작점이 아직 없습니다. 퀵 입력을 통해 계획을 제안해 보세요.</p>`;
  }

  const decisionTitle = decision?.title || "오늘 결정";
  const decisionContent = decision?.impact_summary || decision?.reason || "";
  const decisionHtml = decision
    ? `
      <div class="v2-rail-card v2-modal-clickable" onclick="window.boardV2OpenModal('${escapeHtml(decisionTitle)}', '${escapeHtml(decisionContent)}')">
        <span class="v2-item-title">${escapeHtml(decisionTitle)}</span>
        <span class="v2-item-meta">${escapeHtml(decisionContent)}</span>
      </div>
    `
    : `<div class="v2-rail-card"><p class="v2-empty">오늘 결정 요약이 없습니다.</p></div>`;

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

        <section class="v2-rail-section">
          <span class="v2-section-label">기한 임박</span>
          <div class="v2-rail-card">
            ${renderList(urgentItems, "마감 기한이 있는 항목이 없습니다.", (item) => ({ text: item.due_at || "기한 정보 없음", isDue: true }))}
          </div>
        </section>
      </aside>

      <main class="v2-main v2-main-progress">
        <span class="v2-day-label">${escapeHtml(getDayLabel())}</span>
        <div class="v2-mission-wrap">
          <span class="v2-section-label">오늘 마감 및 내일 준비</span>
          <h1 class="v2-mission-title v2-quest-title">오늘의 마침표를 찍고,<br/>내일의 첫 단추를 연결합니다.</h1>

          <div class="v2-progress-stack">
            <div class="v2-inline-card">
              <span class="v2-inline-label">남은 항목</span>
              <strong>${unfinishedItems.length ? `${unfinishedItems.length}개 항목이 다시 이어갈 대상으로 남아 있습니다.` : "다시 이어갈 항목이 없습니다."}</strong>
            </div>
            
            <span class="v2-section-label" style="margin-top: 12px;">내일의 시작점</span>
            ${tomorrowHtml}
          </div>
        </div>
      </main>

      <aside class="v2-rail v2-rail-right">
        ${renderQuickInputSection()}

        <section class="v2-rail-section">
          <span class="v2-section-label">전체 계획 및 보류</span>
          <div class="v2-rail-card">
            ${renderList(unfinishedItems, "남은 계획 항목이 없습니다.", (item) => ({ text: formatPlanLabel(item.status || item.bucket), isDue: false }))}
          </div>
        </section>

        <section class="v2-rail-section">
          <span class="v2-section-label">최근 브리프</span>
          <div class="v2-rail-card">
            ${renderBriefList(briefs)}
          </div>
        </section>

        <section class="v2-rail-section">
          <span class="v2-section-label">결정 요약</span>
          ${decisionHtml}
        </section>

        <section class="v2-rail-section">
          <span class="v2-section-label">최근 세션</span>
          <div class="v2-rail-card">
            ${renderSessionList(sessions)}
          </div>
        </section>
      </aside>
    </div>
  `;
}
