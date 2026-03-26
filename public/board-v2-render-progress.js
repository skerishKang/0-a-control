function renderInProgress(state) {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const mission = pickMainMission(state);
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
          ${mission.title && mission.title !== "주 임무가 없습니다." 
            ? `<span class="v2-mission-context" title="${escapeHtml(mission.reason)}">오늘의 주 임무: ${escapeHtml(mission.title)}</span>` 
            : ""}
          <span class="v2-section-label">현재 퀘스트</span>
          <h1 class="v2-mission-title v2-quest-title">${escapeHtml(questTitle)}</h1>

          <div class="v2-progress-stack">
            ${quest.whyNow ? `
              <div class="v2-why-now-box">
                <span class="v2-why-now-label">실행 이유 / 맥락</span>
                ${escapeHtml(quest.whyNow)}
              </div>
            ` : ""}
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
