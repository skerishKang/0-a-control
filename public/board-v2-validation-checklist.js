// ── Read-only Validation Checklist Panel ──

// ── Status Label Maps ──

const VALIDATION_STATUS_LABELS = {
  passed: "통과",
  failed: "실패",
  skipped: "건너뜀",
  blocked: "차단",
  pending: "대기",
  not_started: "대기",
};

const VALIDATION_STATUS_CLASS = {
  passed: "v2-status-pass",
  failed: "v2-status-fail",
  skipped: "v2-status-skip",
  blocked: "v2-status-block",
  pending: "v2-status-pending",
  not_started: "v2-status-pending",
};

// ── API ──

async function fetchValidationChecklists() {
  try {
    const response = await fetch("/api/validation-checklists");
    if (!response.ok) {
      return null;
    }
    return await response.json();
  } catch (err) {
    console.warn("Validation checklists fetch failed:", err);
    return null;
  }
}

// ── Main Panel Rendering ──

function renderValidationChecklists(data) {
  var checklists = (data && data.checklists) || (Array.isArray(data) ? data : []);
  var isLoaded = data !== null;

  var sectionId = "validation-checklist-panel";
  var existing = document.getElementById(sectionId);
  if (existing) existing.remove();

  var section = document.createElement("div");
  section.id = sectionId;
  section.className = "v2-panel v2-panel-collapsible";
  section.style.marginTop = "12px";

  var header = document.createElement("div");
  header.className = "v2-panel-header v2-panel-header-inset";
  header.textContent = "검증 체크리스트";
  header.onclick = function () {
    var body = section.querySelector(".v2-panel-body");
    if (body) body.style.display = body.style.display === "none" ? "" : "none";
  };
  section.appendChild(header);

  var body = document.createElement("div");
  body.className = "v2-panel-body";

  if (!isLoaded || checklists.length === 0) {
    var emptyMsg = document.createElement("div");
    emptyMsg.className = "v2-empty-text";
    emptyMsg.textContent = isLoaded ? "검증 체크리스트가 없습니다." : "검증 체크리스트를 불러오지 못했습니다.";
    body.appendChild(emptyMsg);
    section.appendChild(body);
    injectValidationChecklists(section);
    return;
  }

  checklists.forEach(function (checklist) {
    var card = document.createElement("div");
    card.className = "validation-checklist-item";
    card.style.cssText = "padding:6px 8px;margin:2px 0;border:1px solid #333;border-radius:4px;font-size:13px;";

    // Title / name row
    var titleEl = document.createElement("div");
    titleEl.className = "v2-text-subtle";
    var titleParts = [];
    if (checklist.target_type) titleParts.push(checklist.target_type);
    if (checklist.target_id) titleParts.push("#" + checklist.target_id);
    titleEl.textContent = titleParts.length > 0 ? titleParts.join(" ") : (checklist.id || "(체크리스트)");
    titleEl.style.cssText = "font-weight:600;margin-bottom:2px;";
    card.appendChild(titleEl);

    // Meta row with overall status badge + counts
    var metaRow = document.createElement("div");
    metaRow.style.cssText = "display:flex;gap:4px;flex-wrap:wrap;align-items:center;font-size:11px;";

    // Overall status badge
    var overallStatus = checklist.overall_status || "not_started";
    var statusLabel = VALIDATION_STATUS_LABELS[overallStatus] || overallStatus;
    var statusBadge = document.createElement("span");
    statusBadge.textContent = statusLabel;
    statusBadge.style.cssText = "padding:1px 5px;border-radius:3px;color:#fff;background:#666;";
    if (overallStatus === "passed") statusBadge.style.background = "#2e7d32";
    else if (overallStatus === "failed") statusBadge.style.background = "#c62828";
    else if (overallStatus === "blocked") statusBadge.style.background = "#e65100";
    else if (overallStatus === "skipped") statusBadge.style.background = "#555";
    else statusBadge.style.background = "#666";
    metaRow.appendChild(statusBadge);

    // Status counts (pass/fail/skip/block/pending)
    var counts = {};
    var items = checklist.items || [];
    items.forEach(function (item) {
      var st = item.status || "not_started";
      counts[st] = (counts[st] || 0) + 1;
    });

    var countParts = [];
    if (counts.passed) countParts.push("✓ " + counts.passed);
    if (counts.failed) countParts.push("✗ " + counts.failed);
    if (counts.skipped) countParts.push("— " + counts.skipped);
    if (counts.blocked) countParts.push("● " + counts.blocked);
    if (counts.not_started || counts.pending) {
      var pending = (counts.not_started || 0) + (counts.pending || 0);
      countParts.push("○ " + pending);
    }

    if (countParts.length > 0) {
      var countEl = document.createElement("span");
      countEl.textContent = countParts.join(" | ");
      countEl.style.cssText = "color:#aaa;margin-left:4px;";
      metaRow.appendChild(countEl);
    }

    // Last updated timestamp
    if (checklist.updated_at) {
      var timeEl = document.createElement("span");
      timeEl.textContent = checklist.updated_at;
      timeEl.style.cssText = "color:#777;font-size:10px;margin-left:auto;";
      metaRow.appendChild(timeEl);
    }

    card.appendChild(metaRow);
    body.appendChild(card);
  });

  section.appendChild(body);
  injectValidationChecklists(section);
}

function injectValidationChecklists(el) {
  var existing = document.getElementById("validation-checklist-panel");
  if (existing) existing.remove();

  // Insert after work-queue-panel if it exists, otherwise after the last v2-panel
  var insertionPoint = document.getElementById("work-queue-panel") || document.querySelector(".v2-panel:last-of-type");
  if (insertionPoint && insertionPoint.parentNode) {
    insertionPoint.parentNode.insertBefore(el, insertionPoint.nextSibling);
  } else {
    document.querySelector(".v2-panels-container")?.appendChild(el);
  }
}
