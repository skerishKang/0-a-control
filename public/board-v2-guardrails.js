// ── Read-only Settings/Guardrails Panel ──
function renderGuardrailsSection(settings, guardrails) {
  const section = document.createElement("section");
  section.className = "v2-rail-section";

  const label = document.createElement("span");
  label.className = "v2-section-label";
  label.textContent = "설정/가이드레일";
  section.appendChild(label);

  const card = document.createElement("div");
  card.className = "v2-rail-card";

  if (!settings && !guardrails) {
    const empty = document.createElement("p");
    empty.className = "v2-empty";
    empty.textContent = "설정·가이드레일 정보를 불러오지 못했습니다";
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

  if (settings) {
    addRow("호스트", settings.host || "N/A");
    addRow("포트", settings.port);
    addRow("디버그", settings.debug_enabled ? "활성" : "비활성");
    addRow("Python", settings.python_version || "N/A");

    if (settings.telegram && typeof settings.telegram === "object") {
      addRow("Telegram", settings.telegram.configured ? "설정됨" : "미설정");
      addRow("TG API ID", settings.telegram.api_id_configured ? "예" : "아니오");
      addRow("TG API Hash", settings.telegram.api_hash_configured ? "예" : "아니오");
      addRow("TG 세션", settings.telegram.session_path_configured ? "있음" : "없음");
    }
  }

  if (guardrails) {
    addRow("적용 수준", guardrails.overall_level || "N/A");

    if (guardrails.checks && Array.isArray(guardrails.checks)) {
      addRow("체크 수", guardrails.checks.length);

      const levelCounts = {};
      guardrails.checks.forEach(check => {
        if (check.level) {
          levelCounts[check.level] = (levelCounts[check.level] || 0) + 1;
        }
      });
      Object.entries(levelCounts).forEach(([level, count]) => {
        addRow(`Level ${level}`, count + "개");
      });
    }
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

function injectGuardrailsSection(settings, guardrails) {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const existing = document.getElementById("v2-guardrails-container");
  if (existing) existing.remove();

  const container = document.createElement("div");
  container.id = "v2-guardrails-container";
  container.appendChild(renderGuardrailsSection(settings, guardrails));

  const layout = root.querySelector(".v2-layout");
  if (layout) {
    layout.appendChild(container);
    return;
  }

  root.appendChild(container);
}

// Expose globally for board-v2.js to call
window.injectGuardrailsSection = injectGuardrailsSection;