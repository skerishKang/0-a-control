function renderEndOfDay(state) {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const progress = state.day_progress_summary || {};
  const doneItems = pickDoneItems(state);
  const unfinishedItems = pickUnfinishedItems(state);
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
    : `<div class="v2-rail-card"><p class="v2-empty">오늘 결정 결산 내역이 없습니다.</p></div>`;

  // 2단 분배 구조: 좌측(오늘 완료 및 현황), 우측(내일 준비 및 미완료)
  root.innerHTML = `
    <div class="v2-layout" style="grid-template-columns: 1fr 1fr; gap: 40px; max-width: 1000px; margin: 0 auto;">
      
      <!-- Left Column: 오늘 성과 요약 -->
      <aside class="v2-rail">
        <span class="v2-day-label">${escapeHtml(getDayLabel())} 마감</span>
        <h1 class="v2-mission-title" style="font-size: 28px; margin-bottom: 24px; color: var(--v2-foreground);">오늘 하루 결산</h1>
        
        <section class="v2-rail-section">
          <span class="v2-section-label">진행 요약</span>
          <div class="v2-rail-card v2-rail-card-accent" style="padding: 20px; font-size: 16px;">
            <span class="v2-item-title" style="font-size: 20px;">완료 ${progress.done || 0} · 부분 ${progress.partial || 0} · 보류 ${progress.hold || 0}</span>
            <span class="v2-item-meta">오늘 발생한 상태 변화를 요약합니다.</span>
          </div>
        </section>

        <section class="v2-rail-section">
          <span class="v2-section-label">오늘 해낸 일</span>
          <div class="v2-rail-card" style="padding: 16px;">
            ${renderList(doneItems, "완료한 퀘스트가 없습니다.", (item) => ({ text: item.completed_at ? item.completed_at.split('T')[1].substring(0, 5) : "완료 시간 없음", isDue: false }))}
          </div>
        </section>
        
        <section class="v2-rail-section">
          <span class="v2-section-label">전략적 결정 항목</span>
          ${decisionHtml}
        </section>
      </aside>

      <!-- Right Column: 내일의 세팅 -->
      <aside class="v2-rail">
        <h1 class="v2-mission-title" style="font-size: 28px; margin-bottom: 24px; color: var(--v2-foreground); margin-top: 36px;">내일의 준비</h1>
        
        <section class="v2-rail-section">
          <span class="v2-section-label" style="color: var(--v2-brand);">내일의 시작점 배정</span>
          ${tomorrowHtml}
        </section>

        <section class="v2-rail-section">
          <span class="v2-section-label">내일 이어나갈 남은 항목 (${unfinishedItems.length}개)</span>
          <div class="v2-rail-card" style="max-height: 250px; overflow-y: auto;">
            ${renderList(unfinishedItems, "남은 계획 항목이 없습니다.", (item) => ({ text: formatPlanLabel(item.status || item.bucket), isDue: false }))}
          </div>
        </section>

        ${renderQuickInputSection()}
        
      </aside>
    </div>
  `;
}
