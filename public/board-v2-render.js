function renderList(items, emptyText, metaFormatter) {
  if (!items || !items.length) {
    return `<p class="v2-empty">${escapeHtml(emptyText)}</p>`;
  }

  return `
    <ul class="v2-list">
      ${items.map((item) => {
        const meta = metaFormatter(item);
        const clickableClass = item.description || item.reason || item.impact_summary ? " v2-modal-clickable" : "";
        const onclick = clickableClass 
          ? `onclick="window.boardV2OpenModal('${escapeHtml(item.title)}', '${escapeHtml(item.description || item.reason || item.impact_summary || "")}')"` 
          : "";
        
        // Plan bucket badge logic
        const bucket = item.bucket || item.status;
        const bucketLabel = formatPlanLabel(bucket);
        const hasBucketLabel = bucket && bucketLabel && bucket !== 'active' && bucket !== 'done';
        const bucketClass = hasBucketLabel ? ` v2-plan-badge-${bucket}` : "";

        return `
          <li class="v2-list-item${clickableClass}" ${onclick}>
            <div style="display:flex; align-items:flex-start; gap:0;">
              ${hasBucketLabel ? `<span class="v2-plan-badge${bucketClass}">${escapeHtml(bucketLabel)}</span>` : ""}
              <span class="v2-item-title" style="flex:1;">${escapeHtml(item.title)}</span>
            </div>
            <span class="v2-item-meta${meta.isDue ? ' -due' : ''}">${escapeHtml(meta.text)}</span>
          </li>
        `;
      }).join("")}
    </ul>
  `;
}

function renderBriefList(items) {
  if (!items || !items.length) {
    return `<p class="v2-empty">브리프가 없습니다.</p>`;
  }

  return `
    <ul class="v2-list v2-list-compact">
      ${items.map((item) => {
        const title = item.title || "브리프";
        const content = item.content_md || "내용이 없습니다.";
        return `
          <li class="v2-list-item v2-modal-clickable" onclick="window.boardV2OpenModal('${escapeHtml(title)}', '${escapeHtml(content)}')">
            <span class="v2-item-title">${escapeHtml(title)}</span>
            <span class="v2-item-meta">${escapeHtml(summarizeBrief(item))}</span>
          </li>
        `;
      }).join("")}
    </ul>
  `;
}

function renderSessionList(items) {
  if (!items || !items.length) {
    return `<p class="v2-empty">최근 세션이 없습니다.</p>`;
  }

  return `
    <ul class="v2-list v2-list-compact">
      ${items.map((item) => `
        <li class="v2-list-item">
          <span class="v2-item-title">${escapeHtml(item.title || item.project_key || "세션")}</span>
          <span class="v2-item-meta">${escapeHtml(item.agent_name || "agent")} · ${escapeHtml(formatSessionStatus(item.status))}</span>
        </li>
      `).join("")}
    </ul>
  `;
}

function renderQuickInputSection() {
  return `
    <section class="v2-quick-input-card">
      <span class="v2-section-label">빠른 입력</span>
      <textarea id="v2QuickInput" class="v2-quick-input-textarea" 
        placeholder="오늘 할 일, 기한, 아이디어 등을 자유롭게 입력하세요 (Enter: 전송)"
        oninput="window.boardV2SyncQuickInputDraft()">${escapeHtml(_quickInputDraft)}</textarea>
      <div class="v2-quick-input-actions">
        <button type="button" class="v2-btn v2-btn-primary v2-btn-inline" onclick="window.boardV2SubmitQuickInput()">전송</button>
      </div>
    </section>
  `;
}

