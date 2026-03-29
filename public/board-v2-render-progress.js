function renderInProgress(state) {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const quest = pickCurrentQuest(state);
  const recentVerdict = pickRecentVerdict(state);
  const nextQuest = state.recommended_next_quest || state.tomorrow_first_quest?.title || "";
  const questStatus = state.quest_status_summary || {};

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
    : `<div class="v2-rail-card"><p class="v2-empty" style="margin:0;">최근 판단이 없습니다.</p></div>`;

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
    if (_reportDraft.questId !== quest.id) {
      _reportDraft.questId = quest.id;
      _reportDraft.summary = "";
      _reportDraft.assessment = "partial";
    }

    reportFormHtml = `
      <section class="v2-form-card">
        <span class="v2-section-label">진행 결과 보고</span>
        <div class="v2-inline-card" style="background: transparent; border: none; padding: 0;">
          <div class="v2-form-group">
            <label class="v2-form-label" for="v2WorkSummary">작업 내용 입력</label>
            <textarea id="v2WorkSummary" class="v2-textarea" placeholder="무엇을 완료했나요?" 
              oninput="window.boardV2SyncDraft()" style="min-height: 100px;">${escapeHtml(_reportDraft.summary)}</textarea>
          </div>
          <div class="v2-form-group" style="margin-top: 16px;">
            <label class="v2-form-label" for="v2SelfAssessment">자가 평가</label>
            <select id="v2SelfAssessment" class="v2-select" onchange="window.boardV2SyncDraft()">
              <option value="done" ${_reportDraft.assessment === "done" ? "selected" : ""}>완료 (목표 달성)</option>
              <option value="partial" ${_reportDraft.assessment === "partial" ? "selected" : ""}>부분 완료 (진전 있음)</option>
              <option value="hold" ${_reportDraft.assessment === "hold" ? "selected" : ""}>보류 (중단/방향 전환)</option>
            </select>
          </div>
          <div class="v2-form-actions" style="margin-top: 24px;">
            <button type="button" class="v2-btn v2-btn-primary" style="font-size:16px; padding:12px 24px;" onclick="window.boardV2ReportQuest('${escapeHtml(quest.id)}')">보고하고 다음으로 진행</button>
          </div>
        </div>

        ${manualEvalHtml(quest.id)}
      </section>
    `;
  } else {
    reportFormHtml = `<p class="v2-empty" style="text-align:center;">진행 중인 퀘스트가 없어 결과 보고 기능을 사용할 수 없습니다.</p>`;
  }

  // Focus Mode Layout: 1-Column Center, No Distracting Sidebar
  root.innerHTML = `
    <div class="v2-layout" style="display: flex; flex-direction: column; align-items: center; justify-content: flex-start; max-width: 900px; margin: 0 auto; padding-top: 20px;">
      
      <main class="v2-main v2-main-progress" style="width: 100%; border: 1px solid var(--v2-border); border-radius: 12px; background: var(--v2-layer-1); padding: 40px; box-shadow: 0 8px 32px rgba(0,0,0,0.4);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 24px;">
          <span class="v2-day-label" style="margin: 0; color: var(--v2-brand);">현재 집중 퀘스트 (Focus Mode)</span>
          <span class="v2-item-meta" style="font-size:14px;">${questStatus.is_pending ? "판정 대기 중" : "진행 중"}</span>
        </div>
        
        <h1 class="v2-mission-title v2-quest-title" style="font-size: 32px; line-height: 1.4; color: #fff; margin-bottom: 32px; word-break: keep-all;">${escapeHtml(questTitle)}</h1>

        <div class="v2-progress-stack" style="gap: 20px;">
          ${quest.whyNow ? `
            <div class="v2-why-now-box" style="font-size: 16px; padding: 16px;">
              <span class="v2-why-now-label">실행 이유 / 맥락</span>
              ${escapeHtml(quest.whyNow)}
            </div>
          ` : ""}
          <div class="v2-inline-card" style="font-size: 18px; padding: 20px; border-left: 4px solid var(--v2-brand);">
            <span class="v2-inline-label">완료 기준</span>
            <strong style="font-weight: 500;">${escapeHtml(quest.completionCriteria)}</strong>
          </div>
          <div class="v2-inline-card" style="font-size: 16px; padding: 16px;">
            <span class="v2-inline-label">재시작 포인트</span>
            <strong style="color: var(--v2-foreground); font-weight: normal;">${escapeHtml(quest.restartPoint)}</strong>
          </div>
        </div>

        <div style="margin-top: 40px;">
          ${reportFormHtml}
        </div>
      </main>

      <div style="width: 100%; display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 24px;">
        <section class="v2-rail-section" style="margin: 0;">
          <span class="v2-section-label">최근 판단 참조</span>
          ${verdictHtml}
        </section>
        <section class="v2-rail-section" style="margin: 0;">
          <span class="v2-section-label">다음에 이어질 퀘스트</span>
          <div class="v2-rail-card" style="padding: 16px;">
            ${nextQuestHtml}
          </div>
        </section>
      </div>
    </div>
  `;
}
