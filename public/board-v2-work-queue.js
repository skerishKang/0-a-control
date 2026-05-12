// ── Read-only Work Queue Panel ──
const WORK_QUEUE_DISPLAY_ORDER = [
  "NOW",
  "NEXT",
  "LOCAL_NEEDED",
  "VALIDATION_NEEDED",
  "REVIEW_NEEDED",
  "BLOCKED",
  "LATER",
];

const WORK_QUEUE_LABELS = {
  NOW: "지금",
  NEXT: "다음",
  LOCAL_NEEDED: "로컬 필요",
  VALIDATION_NEEDED: "검증 필요",
  REVIEW_NEEDED: "검토 필요",
  BLOCKED: "막힘",
  LATER: "나중",
};

const WORK_QUEUE_PRIORITY_CLASS = {
  P0: "v2-priority-p0",
  P1: "v2-priority-p1",
  P2: "v2-priority-p2",
  P3: "v2-priority-p3",
};

function renderWorkQueueSection(data) {
  const section = document.createElement("section");
  section.className = "v2-rail-section";

  const label = document.createElement("span");
  label.className = "v2-section-label";
  label.textContent = "작업 큐";
  section.appendChild(label);

  const card = document.createElement("div");
  card.className = "v2-rail-card";

  if (!data || !data.queues) {
    const empty = document.createElement("p");
    empty.className = "v2-empty";
    empty.textContent = "작업 큐를 불러오지 못했습니다";
    card.appendChild(empty);
    section.appendChild(card);
    return section;
  }

  const queues = data.queues;
  let hasVisibleItems = false;

  WORK_QUEUE_DISPLAY_ORDER.forEach((queueKey) => {
    const items = queues[queueKey];
    if (!items || items.length === 0) return;

    hasVisibleItems = true;

    const groupLabel = document.createElement("p");
    groupLabel.className = "v2-queue-group-label";
    groupLabel.textContent = (WORK_QUEUE_LABELS[queueKey] || queueKey) + " (" + items.length + ")";
    card.appendChild(groupLabel);

    const list = document.createElement("ul");
    list.className = "v2-list v2-list-compact";

    items.forEach((item) => {
      const li = document.createElement("li");
      li.className = "v2-list-item v2-queue-item";

      // Title
      const titleSpan = document.createElement("span");
      titleSpan.className = "v2-item-title v2-queue-title";
      titleSpan.textContent = item.title || "(제목 없음)";
      li.appendChild(titleSpan);

      // Meta row: source, queue, priority
      const metaRow = document.createElement("div");
      metaRow.className = "v2-queue-meta";

      if (item.source) {
        const sourceBadge = document.createElement("span");
        sourceBadge.className = "v2-badge v2-badge-source";
        sourceBadge.textContent = item.source;
        metaRow.appendChild(sourceBadge);
      }

      const queueBadge = document.createElement("span");
      queueBadge.className = "v2-badge v2-badge-queue";
      queueBadge.textContent = WORK_QUEUE_LABELS[item.queue] || item.queue;
      metaRow.appendChild(queueBadge);

      if (item.priority) {
        const priorityBadge = document.createElement("span");
        priorityBadge.className = "v2-badge " + (WORK_QUEUE_PRIORITY_CLASS[item.priority] || "v2-priority-p2");
        priorityBadge.textContent = item.priority;
        metaRow.appendChild(priorityBadge);
      }

      if (item.execution_context) {
        const ctxBadge = document.createElement("span");
        ctxBadge.className = "v2-badge v2-badge-ctx";
        ctxBadge.textContent = item.execution_context;
        metaRow.appendChild(ctxBadge);
      }

      li.appendChild(metaRow);

      // Updated timestamp
      if (item.updated_at) {
        const timeSpan = document.createElement("span");
        timeSpan.className = "v2-item-meta v2-queue-time";
        try {
          const date = new Date(item.updated_at);
          timeSpan.textContent = date.toLocaleString("ko-KR", { timeZone: "Asia/Seoul" });
        } catch (_) {
          timeSpan.textContent = item.updated_at;
        }
        li.appendChild(timeSpan);
      }

      list.appendChild(li);
    });

    card.appendChild(list);
  });

  if (!hasVisibleItems) {
    const empty = document.createElement("p");
    empty.className = "v2-empty";
    empty.textContent = "표시할 작업이 없습니다";
    card.appendChild(empty);
  }

  section.appendChild(card);
  return section;
}

function injectWorkQueueSection(data) {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const existing = document.getElementById("v2-work-queue-container");
  if (existing) existing.remove();

  const container = document.createElement("div");
  container.id = "v2-work-queue-container";
  container.appendChild(renderWorkQueueSection(data));

  const layout = root.querySelector(".v2-layout");
  if (layout) {
    layout.appendChild(container);
    return;
  }

  root.appendChild(container);
}

// Expose globally for board-v2.js to call
window.injectWorkQueueSection = injectWorkQueueSection;
