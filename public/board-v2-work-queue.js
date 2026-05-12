// ── Read-only Work Queue Panel with Executor Prompt Copy ──

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
  NOW: "지금 (NOW)",
  NEXT: "다음 (NEXT)",
  LOCAL_NEEDED: "로컬 실행 필요",
  VALIDATION_NEEDED: "검증 필요",
  REVIEW_NEEDED: "리뷰 필요",
  BLOCKED: "차단됨 (BLOCKED)",
  LATER: "나중에 (LATER)",
};

const WORK_QUEUE_PRIORITY_CLASS = {
  P0: "v2-priority-p0",
  P1: "v2-priority-p1",
  P2: "v2-priority-p2",
  P3: "v2-priority-p3",
};

// ── Executor Prompt Generation (for LOCAL_NEEDED / VALIDATION_NEEDED) ──

const COPY_SAFETY_RULES = [
  "## 안전 규칙",
  "1. Raw JSON, secrets, session data, private runtime content를 prompt에 포함하지 마세요.",
  "2. 저장소 인증 정보, API 키, 토큰은 절대 출력하지 마세요.",
  "3. 작업 범위를 벗어난 수정은 하지 마세요.",
  "4. 변경 전/후를 명확히 구분하여 보고하세요.",
].join("\n");

function generateExecutorPrompt(item, queueKey) {
  const label = WORK_QUEUE_LABELS[queueKey] || queueKey;
  const lines = [
    "=".repeat(60),
    "실행자 프롬프트 (Executor Prompt)",
    "=".repeat(60),
    "",
    "## 작업 항목",
    "- 제목: " + (item.title || "(제목 없음)"),
    "- 저장소: " + (item.source || "unknown"),
    "- 참조: " + (item.source_id ? "#" + item.source_id : ""),
    "- 큐: " + label,
    "- 우선순위: " + (item.priority || "P2"),
    item.status ? "- 상태: " + item.status : "",
    item.updated_at ? "- 업데이트: " + item.updated_at : "",
    "",
    "## 실행 컨텍스트",
    queueKey === "LOCAL_NEEDED"
      ? "이 작업은 로컬 환경에서 실행해야 합니다."
      : "이 작업은 로컬 환경에서 검증/확인이 필요합니다.",
    "",
    COPY_SAFETY_RULES,
    "",
    "## 작업 보고 템플릿",
    "- 수행한 작업:",
    "- 변경한 파일:",
    "- 주요 결정 사항:",
    "- 결과: [ ] 완료 / [ ] 부분 / [ ] 보류",
    "",
    "=".repeat(60),
  ];
  return lines.filter(Boolean).join("\n");
}

function copyPromptToClipboard(item, queueKey) {
  var text = generateExecutorPrompt(item, queueKey);
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(function () {
      var btn = document.activeElement;
      if (btn) {
        btn.textContent = "✓ 복사완료";
        setTimeout(function () { btn.textContent = "📋 프롬프트 복사"; }, 2000);
      }
    }).catch(function () { fallbackCopy(text); });
  } else {
    fallbackCopy(text);
  }
}

function fallbackCopy(text) {
  var ta = document.createElement("textarea");
  ta.value = text;
  ta.style.position = "fixed";
  ta.style.opacity = "0";
  document.body.appendChild(ta);
  ta.select();
  try { document.execCommand("copy"); alert("프롬프트가 클립보드에 복사되었습니다."); }
  catch (e) { alert("복사 실패: 수동으로 복사하세요."); }
  document.body.removeChild(ta);
}

// ── Main Panel Rendering ──

