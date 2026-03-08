function showDetailedList(label, title, items, formatter) {
  const bodyHtml = `
    <div class="list detailed-list-in-panel">
      ${items.map(formatter).join("")}
    </div>
  `;
  openDetailPanel(label, title, bodyHtml);
}

function renderBriefs() {
  const targetId = "briefList";
  const items = state.briefs;
  setCountBadge("briefCount", items.length);
  
  const formatter = (item) => {
    const summary = (item.content_md || "")
      .split("\n")
      .map((line) => line.trim())
      .find((line) => line && !line.startsWith("#")) || "핵심 요약이 아직 없습니다.";
    return `
      <div class="list-item candidate-item" onclick="showDetailedList('최근 브리프', '브리프 목록', state.briefs, (i) => \`
        <div class='list-item'>
          <strong>\${escapeHtml(i.title)}</strong>
          <p class='muted'>\${escapeHtml(i.content_md)}</p>
        </div>
      \`)">
        <div class="candidate-head">
          <strong>${escapeHtml(item.title)}</strong>
          <span class="candidate-rank">${escapeHtml(item.brief_type || "brief")}</span>
        </div>
        <span class="candidate-reason">${escapeHtml(summary)}</span>
      </div>
    `;
  };

  renderCappedList(targetId, items, formatter, 3, "브리프가 생성되면 여기에 정리됩니다.");
}

function renderWorkdiary() {
  const targetId = "workdiaryList";
  const items = state.workdiaryItems;
  setCountBadge("workdiaryCount", items.length);

  const formatter = (item) => `
    <div class="list-item candidate-item" onclick="showDetailedList('workdiary 상위 폴더', '폴더 목록', state.workdiaryItems, (i) => \`
      <div class='list-item'><strong>\${escapeHtml(i.name)}</strong> <span class='muted'>\${escapeHtml(i.modified_at)}</span></div>
    \`)">
      <div class="candidate-head">
        <strong>${escapeHtml(item.name)}</strong>
        <span class="candidate-rank">${escapeHtml(item.item_type || "item")}</span>
      </div>
      <span class="candidate-reason">${escapeHtml(formatDateTime(item.modified_at).slice(0, 16) || "-")}</span>
    </div>
  `;

  renderCappedList(targetId, items, formatter, 3, "workdiary를 읽으면 여기에 상위 폴더가 정리됩니다.");
}

