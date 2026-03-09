/**
 * Support Grid rendering module
 */

function renderSupportGrid(state) {
  renderPlansSection(state);
  renderSessionsSection(state);
  renderBriefsSection(state);
  renderWorkdiarySection(state);
  renderPriorityCandidatesSection(state);
}

function renderPlansSection(state) {
  const current = state.currentState || {};
  const plans = state.plans || [];
  const markAsBrowsing = (id) => document.getElementById(id)?.parentElement.classList.add('panel-browsing');

  markAsBrowsing('dueSoonList');
  markAsBrowsing('unfinishedList');
  markAsBrowsing('shortTermList');
  markAsBrowsing('longTermList');
  markAsBrowsing('recurringList');

  setCountBadge("dueSoonCount", byBucket(plans, "dated").length);
  setCountBadge("unfinishedCount", (current.top_unfinished_summary || []).length);
  setCountBadge("shortTermCount", byBucket(plans, "short_term").length);
  setCountBadge("longTermCount", byBucket(plans, "long_term").length);
  setCountBadge("recurringCount", byBucket(plans, "recurring").length);

  const planFormatter = (item) => `
    <div class="list-item signal-item">
      <div class="signal-head">
        <strong>${escapeHtml(item.title)}</strong>
        <span class="session-badge verdict ${escapeHtml(item.status || "pending")}">${escapeHtml(labelStatus(item.status))}</span>
      </div>
      <span>${escapeHtml(item.due_at || labelBucket(item.bucket))}</span>
    </div>
  `;

  const detailFormatter = (secondary) => (i) => `
    <div class='list-item'><strong>${escapeHtml(i.title)}</strong> <span>${escapeHtml(secondary(i))}</span></div>
  `;

  renderCappedList("dueSoonList", byBucket(plans, "dated"), planFormatter, 3, "이번 달 예정된 고정 기한 일정이 없습니다.");
  document.getElementById("dueSoonList")?.parentElement?.addEventListener("click", () => {
    showDetailedList("기한 임박", "기한 고정 플랜", byBucket(state.plans, "dated"), detailFormatter((i) => i.due_at));
  }, { once: true });

  renderCappedList("unfinishedList", current.top_unfinished_summary || [], planFormatter, 3, "이전 세션에서 이월된 미완료 항목이 없습니다.");
  document.getElementById("unfinishedList")?.parentElement?.addEventListener("click", () => {
    showDetailedList("어제 미완료", "미완료 핵심", state.currentState.top_unfinished_summary || [], detailFormatter((i) => labelStatus(i.status)));
  }, { once: true });

  renderCappedList("shortTermList", byBucket(plans, "short_term"), planFormatter, 3, "현재 집중해야 할 단기 계획이 비어 있습니다.");
  document.getElementById("shortTermList")?.parentElement?.addEventListener("click", () => {
    showDetailedList("단기 플랜", "단기 계획", byBucket(state.plans, "short_term"), detailFormatter((i) => labelStatus(i.status)));
  }, { once: true });

  renderCappedList("longTermList", byBucket(plans, "long_term"), planFormatter, 3, "장기적 관점에서 준비 중인 프로젝트가 없습니다.");
  document.getElementById("longTermList")?.parentElement?.addEventListener("click", () => {
    showDetailedList("장기 플랜", "장기 계획", byBucket(state.plans, "long_term"), detailFormatter((i) => labelStatus(i.status)));
  }, { once: true });

  renderCappedList("recurringList", byBucket(plans, "recurring"), planFormatter, 3, "주기적으로 검토할 반복 일정이 설정되지 않았습니다.");
  document.getElementById("recurringList")?.parentElement?.addEventListener("click", () => {
    showDetailedList("반복 플랜", "반복 계획", byBucket(state.plans, "recurring"), detailFormatter((i) => labelStatus(i.status)));
  }, { once: true });
}

function renderSessionsSection(state) {
  renderSessions(); // Already defined in app-sessions.js and refined
}