function renderWorkQueueSection(data) {
  var queues = (data && data.queues) || {};
  var items = (data && data.items) || [];
  var isLoaded = data !== null;

  var sectionId = "work-queue-panel";
  var existing = document.getElementById(sectionId);
  if (existing) existing.remove();

  var section = document.createElement("div");
  section.id = sectionId;
  section.className = "v2-panel v2-panel-collapsible";
  section.style.marginTop = "12px";

  var header = document.createElement("div");
  header.className = "v2-panel-header v2-panel-header-inset";
  header.textContent = "작업 큐";
  header.onclick = function () {
    var body = section.querySelector(".v2-panel-body");
    if (body) body.style.display = body.style.display === "none" ? "" : "none";
  };
  section.appendChild(header);

  var body = document.createElement("div");
  body.className = "v2-panel-body";

  if (!isLoaded || items.length === 0) {
    var emptyMsg = document.createElement("div");
    emptyMsg.className = "v2-empty-text";
    emptyMsg.textContent = isLoaded ? "작업 큐에 항목이 없습니다." : "작업 큐를 불러오지 못했습니다.";
    body.appendChild(emptyMsg);
    section.appendChild(body);
    injectWorkQueueSection(section);
    return;
  }

  WORK_QUEUE_DISPLAY_ORDER.forEach(function (queueKey) {
    var queueItems = queues[queueKey];
    if (!queueItems || queueItems.length === 0) return;

    var groupLabel = document.createElement("div");
    groupLabel.className = "v2-queue-group-label";
    groupLabel.textContent = (WORK_QUEUE_LABELS[queueKey] || queueKey) + " (" + queueItems.length + ")";
    body.appendChild(groupLabel);

    queueItems.forEach(function (item) {
      var card = document.createElement("div");
      card.className = "work-queue-item";
      card.style.cssText = "padding:6px 8px;margin:2px 0;border:1px solid #333;border-radius:4px;font-size:13px;";

      var titleEl = document.createElement("div");
      titleEl.className = "v2-text-subtle";
      titleEl.textContent = item.title || "(제목 없음)";
      titleEl.style.cssText = "font-weight:600;margin-bottom:2px;";
      card.appendChild(titleEl);

      var metaRow = document.createElement("div");
      metaRow.style.cssText = "display:flex;gap:4px;flex-wrap:wrap;align-items:center;font-size:11px;";

      var sourceLabel = document.createElement("span");
      sourceLabel.textContent = item.source || "";
      sourceLabel.style.cssText = "color:#999;";
      if (item.source) metaRow.appendChild(sourceLabel);

      var queueBadge = document.createElement("span");
      queueBadge.textContent = WORK_QUEUE_LABELS[queueKey] || queueKey;
      queueBadge.style.cssText = "background:#444;color:#eee;padding:1px 5px;border-radius:3px;";
      metaRow.appendChild(queueBadge);

      var priorityBadge = document.createElement("span");
      priorityBadge.textContent = item.priority || "P2";
      priorityBadge.style.cssText = "padding:1px 5px;border-radius:3px;color:#fff;background:#666;";
      metaRow.appendChild(priorityBadge);

      if (item.updated_at) {
        var timeEl = document.createElement("span");
        timeEl.textContent = item.updated_at;
        timeEl.style.cssText = "color:#777;font-size:10px;";
        metaRow.appendChild(timeEl);
      }

      // Copy prompt button for LOCAL_NEEDED / VALIDATION_NEEDED
      if (queueKey === "LOCAL_NEEDED" || queueKey === "VALIDATION_NEEDED") {
        var copyBtn = document.createElement("button");
        copyBtn.textContent = "📋 프롬프트 복사";
        copyBtn.style.cssText = "margin-left:auto;padding:2px 6px;font-size:11px;cursor:pointer;background:#3a3a3a;color:#ddd;border:1px solid #555;border-radius:3px;";
        copyBtn.onclick = (function (itm, qk) {
          return function () { copyPromptToClipboard(itm, qk); };
        })(item, queueKey);
        metaRow.appendChild(copyBtn);
      }

      card.appendChild(metaRow);
      body.appendChild(card);
    });
  });

  section.appendChild(body);
  injectWorkQueueSection(section);
}

function injectWorkQueueSection(el) {
  var existing = document.getElementById("work-queue-panel");
  if (existing) existing.remove();

  var insertionPoint = document.getElementById("manual-override-panel") || document.querySelector(".v2-panel:last-of-type");
  if (insertionPoint && insertionPoint.parentNode) {
    insertionPoint.parentNode.insertBefore(el, insertionPoint.nextSibling);
  } else {
    document.querySelector(".v2-panels-container")?.appendChild(el);
  }
}