function renderPriorityCandidates() {
  const targetId = "priorityCandidateList";
  const items = state.priorityCandidates;
  setCountBadge("priorityCandidateCount", items.length);

  const renderCandidate = (item, rank) => `
    <div class="list-item candidate-item" onclick="showDetailedList('우선 검토 후보', '프로젝트 후보 목록', state.priorityCandidates, (i) => \`
      <div class='list-item'>
        <strong>\${escapeHtml(i.name)}</strong>
        <p class='muted'>\${escapeHtml(i.priority_reason)} (Score: \${i.priority_score})</p>
      </div>
    \`)">
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
  renderCappedList(targetId, items, formatter, 4, "workdiary를 분석하면 여기에 후보가 정리됩니다.");
}

function renderPlans() {
  const current = state.currentState || {};
  
  setCountBadge("dueSoonCount", byBucket(state.plans, "dated").length);
  setCountBadge("unfinishedCount", (current.top_unfinished_summary || []).length);
  setCountBadge("shortTermCount", byBucket(state.plans, "short_term").length);
  setCountBadge("longTermCount", byBucket(state.plans, "long_term").length);
  setCountBadge("recurringCount", byBucket(state.plans, "recurring").length);

  const planFormatter = (item) => `
    <div class="list-item signal-item">
      <div class="signal-head">
        <strong>${escapeHtml(item.title)}</strong>
        <span class="session-badge verdict ${escapeHtml(item.status || "pending")}">${escapeHtml(labelStatus(item.status))}</span>
      </div>
      <span>${escapeHtml(item.due_at || labelBucket(item.bucket))}</span>
    </div>
  `;

  const makeDetailOpener = (label, title, items) => {
    return () => showDetailedList(label, title, items, planFormatter);
  };

  renderCappedList("dueSoonList", byBucket(state.plans, "dated"), (item) => `
    <div onclick="showDetailedList('기한 임박', '기한 고정 플랜', byBucket(state.plans, 'dated'), (i) => \`
      <div class='list-item'><strong>\${escapeHtml(i.title)}</strong> <span>\${escapeHtml(i.due_at)}</span></div>
    \`)" class="clickable-item">${planFormatter(item)}</div>
  `, 3, "현재 기한 압박 없음");

  renderCappedList("unfinishedList", current.top_unfinished_summary || [], (item) => `
    <div onclick="showDetailedList('어제 미완료', '미완료 핵심', state.currentState.top_unfinished_summary, (i) => \`
      <div class='list-item'><strong>\${escapeHtml(i.title)}</strong> <span>\${escapeHtml(labelStatus(i.status))}</span></div>
    \`)" class="clickable-item">${planFormatter(item)}</div>
  `, 3, "현재 이어갈 미완료 없음");

  renderCappedList("shortTermList", byBucket(state.plans, "short_term"), (item) => `
    <div onclick="showDetailedList('단기 플랜', '단기 계획', byBucket(state.plans, 'short_term'), (i) => \`
      <div class='list-item'><strong>\${escapeHtml(i.title)}</strong> <span>\${escapeHtml(labelStatus(i.status))}</span></div>
    \`)" class="clickable-item">${planFormatter(item)}</div>
  `, 3, "현재 단기 플랜 없음");

  renderCappedList("longTermList", byBucket(state.plans, "long_term"), (item) => `
    <div onclick="showDetailedList('장기 플랜', '장기 계획', byBucket(state.plans, 'long_term'), (i) => \`
      <div class='list-item'><strong>\${escapeHtml(i.title)}</strong> <span>\${escapeHtml(labelStatus(i.status))}</span></div>
    \`)" class="clickable-item">${planFormatter(item)}</div>
  `, 3, "현재 장기 플랜 없음");

  renderCappedList("recurringList", byBucket(state.plans, "recurring"), (item) => `
    <div onclick="showDetailedList('반복 플랜', '반복 계획', byBucket(state.plans, 'recurring'), (i) => \`
      <div class='list-item'><strong>\${escapeHtml(i.title)}</strong> <span>\${escapeHtml(labelStatus(i.status))}</span></div>
    \`)" class="clickable-item">${planFormatter(item)}</div>
  `, 3, "현재 반복 플랜 없음");
}

function renderSessions() {
  const targetId = "recentSessionList";
  const items = state.sessions;
  setCountBadge("recentSessionCount", items.length);

  const formatter = (item) => `
    <div class="list-item candidate-item" onclick="openSessionDetail('${item.id}')">
      <div class="candidate-head">
        <strong>${escapeHtml(item.title || item.project_key)}</strong>
        <span class="candidate-rank">${escapeHtml(item.agent_name)}</span>
      </div>
      <span class="candidate-reason">${escapeHtml(formatRecentLabel(item.updated_at))}</span>
    </div>
  `;

  renderCappedList(targetId, items, formatter, 4, "최근 세션이 없습니다.");
}

function renderPlanChanges() {
  const current = state.currentState || {};
  const entries = [];

  const latestDecision = current.latest_decision_summary || {};
  if (latestDecision.title) {
    entries.push({
      badgeText: "방금 판정",
      badgeClass: "partial",
      title: latestDecision.title.replace(/^Quest verdict:\s*/i, ""),
      secondary: latestDecision.impact_summary || latestDecision.reason || "-",
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

  renderCappedList("planChangeSummary", entries, formatter, 3);
}
