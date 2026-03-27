function renderHistory(state) {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const { todayTasks, recentTasks, todayLogs, recentLogs, allTasks, allLogs } = pickCompletedItems(state);
  const totalCompleted = allTasks.length + allLogs.length;

  // Filter Helper Function
  window.filterHistory = window.filterHistory || function(type) {
    const listWraps = document.querySelectorAll('.v2-history-list-container');
    
    listWraps.forEach(listWrap => {
      const items = listWrap.querySelectorAll('.v2-list-item');
      const visibleDates = new Set();
      let count = 0;
      
      items.forEach(li => {
        const itemType = li.dataset.type; // Quest, Session, Log
        const isMatch = (type === 'all') || 
                        (type === 'tasks' && (itemType === 'Quest' || itemType === 'Session')) ||
                        (type === 'logs' && itemType === 'Log');

        if (isMatch) {
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
    });
    
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

    window.__v2HistoryFilter = type;
  };

  const renderHistoryList = (items, emptyText, compact = false) => {
    if (!items || items.length === 0) {
      return `<p class="v2-empty" style="padding: 16px; margin: 0;">${escapeHtml(emptyText)}</p>`;
    }
    
    let lastDateStr = null;
    let html = `<ul class="v2-list v2-history-list-container" style="margin:0;">`;
    
    items.forEach(item => {
      const isQuest = item.type === 'Quest';
      const isLog = item.type === 'Log' || item.isLog;
      const typeClass = isQuest ? 'v2-history-badge-quest' : 'v2-history-badge-session';
      const typeLabel = isQuest ? '퀘스트' : (isLog ? '로그' : '세션');
      
      const isDone = item.verdict === 'done';
      const statusClass = isDone ? 'v2-history-badge-done' : 'v2-history-badge-partial';
      const statusLabel = isDone ? (isLog ? '기록' : '완료') : '부분';
      
      let dateStr = '';
      let timeStr = '';
      if (item.completedAt) {
        const fullStr = String(item.completedAt); 
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
      const modalContent = item.description ? escapeHtml(item.description).replace(/\n/g, '\\n').replace(/'/g, "\\'") : "상세 내용 없음";
      const onclick = `onclick="window.boardV2OpenModal('${escapeHtml(item.title).replace(/\n/g, '\\n').replace(/'/g, "\\'")}', '${modalContent}')"`;
      
      const titleStyle = !isLog 
          ? `font-size: ${compact ? '14px' : '15px'}; font-weight: 700; color: var(--v2-text);`
          : `font-size: ${compact ? '13px' : '14px'}; font-weight: 500; color: var(--v2-text-muted); opacity: 0.8;`;
      const itemBg = !isLog ? 'background: #fff;' : 'background: rgba(0,0,0,0.01); border-left: 3px solid transparent;';
      const subtextOpacity = !isLog ? '0.85' : '0.5';
      
      html += `
        <li class="v2-list-item${clickableClass}" data-type="${item.type}" data-date="${dateStr}" ${onclick} style="padding: ${compact ? '8px 16px' : '10px 16px 12px'}; border-bottom: 1px solid var(--v2-border); ${itemBg}">
          <div style="display:flex; flex-direction:column; gap:2px;">
            <span class="v2-item-title" style="${titleStyle}">${escapeHtml(item.title)}</span>
            ${item.subtext ? `<span style="font-size: 11px; color: var(--v2-text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; opacity: ${subtextOpacity};">↳ ${escapeHtml(item.subtext)}</span>` : ''}
          </div>
          <div class="v2-history-item-meta">
            <span class="v2-history-badge ${typeClass}" style="${isLog ? 'opacity: 0.7;' : ''}">${typeLabel}</span>
            <span class="v2-history-badge ${statusClass}" style="${isLog ? 'background: rgba(0,0,0,0.05); color: #666;' : ''}">${statusLabel}</span>
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
          <span class="v2-section-label">이력 요약</span>
          <div class="v2-rail-card v2-rail-card-accent">
            <span class="v2-item-title">완료된 작업 ${allTasks.length}건</span>
            <span class="v2-item-meta">오늘 ${todayTasks.length}건 / 최근 ${recentTasks.length}건</span>
            <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid rgba(45, 90, 39, 0.1);">
              <span class="v2-item-title" style="font-size:12px; opacity:0.8;">참고 세션 로그 ${allLogs.length}건</span>
              <span class="v2-item-meta" style="font-size:11px;">전체 누적 기록 ${totalCompleted}건</span>
            </div>
          </div>
        </section>
      </aside>

      <main class="v2-main v2-main-progress">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 24px;">
          <div>
            <span class="v2-day-label">완료 및 기록</span>
            <p style="margin: 6px 0 0 0; font-size: 13px; color: var(--v2-text-muted); line-height: 1.5;">
              실행된 퀘스트 결과와 기술적인 세션 로그를 구분하여 관리합니다.
            </p>
          </div>
          <div style="display:flex; gap: 4px; border: 1px solid var(--v2-border); border-radius: 4px; padding: 2px; margin-top: 4px;">
            <button class="v2-btn-inline v2-history-filter-btn" data-filter="all" onclick="window.filterHistory('all')" style="border:0; background:transparent; border-radius:3px; padding:2px 8px; font-size:11px; font-weight:600; cursor:pointer; color:var(--v2-text-muted);">전체</button>
            <button class="v2-btn-inline v2-history-filter-btn" data-filter="tasks" onclick="window.filterHistory('tasks')" style="border:0; background:transparent; border-radius:3px; padding:2px 8px; font-size:11px; font-weight:600; cursor:pointer; color:var(--v2-text-muted);">작업</button>
            <button class="v2-btn-inline v2-history-filter-btn" data-filter="logs" onclick="window.filterHistory('logs')" style="border:0; background:transparent; border-radius:3px; padding:2px 8px; font-size:11px; font-weight:600; cursor:pointer; color:var(--v2-text-muted);">로그</button>
          </div>
        </div>

        <div class="v2-mission-wrap" style="padding-bottom: 60px;">
          <!-- 1. Completed Tasks Section -->
          <span class="v2-section-label" style="color: var(--v2-primary);">완료된 작업 (Quests/Sessions)</span>
          <div class="v2-progress-stack" style="margin-bottom: 32px;">
            <div class="v2-rail-card" style="padding: 0; overflow: hidden; border-top: 2px solid var(--v2-primary);">
              ${renderHistoryList([...todayTasks, ...recentTasks], "완료된 작업이 없습니다.")}
            </div>
          </div>

          <!-- 2. Session Logs Section -->
          <span class="v2-section-label">참고 기록 / 세션 로그</span>
          <div class="v2-progress-stack" style="margin-bottom: 32px;">
            <div class="v2-rail-card" style="padding: 0; overflow: hidden; opacity: 0.9;">
              ${renderHistoryList([...todayLogs, ...recentLogs], "참가 기록이 없습니다.")}
            </div>
          </div>

          <!-- 3. Overall History Details -->
          <div style="margin-top: 40px;">
            <details style="cursor: pointer; background: var(--v2-bg-elevated); border-radius: 8px; border: 1px solid var(--v2-border); overflow: hidden;">
              <summary class="v2-item-title" style="margin:0; padding: 16px; outline: none; user-select: none; font-size: 13px;">
                전체 누적 리스트 펼치기 <span style="opacity: 0.6; font-weight: normal;">(총 ${totalCompleted}건)</span>
              </summary>
              <div style="padding: 0; border-top: 1px solid var(--v2-border);">
                ${renderHistoryList([...allTasks, ...allLogs], "데이터가 없습니다.", true)}
              </div>
            </details>
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
