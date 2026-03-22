/**
 * Card rendering modules for 0-a-control
 * Responsibility: UI rendering for specific card components
 */

function getActiveQuestContext(current) {
  const quests = (state?.quests) || [];
  const activeQuest = quests.find((item) => item.id === current.current_quest_id) || {};
  const metadata = activeQuest.metadata_json || {};
  return {
    quests,
    aiVerdict: metadata.ai_verdict || {},
    report: metadata.report || {},
  };
}

/**
 * Card 1. 재시작 포인트 카드
 */
function renderRestartPointCard(current) {
  const { aiVerdict } = getActiveQuestContext(current);
  const restartPointEmptyMsg = current.current_quest_id
    ? "현재 퀘스트를 수행 중입니다. 작업이 중단되거나 완료되면 복귀를 위한 핵심 지점이 여기에 기록됩니다."
    : "모든 흐름이 정상적으로 마무리되었습니다. 새로운 퀘스트로 다시 시작할 준비가 되었습니다.";

  renderList(
    "restartPointHint",
    [{
      title: current.restart_point || aiVerdict.restart_point || current.current_quest_title || "재시작 포인트를 정리하세요",
      reason: current.main_mission_title
        ? `${current.main_mission_title} 흐름으로 바로 복귀`
        : "중단된 흐름을 다시 이어갈 출발점",
    }],
    (item) => `
      <div class="list-item signal-item">
        <div class="signal-head">
          <strong>${escapeHtml(item.title)}</strong>
          <span class="session-badge verdict partial">재시작</span>
        </div>
        <span>${escapeHtml(item.reason)}</span>
      </div>
    `,
    restartPointEmptyMsg
  );
}

/**
 * Card 2. 다음 퀘스트 카드
 */
function renderNextQuestCard(current) {
  const nextQuestEmptyMsg = current.current_quest_id
    ? "현재 진행 중인 퀘스트를 마친 후, 보고를 통해 다음 권장 행동을 제안받으세요."
    : "현재 잡혀 있는 퀘스트가 없습니다. 주 임무 달성을 위해 실행 가능한 가장 작은 행동을 정의하세요.";

  renderList(
    "nextQuestHint",
    current.recommended_next_quest
      ? [{
        title: current.recommended_next_quest,
        reason: current.restart_point || current.latest_decision_summary?.impact_summary || "현재 흐름을 이어가기 위한 다음 작은 행동",
      }]
      : [],
    (item) => `
      <div class="list-item signal-item next-quest-item">
        <div class="signal-head">
          <strong>${escapeHtml(item.title)}</strong>
          <span class="session-badge verdict partial">다음</span>
        </div>
        <span>${escapeHtml(item.reason)}</span>
      </div>
    `,
    nextQuestEmptyMsg
  );
}

/**
 * Card 3. 막힘 / 주의점 카드
 */
function renderCautionCard(current, nextCore, cautionText) {
  const statusSummary = current.quest_status_summary || {};
  const cautionEmptyMsg = statusSummary.is_pending
    ? "현재 퀘스트가 외부 판정 대기 중입니다. 흐름이 끊기지 않도록 직전 맥락을 유지하세요."
    : "현재 감지된 특별한 지연 신호나 위험 요소가 없습니다. 주 임무의 핵심 경로를 따라가세요.";

  renderList(
    "cautionHint",
    [{
      title: nextCore ? nextCore.title : current.current_quest_title || "현재 퀘스트 흐름 유지",
      reason: cautionText,
    }],
    (item) => `
      <div class="list-item signal-item">
        <div class="signal-head">
          <strong>${escapeHtml(item.title)}</strong>
          <span class="session-badge verdict hold">주의</span>
        </div>
        <span>${escapeHtml(item.reason)}</span>
      </div>
    `,
    cautionEmptyMsg
  );
}

/**
 * Card 4. 최근 판정 카드
 */