function renderMorning(state) {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const mission = pickMainMission(state);
  const dueItems = pickDueItems(state);
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
        <section class="v2-rail-section">
          <span class="v2-section-label">기한 임박</span>
          <div class="v2-rail-card">
            ${renderList(dueItems, "마감 기한이 있는 항목이 없습니다.", (item) => ({ text: item.due_at || "기한 정보 없음", isDue: true }))}
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

function renderInProgress(state) {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const quest = pickCurrentQuest(state);
  const unfinishedItems = pickUnfinishedItems(state);
  const dueItems = pickDueItems(state);
  const briefs = pickBriefs(state);
  const sessions = pickSessions(state);
  const recentVerdict = pickRecentVerdict(state);
  const nextQuest = state.recommended_next_quest || state.tomorrow_first_quest?.title || "";
  const questStatus = state.quest_status_summary || {};
  const progress = state.day_progress_summary || {};

  const questTitle = quest.id || quest.title !== "현재 퀘스트가 없습니다."
    ? quest.title
    : state.main_mission_title || "현재 퀘스트가 없습니다.";

  const verdictTitle = recentVerdict?.title || "최근 판단";
  const verdictContent = recentVerdict?.reason || recentVerdict?.impact_summary || "최근 판단 요약이 없습니다.";
  const verdictHtml = recentVerdict
    ? `
      <div class="v2-rail-card v2-modal-clickable" onclick="window.boardV2OpenModal('${escapeHtml(verdictTitle)}', '${escapeHtml(verdictContent)}')">
        <span class="v2-item-title">${escapeHtml(verdictTitle)}</span>
        <span class="v2-item-meta">${escapeHtml(verdictContent)}</span>
      </div>
    `
    : `<div class="v2-rail-card"><p class="v2-empty">최근 판단이 없습니다.</p></div>`;

  const nextQuestHtml = nextQuest
    ? `<div class="v2-inline-card"><span class="v2-inline-label">다음 퀘스트 후보</span><strong>${escapeHtml(nextQuest)}</strong></div>`
    : `<div class="v2-inline-card"><span class="v2-inline-label">다음 퀘스트 후보</span><strong>아직 제안이 없습니다.</strong></div>`;

  const manualEvalHtml = (id) => `
    <div class="v2-inline-card" style="margin-top: 12px;">
      <span class="v2-inline-label">수동 판정 (강제 종료)</span>
      <div class="v2-start-actions" style="margin-top: 0;">
        <button type="button" class="v2-btn v2-btn-secondary" onclick="window.boardV2EvaluateQuest('${escapeHtml(id)}', 'done')">완료</button>
        <button type="button" class="v2-btn v2-btn-secondary" onclick="window.boardV2EvaluateQuest('${escapeHtml(id)}', 'partial')">부분</button>
        <button type="button" class="v2-btn v2-btn-secondary" onclick="window.boardV2EvaluateQuest('${escapeHtml(id)}', 'hold')">보류</button>
        <button type="button" class="v2-btn v2-btn-secondary" style="border-color: rgba(217, 119, 6, 0.3); color: var(--v2-amber);" 
          onclick="window.boardV2DeferQuest()">단기 플랜으로 미루기</button>
      </div>
    </div>
  `;

  let reportFormHtml = "";
  if (questStatus.is_pending) {
    reportFormHtml = `
      <section class="v2-form-card">
        <span class="v2-section-label">결과 보고</span>
        <div class="v2-info-box">
          AI가 작업 결과를 분석하고 있습니다...
        </div>
        ${manualEvalHtml(quest.id || state.current_quest_id)}
      </section>
    `;
  } else if (quest.id) {
    // 퀘스트가 바뀌었으면 초안 초기화
    if (_reportDraft.questId !== quest.id) {
      _reportDraft.questId = quest.id;
      _reportDraft.summary = "";
      _reportDraft.assessment = "partial";
    }

    reportFormHtml = `
      <section class="v2-form-card">
        <span class="v2-section-label">결과 보고</span>
        <div class="v2-inline-card">
          <div class="v2-form-group">
            <label class="v2-form-label" for="v2WorkSummary">작업 내용</label>
            <textarea id="v2WorkSummary" class="v2-textarea" placeholder="무엇을 완료했나요?" 
              oninput="window.boardV2SyncDraft()">${escapeHtml(_reportDraft.summary)}</textarea>
          </div>
          <div class="v2-form-group">
            <label class="v2-form-label" for="v2SelfAssessment">자가 평가</label>
            <select id="v2SelfAssessment" class="v2-select" onchange="window.boardV2SyncDraft()">
              <option value="done" ${_reportDraft.assessment === "done" ? "selected" : ""}>완료 (목표 달성)</option>
              <option value="partial" ${_reportDraft.assessment === "partial" ? "selected" : ""}>부분 완료 (진전 있음)</option>
              <option value="hold" ${_reportDraft.assessment === "hold" ? "selected" : ""}>보류 (중단/방향 전환)</option>
            </select>
          </div>
          <div class="v2-form-actions">
            <button type="button" class="v2-btn v2-btn-primary" onclick="window.boardV2ReportQuest('${escapeHtml(quest.id)}')">보고 및 판정 요청</button>
          </div>
        </div>

        ${manualEvalHtml(quest.id)}
      </section>
    `;
  }

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

        <section class="v2-rail-section">
          <span class="v2-section-label">최근 브리프</span>
          <div class="v2-rail-card">
            ${renderBriefList(briefs)}
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

          ${reportFormHtml}
        </div>
      </main>

      <aside class="v2-rail v2-rail-right">
        ${renderQuickInputSection()}

        <section class="v2-rail-section">
          <span class="v2-section-label">진행 상태</span>
          <div class="v2-rail-card">
            <span class="v2-item-title">${questStatus.is_pending ? "판정 대기 중" : "진행 중"}</span>
            <span class="v2-item-meta">${escapeHtml(questStatus.preliminary_reason || state.day_phase_reason || "현재 퀘스트 중심으로 진행 중입니다.")}</span>
          </div>
        </section>

        <section class="v2-rail-section">
          <span class="v2-section-label">전체 계획 및 보류</span>
          <div class="v2-rail-card">
            ${renderList(unfinishedItems, "남은 계획 항목이 없습니다.", (item) => ({ text: item.project_key || "No Project", isDue: false }))}
          </div>
        </section>

        <section class="v2-rail-section">
          <span class="v2-section-label">기한 압박</span>
          <div class="v2-rail-card">
            ${renderList(dueItems, "마감 기한이 있는 항목이 없습니다.", (item) => ({ text: item.due_at || "기한 정보 없음", isDue: true }))}
          </div>
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

  const tomorrowCard = tomorrowFirst && tomorrowFirst.title
    ? `
      <div class="v2-start-card">
        <span class="v2-start-badge">내일 첫 퀘스트</span>
        <span class="v2-item-title">${escapeHtml(tomorrowFirst.title)}</span>
        <span class="v2-item-meta">${escapeHtml(tomorrowFirst.reason || "")}</span>
        <div class="v2-start-actions" style="margin-top: 14px;">
          <button class="v2-btn v2-btn-primary" type="button" 
            onclick="window.boardV2ConfirmStartingPoint('${escapeHtml(tomorrowFirst.title)}', '${escapeHtml(tomorrowFirst.reason || "")}', '${escapeHtml(tomorrowFirst.source || "suggestion")}')"
            ${confirmed && confirmed.title ? "disabled" : ""}>
            ${confirmed && confirmed.title ? "이미 확정됨" : "이 제안 확정"}
          </button>
        </div>
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
          <span class="v2-section-label">기한 압박</span>
          <div class="v2-rail-card">
            ${renderList(dueItems, "마감 기한이 있는 항목이 없습니다.", (item) => ({ text: item.due_at || "기한 정보 없음", isDue: true }))}
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
        ${renderQuickInputSection()}

        <section class="v2-rail-section">
          <span class="v2-section-label">확정된 시작점</span>
          ${confirmedHtml}
        </section>

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

