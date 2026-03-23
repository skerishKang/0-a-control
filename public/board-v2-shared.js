function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function getDayLabel() {
  const now = new Date();
  const weekdays = ["일", "월", "화", "수", "목", "금", "토"];
  const yyyy = now.getFullYear();
  const mm = String(now.getMonth() + 1).padStart(2, "0");
  const dd = String(now.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd} (${weekdays[now.getDay()]})`;
}

function formatPlanLabel(value) {
  const mapping = {
    today: "오늘",
    short_term: "단기",
    long_term: "장기",
    recurring: "반복",
    dated: "기한",
    hold: "보류",
    pending: "대기",
    partial: "부분",
    active: "진행 중",
    done: "완료",
  };
  return mapping[value] || value || "상태 미정";
}

function formatSessionStatus(value) {
  const mapping = {
    active: "진행 중",
    closed: "종료",
    stale: "정리 필요",
  };
  return mapping[value] || value || "상태 미정";
}

function summarizeBrief(brief) {
  const content = String(brief?.content_md || "")
    .replace(/\r/g, "")
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith("##"));
  return content[0] || "브리프 요약이 없습니다.";
}

function renderList(items, emptyText, metaFormatter) {
  if (!items || !items.length) {
    return `<p class="v2-empty">${escapeHtml(emptyText)}</p>`;
  }

  return `
    <ul class="v2-list">
      ${items.map((item) => `
        <li class="v2-list-item">
          <span class="v2-item-title">${escapeHtml(item.title)}</span>
          <span class="v2-item-meta${metaFormatter(item).isDue ? ' -due' : ''}">${escapeHtml(metaFormatter(item).text)}</span>
        </li>
      `).join("")}
    </ul>
  `;
}

function renderBriefList(items) {
  if (!items || !items.length) {
    return `<p class="v2-empty">브리프가 없습니다.</p>`;
  }

  return `
    <ul class="v2-list v2-list-compact">
      ${items.map((item) => `
        <li class="v2-list-item">
          <span class="v2-item-title">${escapeHtml(item.title || "브리프")}</span>
          <span class="v2-item-meta">${escapeHtml(summarizeBrief(item))}</span>
        </li>
      `).join("")}
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