function renderRecentVerdictCard(current) {
  const { quests, aiVerdict, report } = getActiveQuestContext(current);
  const recentVerdict = current.recent_verdict || {};
  const statusSummary = current.quest_status_summary || {};
  const recentVerdictTarget = document.getElementById("recentVerdict");
  if (!recentVerdictTarget) return;
  recentVerdictTarget.parentElement.classList.add("panel-browsing");

  const renderDetail = () => {
    const detailHtml = aiVerdict.verdict
      ? `
        <div class="detail-section"><strong>AI 판정</strong><p>${escapeHtml(labelStatus(aiVerdict.verdict))}</p></div>
        <div class="detail-section"><strong>판정 이유</strong><p>${escapeHtml(aiVerdict.reason || "-")}</p></div>
        <div class="detail-section"><strong>재시작 지점</strong><p>${escapeHtml(aiVerdict.restart_point || "-")}</p></div>
        <div class="detail-section"><strong>다음 퀘스트</strong><p>${escapeHtml(aiVerdict.next_hint || "-")}</p></div>
        <div class="detail-section"><strong>계획 반영</strong><p>${escapeHtml(aiVerdict.plan_impact || "-")}</p></div>
        <div class="detail-section"><strong>사용자 보고</strong><p>${escapeHtml(report.work_summary || "-")}</p></div>
      `
      : `<p class="muted">아직 상세 판정이 없습니다.</p>`;
    openDetailPanel("최근 판정 상세", recentVerdict.title || "판정", detailHtml);
  };

  if (statusSummary.is_awaiting_external_verdict) {
    recentVerdictTarget.innerHTML = `
      <div class="verdict-card-main">
        <div class="signal-head">
          <strong>${escapeHtml(current.current_quest_title || "퀘스트")}</strong>
          <span class="session-badge verdict pending">Awaiting</span>
        </div>
        <span class="verdict-reason-preview muted" style="font-size: 0.85rem; opacity: 0.85;">${escapeHtml(statusSummary.preliminary_reason || "외부 에이전트의 응답을 기다리고 있습니다.")}</span>
      </div>
    `;
    recentVerdictTarget.onclick = null;
    recentVerdictTarget.parentElement.classList.remove("panel-browsing");
  } else if (recentVerdict.title) {
    const providerStr = statusSummary.latest_verdict_provider ? ` (by ${statusSummary.latest_verdict_provider})` : "";
    recentVerdictTarget.innerHTML = `
      <div class="verdict-card-main clickable-item">
        <div class="signal-head">
          <strong>${escapeHtml(recentVerdict.title)}</strong>
          ${renderVerdictBadge(recentVerdict.status)}
        </div>
        <span class="verdict-reason-preview">${escapeHtml(summarizeVerdictReason(recentVerdict.status, aiVerdict.reason))}</span>
        <span>${escapeHtml(formatRecentLabel(recentVerdict.updated_at))}${escapeHtml(providerStr)}</span>
      </div>
    `;
    recentVerdictTarget.onclick = renderDetail;
    recentVerdictTarget.parentElement.classList.add("panel-browsing");
  } else {
    const hasQuests = (quests || []).length > 0;
    const msg = hasQuests 
      ? "활성 퀘스트가 있습니다. 완료 보고를 하면 AI가 분석한 판정 결과가 여기에 나타납니다."
      : "아직 기록된 퀘스트가 없습니다. 첫 작업을 시작하여 통제 타워의 기록을 채워보세요.";
    recentVerdictTarget.innerHTML = `<div class="list-item empty">${msg}</div>`;
    recentVerdictTarget.onclick = null;
    recentVerdictTarget.parentElement.classList.remove("panel-browsing");
  }
}

/**
 * Card 5. 오늘 판단 / 남은 핵심 카드
 */
function renderPlanChangesCard(current) {
  const target = document.getElementById("planChangeSummary");
  if (!target) return;
  target.parentElement.classList.add("panel-browsing");

  const entries = [];
  const latestDecision = current.latest_decision_summary || {};
  
  if (latestDecision.title) {
    const normalizedTitle = latestDecision.title
      .replace(/^Quest verdict:\s*/i, "")
      .replace(/^Keep current quest unfinished:\s*/i, "미완료로 남김: ")
      .replace(/^Move current quest out of today:\s*/i, "단기 플랜으로 이동: ");
    const normalizedSecondary = String(latestDecision.impact_summary || latestDecision.reason || "-")
      .replace("[today] removed -> [short_term] deferred", "오늘판에서 내리고 단기 플랜으로 넘김")
      .replace("[today] kept as unfinished", "오늘 미완료로 남김");
    entries.push({
      badgeText: "방금 판정",
      badgeClass: "partial",
      title: normalizedTitle,
      secondary: normalizedSecondary,
    });
  }

  (current.top_unfinished_summary || []).slice(0, 2).forEach((item) => {
    entries.push({
      badgeText: labelBucket(item.bucket),
      badgeClass: item.status || "pending",
      title: `남은 핵심: ${item.title}`,
      secondary: labelStatus(item.status),
    });
  });

  const formatter = (item) => `
    <div class="list-item signal-item">
      <div class="signal-head">
        <strong>${escapeHtml(item.title)}</strong>
        <span class="session-badge verdict ${escapeHtml(item.badgeClass || "partial")}">${escapeHtml(item.badgeText || "")}</span>
      </div>
      <span>${escapeHtml(item.secondary || "-")}</span>
    </div>
  `;
  
  const cappedFormatter = (item) => `<div class="clickable-item">${formatter(item)}</div>`;
  
  target.onclick = () => {
    showDetailedList("오늘 판단 / 남은 핵심", "상세 내역", entries, formatter);
  };

  renderCappedList("planChangeSummary", entries, cappedFormatter, 3, "오늘 진행된 핵심 결정이나 판정 이력이 아직 없습니다. 작업을 통해 흐름을 만들어보세요.");
}

