function renderHistory(state) {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const { todayDone, partialItems, recentDone, allDone } = pickCompletedItems(state);

  // Filter Helper Function
  window.filterHistory = window.filterHistory || function(type) {
    const listWrap = document.getElementById('allDoneListContainer');
    if (!listWrap) return;
    
    const items = listWrap.querySelectorAll('.v2-list-item');
    const visibleDates = new Set();
    let count = 0;
    
    items.forEach(li => {
      if (type === 'all' || li.dataset.type === type) {
        li.style.display = '';
        if (li.dataset.date) visibleDates.add(li.dataset.date);
        count++;
      } else {
        li.style.display = 'none';
      }
    });

    const dividers = listWrap.querySelectorAll('.v2-history-divider');
    dividers.forEach(div => {
      if (visibleDates.has(div.dataset.date)) {
        div.style.display = '';
      } else {
        div.style.display = 'none';
      }
    });
    
    // Update summary count if details open
    const summarySpan = document.getElementById('allDoneCountText');
    if (summarySpan) {
      summarySpan.textContent = type === 'all' ? `(${count}건)` : `(${type === 'Quest'? '퀘스트':'세션'} ${count}건)`;
      summarySpan.title = type === 'all' ? '전체 항목 개수' : '필터링된 항목 개수';
    }

    // Toggle button active state
    document.querySelectorAll('.v2-history-filter-btn').forEach(btn => {
      if (btn.dataset.filter === type) {
        btn.style.background = 'rgba(45, 90, 39, 0.1)';
        btn.style.fontWeight = '800';
      } else {
        btn.style.background = 'transparent';
        btn.style.fontWeight = '600';
      }
    });

    // Save global state across 30s polls
    window.__v2HistoryFilter = type;
  };

  const renderHistoryList = (items, emptyText, compact = false) => {
    if (!items || items.length === 0) {
      return `<p class="v2-empty" style="padding: 16px; margin: 0;">${escapeHtml(emptyText)}</p>`;
    }
    
    let lastDateStr = null;
    let html = `<ul class="v2-list" style="margin:0;">`;
    
    items.forEach(item => {
      const isQuest = item.type === 'Quest';
      const typeClass = isQuest ? 'v2-history-badge-quest' : 'v2-history-badge-session';
      const typeLabel = isQuest ? '퀘스트' : '세션';
      
      const isDone = item.verdict === 'done';
      const statusClass = isDone ? 'v2-history-badge-done' : 'v2-history-badge-partial';
      const statusLabel = isDone ? '완료' : '부분';
      
      let dateStr = '';
      let timeStr = '';
      if (item.completedAt) {
        const fullStr = String(item.completedAt); // e.g., "2026-03-26T14:30:00"
        dateStr = fullStr.slice(0, 10);
        timeStr = fullStr.length > 11 ? fullStr.slice(11, 16).replace('T', ' ') : '';
      }
      
      if (dateStr && dateStr !== lastDateStr) {
        html += `
          <li class="v2-history-divider" data-date="${dateStr}" style="padding: 12px 16px 8px; background: rgba(45, 90, 39, 0.04); border-bottom: 1px solid rgba(45, 90, 39, 0.1); color: var(--v2-primary); font-size: 11px; font-weight: 800; letter-spacing: 0.04em;">
            ${dateStr}
          </li>
        `;
        lastDateStr = dateStr;
      }
      
      const clickableClass = " v2-modal-clickable";
      const modalContent = item.description ? escapeHtml(item.description).replace(/\n/g, '\\n') : "상세 내용 없음";
      const onclick = `onclick="window.boardV2OpenModal('${escapeHtml(item.title).replace(/\n/g, '\\n')}', '${modalContent}')"`;
      
      const titleStyle = isQuest 
          ? `font-size: ${compact ? '14px' : '15px'}; font-weight: 700; color: var(--v2-text);`
          : `font-size: ${compact ? '13px' : '14px'}; font-weight: 500; color: var(--v2-text-muted);`;
      const itemBg = isQuest ? 'background: #fff;' : 'background: rgba(0,0,0,0.015); border-left: 3px solid transparent;';
      const subtextOpacity = isQuest ? '0.85' : '0.5';
      
      html += `
        <li class="v2-list-item${clickableClass}" data-type="${item.type}" data-date="${dateStr}" ${onclick} style="padding: ${compact ? '8px 16px' : '10px 16px 12px'}; border-bottom: 1px solid var(--v2-border); ${itemBg}">
          <div style="display:flex; flex-direction:column; gap:2px;">
            <span class="v2-item-title" style="${titleStyle}">${escapeHtml(item.title)}</span>
            ${item.subtext ? `<span style="font-size: 11px; color: var(--v2-text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; opacity: ${subtextOpacity};">↳ ${escapeHtml(item.subtext)}</span>` : ''}
          </div>
          <div class="v2-history-item-meta">
            <span class="v2-history-badge ${typeClass}">${typeLabel}</span>
            <span class="v2-history-badge ${statusClass}">${statusLabel}</span>
            <span style="opacity: 0.8;">${timeStr || dateStr}</span>
          </div>
        </li>
      `;
    });
    
    html += `</ul>`;
    return html;
  };

  root.innerHTML = `
    <div class="v2-layout">
      <aside class="v2-rail v2-rail-left">
        <section class="v2-rail-section">
          <span class="v2-section-label" title="현재 집계된 완료 상태 데이터 요약">요약</span>
          <div class="v2-rail-card v2-rail-card-accent">
            <span class="v2-item-title" title="오늘(KST) 완전히 끝난 항목">오늘 완료 ${todayDone.length}건</span>
            <span class="v2-item-meta" style="line-height: 1.6;">
              <span title="완전히 끝나지 않고 보류/부분 처리된 항목">부분 완료<span style="opacity:0.6; font-size:0.9em; font-weight:normal;">(보류)</span> ${partialItems.length}건</span><br/>
              <span title="오늘을 제외한 과거 완료 항목 전체">이전 완료<span style="opacity:0.6; font-size:0.9em; font-weight:normal;">(과거)</span> ${allDone.length - todayDone.length - partialItems.length}건</span>
            </span>
            <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(45, 90, 39, 0.1);">
              <span class="v2-item-meta" style="font-weight:700; color: var(--v2-primary);" title="모든 완료 및 부분 완료 기록의 총합">총 누적 기록 ${allDone.length}건</span>
            </div>
          </div>
        </section>
      </aside>

      <main class="v2-main v2-main-progress">
        <span class="v2-day-label">완료된 작업 내역</span>
        <p style="margin: 6px 0 24px 0; font-size: 13px; color: var(--v2-text-muted); line-height: 1.5;">
          단순한 에이전트 로그가 아닌, <b>완전히 끝마친 퀘스트와 세션 결과물</b>을 돌아보는 공간입니다.
        </p>
        <div class="v2-mission-wrap" style="padding-bottom: 60px;">
          <span class="v2-section-label" title="오늘(KST) 완전히 끝난 퀘스트 및 세션">오늘 완료한 작업 <span style="font-weight:normal; opacity:0.8;">${todayDone.length}건</span></span>
          <div class="v2-progress-stack" style="margin-bottom: 32px;">
            <div class="v2-rail-card" style="padding: 0; overflow: hidden;">
              ${renderHistoryList(todayDone, "오늘 완료된 작업이 없습니다.")}
            </div>
          </div>

          <span class="v2-section-label" title="진행 중에 부분적으로 완료 처리된 항목">보류 및 부분 완료 <span style="font-weight:normal; opacity:0.8;">${partialItems.length}건</span></span>
          <div class="v2-progress-stack" style="margin-bottom: 32px;">
            <div class="v2-rail-card" style="padding: 0; overflow: hidden;">
              ${renderHistoryList(partialItems, "보류되거나 부분 완료된 작업이 없습니다.")}
            </div>
          </div>

          <span class="v2-section-label" title="오늘을 제외한 최근 완료 항목 (최대 10개)">최근 완료 기록 <span style="font-weight:normal; opacity:0.8;">${recentDone.length}건</span></span>
          <div class="v2-progress-stack" style="margin-bottom: 32px;">
            <div class="v2-rail-card" style="padding: 0; overflow: hidden;">
              ${renderHistoryList(recentDone, "최근 완료된 작업이 없습니다.")}
            </div>
          </div>

          <div style="display:flex; justify-content:space-between; align-items:center;" title="기간 제한 없이 모든 완료 및 부분 완료 항목을 조회합니다.">
            <span class="v2-section-label" style="margin:0;">전체 완료 기록 보기</span>
            <div style="display:flex; gap: 4px; border: 1px solid var(--v2-border); border-radius: 4px; padding: 2px;" title="목록 필터링">
              <button class="v2-btn-inline v2-history-filter-btn" data-filter="all" onclick="window.filterHistory('all')" style="border:0; background:transparent; border-radius:3px; padding:2px 8px; font-size:11px; font-weight:600; cursor:pointer; color:var(--v2-text-muted);">전체</button>
              <button class="v2-btn-inline v2-history-filter-btn" data-filter="Quest" onclick="window.filterHistory('Quest')" style="border:0; background:transparent; border-radius:3px; padding:2px 8px; font-size:11px; font-weight:600; cursor:pointer; color:var(--v2-text-muted);">퀘스트</button>
              <button class="v2-btn-inline v2-history-filter-btn" data-filter="Session" onclick="window.filterHistory('Session')" style="border:0; background:transparent; border-radius:3px; padding:2px 8px; font-size:11px; font-weight:600; cursor:pointer; color:var(--v2-text-muted);">세션</button>
            </div>
          </div>
          <div class="v2-progress-stack" style="margin-top: 14px;">
            <details style="cursor: pointer; background: var(--v2-bg-elevated); border-radius: 8px; border: 1px solid var(--v2-border); overflow: hidden;">
              <summary class="v2-item-title" style="margin:0; padding: 16px; outline: none; user-select: none;">
                전체 리스트 펼치기 <span id="allDoneCountText" style="opacity: 0.8; font-weight: normal;">(${allDone.length}건)</span>
              </summary>
              <div id="allDoneListContainer" style="padding: 0; border-top: 1px solid var(--v2-border);">
                ${renderHistoryList(allDone, "완료된 항목이 없습니다.", true)}
              </div>
            </details>
          </div>
        </div>
      </main>

      <aside class="v2-rail v2-rail-right">
        ${renderQuickInputSection()}
      </aside>
    </div>
  `;
  
  // Re-apply filter if set from previous renders
  if (window.__v2HistoryFilter) {
    setTimeout(() => window.filterHistory(window.__v2HistoryFilter), 0);
  } else {
    setTimeout(() => window.filterHistory('all'), 0);
  }
}
