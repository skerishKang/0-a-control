// ── Read-only Ops Panel ──
function renderOpsSection(data) {
  const section = document.createElement("section");
  section.className = "v2-rail-section";

  const label = document.createElement("span");
  label.className = "v2-section-label";
  label.textContent = "운영 요약";
  section.appendChild(label);

  const card = document.createElement("div");
  card.className = "v2-rail-card";

  if (!data) {
    const empty = document.createElement("p");
    empty.className = "v2-empty";
    empty.textContent = "운영 요약을 불러오지 못했습니다";
    card.appendChild(empty);
    section.appendChild(card);
    return section;
  }

  const list = document.createElement("ul");
  list.className = "v2-list v2-list-compact";

  const addRow = (fieldLabel, value) => {
    if (value === null || value === undefined) return;
    if (typeof value === "object") return;

    const li = document.createElement("li");
    li.className = "v2-list-item";

    const labelSpan = document.createElement("span");
    labelSpan.className = "v2-item-meta";
    labelSpan.textContent = fieldLabel + ":";

    const valueSpan = document.createElement("span");
    valueSpan.className = "v2-item-title";
    valueSpan.textContent = String(value);

    li.appendChild(labelSpan);
    li.appendChild(valueSpan);
    list.appendChild(li);
  };

  if (data.ok !== undefined) {
    addRow("OK", data.ok ? "예" : "아니오");
  }

  if (data.source_status) {
    if (typeof data.source_status === "object") {
      if (data.source_status.github !== undefined) {
        addRow("GitHub", String(data.source_status.github));
      }
      if (data.source_status.classifier !== undefined) {
        addRow("분류기", String(data.source_status.classifier));
      }
    }
  }

  if (data.counts && typeof data.counts === "object") {
    Object.entries(data.counts).forEach(([key, value]) => {
      if (value !== null && value !== undefined && !isNaN(Number(value))) {
        addRow(key.replace(/_/g, " "), Number(value));
      }
    });
  }

  if (data.open_issues && Array.isArray(data.open_issues)) {
    addRow("오픈 이슈", data.open_issues.length);
  }

  if (data.open_pull_requests && Array.isArray(data.open_pull_requests)) {
    addRow("오픈 PR", data.open_pull_requests.length);
  }

  if (data.recent_closed_pull_requests && Array.isArray(data.recent_closed_pull_requests)) {
    addRow("최근 닫힌 PR", data.recent_closed_pull_requests.length);
  }

  if (data.generated_at) {
    addRow("생성", new Date(data.generated_at).toLocaleString("ko-KR", { timeZone: "Asia/Seoul" }));
  }

  if (list.children.length === 0) {
    const empty = document.createElement("p");
    empty.className = "v2-empty";
    empty.textContent = "정보 없음";
    card.appendChild(empty);
  } else {
    card.appendChild(list);
  }

  section.appendChild(card);
  return section;
}

function injectOpsSection(data) {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const existing = document.getElementById("v2-ops-container");
  if (existing) existing.remove();

  const container = document.createElement("div");
  container.id = "v2-ops-container";
  container.appendChild(renderOpsSection(data));

  const layout = root.querySelector(".v2-layout");
  if (layout) {
    layout.appendChild(container);
    return;
  }

  root.appendChild(container);
}

// Expose globally for board-v2.js to call
window.injectOpsSection = injectOpsSection;