function selectCalendarDate(dateStr) {
  state.selectedDate = dateStr;
  renderCalendarCard(state.plans, state.selectedDate);

  const summaryEl = document.getElementById("calendarSummary");
  if (!summaryEl) return;

  const datedPlans = byBucket(state.plans, "dated");
  const selectedPlans = datedPlans.filter(p => p.due_at && p.due_at.startsWith(dateStr));

  if (selectedPlans.length > 0) {
    summaryEl.textContent = `${dateStr} 일정: ${selectedPlans.length}개 (클릭하여 상세보기)`;
    summaryEl.classList.add("is-actionable");
    summaryEl.onclick = () => {
      const title = `${dateStr} 일정`;
      const label = "계획 달력 상세";
      showDetailedList(label, title, selectedPlans, (p) => `
        <div class="list-item signal-item">
          <div class="signal-head">
            <strong>${escapeHtml(p.title)}</strong>
            <span class="session-badge verdict ${escapeHtml(p.status || "pending")}">${escapeHtml(labelStatus(p.status))}</span>
          </div>
          <span class="muted" style="font-size: 0.85rem;">${escapeHtml(p.due_at)}</span>
        </div>
      `);
    };
  } else {
    summaryEl.textContent = `${dateStr}일에는 예정된 고정 일정이 없습니다.`;
    summaryEl.classList.remove("is-actionable");
    summaryEl.onclick = null;
  }
}

/**
 * Card 6. 계획 달력 카드
 */
function renderCalendarCard(plans, selectedDate) {
  const container = document.getElementById("calendarContainer");
  const summaryEl = document.getElementById("calendarSummary");
  if (!container) return;
  container.parentElement.classList.add("panel-browsing");

  const today = new Date();
  const year = today.getFullYear();
  const month = today.getMonth();
  const todayStr = today.toISOString().split('T')[0];

  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const prevMonthLastDay = new Date(year, month, 0);

  const startDay = firstDay.getDay(); // 0 (Sun) to 6 (Sat)
  const totalDays = lastDay.getDate();

  let html = `
    <div class="calendar-header">
      <span class="calendar-month">${year}년 ${month + 1}월</span>
    </div>
    <div class="calendar-grid">
      <div class="calendar-weekday">일</div>
      <div class="calendar-weekday">월</div>
      <div class="calendar-weekday">화</div>
      <div class="calendar-weekday">수</div>
      <div class="calendar-weekday">목</div>
      <div class="calendar-weekday">금</div>
      <div class="calendar-weekday">토</div>
  `;

  // Previous month days
  for (let i = startDay - 1; i >= 0; i--) {
    html += `<div class="calendar-day prev-month">${prevMonthLastDay.getDate() - i}</div>`;
  }

  // Current month days
  const datedPlans = byBucket(plans, "dated");
  
  for (let i = 1; i <= totalDays; i++) {
    const currentDayDate = new Date(year, month, i);
    const dateStr = currentDayDate.toISOString().split('T')[0];
    const dayPlans = datedPlans.filter(p => p.due_at && p.due_at.startsWith(dateStr));
    const hasPlans = dayPlans.length > 0;
    const isToday = dateStr === todayStr;
    const isSelected = dateStr === selectedDate;

    html += `
      <div class="calendar-day ${isToday ? 'is-today' : ''} ${isSelected ? 'is-selected' : ''} ${hasPlans ? 'has-plans' : ''}" 
           onclick="selectCalendarDate('${dateStr}')">
        <span>${i}</span>
        ${hasPlans ? `<div class="plan-count-hint">${dayPlans.length}</div>` : ''}
      </div>
    `;
  }

  html += `</div>`;
  container.innerHTML = html;

  if (!summaryEl) return;
  const effectiveDate = selectedDate || todayStr;
  const selectedPlans = datedPlans.filter((p) => p.due_at && p.due_at.startsWith(effectiveDate));
  summaryEl.hidden = false;

  if (selectedPlans.length > 0) {
    summaryEl.textContent = `${effectiveDate} 일정: ${selectedPlans.length}개 (클릭하여 상세보기)`;
    summaryEl.classList.add("is-actionable");
    summaryEl.onclick = () => {
      showDetailedList("계획 달력 상세", `${effectiveDate} 일정`, selectedPlans, (p) => `
        <div class="list-item signal-item">
          <div class="signal-head">
            <strong>${escapeHtml(p.title)}</strong>
            <span class="session-badge verdict ${escapeHtml(p.status || "pending")}">${escapeHtml(labelStatus(p.status))}</span>
          </div>
          <span class="muted" style="font-size: 0.85rem;">${escapeHtml(p.due_at)}</span>
        </div>
      `);
    };
  } else {
    summaryEl.textContent = `${effectiveDate} 일정: 0개`;
    summaryEl.classList.remove("is-actionable");
    summaryEl.onclick = null;
  }
}