function renderBriefsSection(state) {
  const targetId = "briefList";
  const parentPanel = document.getElementById(targetId)?.parentElement;
  if (!parentPanel) return;
  parentPanel.classList.add("panel-browsing");

  const items = state.briefs || [];
  setCountBadge("briefCount", items.length);

  const formatter = (item) => {
    const summary = (item.content_md || "")
      .split("\n")
      .map((line) => line.trim())
      .find((line) => line && !line.startsWith("#")) || "핵심 요약이 아직 없습니다.";
    return `
      <div class="list-item candidate-item">
        <div class="candidate-head">
          <strong>${escapeHtml(item.title)}</strong>
          <span class="candidate-rank">${escapeHtml(item.brief_type || "brief")}</span>
        </div>
        <span class="candidate-reason">${escapeHtml(summary)}</span>
      </div>
    `;
  };

  renderCappedList(targetId, items, formatter, 3, "아직 생성된 브리프가 없습니다. 작업 일지가 쌓이면 AI가 요약 브리프를 생성합니다.");
  parentPanel.onclick = () => {
    showDetailedList("최근 브리프", "브리프 목록", state.briefs, (i) => `
      <div class='list-item'>
        <strong>${escapeHtml(i.title)}</strong>
        <p class='muted'>${escapeHtml(i.content_md)}</p>
      </div>
    `);
  };
}

function renderWorkdiarySection(state) {
  const targetId = "workdiaryList";
  const parentPanel = document.getElementById(targetId)?.parentElement;
  if (!parentPanel) return;
  parentPanel.classList.add("panel-browsing");

  // 자연 정렬 적용 (Intl.Collator 사용)
  const collator = new Intl.Collator(undefined, {numeric: true, sensitivity: 'base'});
  const items = (state.workdiaryItems || []).sort((a, b) => collator.compare(a.name, b.name));

  setCountBadge("workdiaryCount", items.length);

  const formatter = (item) => `
    <div class="list-item candidate-item">
      <div class="candidate-head">
        <strong>${escapeHtml(item.name)}</strong>
        <span class="candidate-rank">${escapeHtml(item.item_type || "item")}</span>
      </div>
      <span class="candidate-reason">${escapeHtml(formatDateTime(item.modified_at).slice(0, 16) || "-")}</span>
    </div>
  `;

  renderCappedList(targetId, items, formatter, 3, "workdiary 스캔 결과가 비어 있거나 경로 설정이 필요합니다.");
  parentPanel.onclick = () => {
    showDetailedList("workdiary 상위 폴더", "폴더 목록 (자연 정렬)", items, (i) => `
      <div class='list-item'><strong>${escapeHtml(i.name)}</strong> <span class='muted'>${escapeHtml(i.modified_at)}</span></div>
    `);
  };
}

function renderPriorityCandidatesSection(state) {
  const targetId = "priorityCandidateList";
  const parentPanel = document.getElementById(targetId)?.parentElement;
  if (!parentPanel) return;
  parentPanel.classList.add("panel-browsing");

  const items = state.priorityCandidates || [];
  setCountBadge("priorityCandidateCount", items.length);

  const renderCandidate = (item, rank) => `
    <div class="list-item candidate-item">
      <div class="candidate-head">
        <strong>${escapeHtml(item.name)}</strong>
        <div class="candidate-meta">
          <span class="candidate-rank">#${rank}</span>
          <span class="candidate-score">${escapeHtml(String(item.priority_score ?? 0))}</span>
        </div>
      </div>
      <span class="candidate-reason">${escapeHtml(item.priority_reason || "-")}</span>
    </div>
  `;

  const formatter = (item, index) => renderCandidate(item, index + 1);
  renderCappedList(targetId, items, formatter, 3, "우선순위를 분석할 만한 작업 데이터가 아직 충분하지 않습니다.");
  parentPanel.onclick = () => {
    showDetailedList("우선 검토 후보", "프로젝트 후보 목록", state.priorityCandidates, (i) => `
      <div class='list-item'>
        <strong>${escapeHtml(i.name)}</strong>
        <p class='muted'>${escapeHtml(i.priority_reason)} (Score: ${escapeHtml(String(i.priority_score ?? 0))})</p>
      </div>
    `);
  };
}
