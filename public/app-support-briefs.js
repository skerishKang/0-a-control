/**
 * Briefs rendering module for Classic UI
 */

function normalizeBriefContent(value) {
  return String(value || "")
    .replace(/\bNone\b/g, "없음")
    .replace(/\s+-\s+/g, "\n- ");
}

function normalizeBriefTypeLabel(value) {
  const key = String(value || "").trim().toLowerCase();
  if (!key || key === "brief") return "브리프";
  if (key === "morning_auto") return "자동 아침";
  if (key === "morning") return "아침";
  if (key === "evening") return "저녁";
  return value || "브리프";
}

function renderBriefsSection(state) {
  const targetId = "briefList";
  const parentPanel = document.getElementById(targetId)?.parentElement;
  if (!parentPanel) return;
  parentPanel.classList.add("panel-browsing");

  const items = state.briefs || [];
  setCountBadge("briefCount", items.length);

  const formatter = (item) => {
    const summary = normalizeBriefContent(item.content_md || "")
      .split("\n")
      .map((line) => line.trim())
      .find((line) => line && !line.startsWith("#")) || "핵심 요약이 아직 없습니다.";
    return `
      <div class="list-item candidate-item">
        <div class="candidate-head">
          <strong>${escapeHtml(item.title)}</strong>
          <span class="candidate-rank">${escapeHtml(normalizeBriefTypeLabel(item.brief_type))}</span>
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
        <p class='muted'>${escapeHtml(normalizeBriefContent(i.content_md))}</p>
      </div>
    `);
  };
}
