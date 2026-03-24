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
        return `
          <li class="v2-list-item${clickableClass}" ${onclick}>
            <span class="v2-item-title">${escapeHtml(item.title)}</span>
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
          <span class="v2-section-label">미완료 항목</span>
          <div class="v2-rail-card">
            ${renderList(unfinishedItems, "미완료 항목이 없습니다.", (item) => ({ text: formatPlanLabel(item.bucket), isDue: false }))}
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
          <span class="v2-section-label">미완료 항목</span>
          <div class="v2-rail-card">
            ${renderList(unfinishedItems, "미완료 항목이 없습니다.", (item) => ({ text: formatPlanLabel(item.bucket), isDue: false }))}
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
          <span class="v2-section-label">남은 전략</span>
          <div class="v2-rail-card">
            ${renderList(unfinishedItems, "미완료 항목이 없습니다.", (item) => ({ text: formatPlanLabel(item.status || item.bucket), isDue: false }))}
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
