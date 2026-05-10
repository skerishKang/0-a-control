// ── Manual Overrides UI (read-only) ──
function renderOverridesSection(overrides) {
  const section = document.createElement("section");
  section.className = "v2-rail-section";

  const label = document.createElement("span");
  label.className = "v2-section-label";
  label.textContent = "수동 오버라이드";
  section.appendChild(label);

  const card = document.createElement("div");
  card.className = "v2-rail-card";

  // Create form for manual override
  const form = document.createElement("form");
  form.className = "v2-override-form";

  const typeSelect = document.createElement("select");
  typeSelect.id = "v2OverrideTargetType";
  typeSelect.className = "v2-override-select";
  typeSelect.setAttribute("aria-label", "타입 선택");
  const typeOptions = ["", "issue", "pr", "quest", "plan", "session", "source", "global"];
  typeOptions.forEach((opt) => {
    const option = document.createElement("option");
    option.value = opt;
    option.textContent = opt || "타입 선택";
    typeSelect.appendChild(option);
  });

  const idInput = document.createElement("input");
  idInput.type = "text";
  idInput.id = "v2OverrideTargetId";
  idInput.className = "v2-override-input";
  idInput.setAttribute("placeholder", "대상ID");
  idInput.setAttribute("maxlength", "50");

  const statusSelect = document.createElement("select");
  statusSelect.id = "v2OverrideManualStatus";
  statusSelect.className = "v2-override-select";
  statusSelect.setAttribute("aria-label", "상태");
  const statusOptions = ["", "READY", "IN_PROGRESS", "BLOCKED", "NEEDS_IMPLEMENTATION", "NEEDS_REVIEW", "NEEDS_VALIDATION", "DONE", "NO_ACTION", "PINNED", "WATCH", "IGNORE_UNTIL", "DO_NOT_MERGE", "DO_NOT_CLOSE"];
  statusOptions.forEach((opt) => {
    const option = document.createElement("option");
    option.value = opt;
    option.textContent = opt || "상태 선택";
    statusSelect.appendChild(option);
  });

  const reasonInput = document.createElement("input");
  reasonInput.type = "text";
  reasonInput.id = "v2OverrideReason";
  reasonInput.className = "v2-override-input";
  reasonInput.setAttribute("placeholder", "사유");
  reasonInput.setAttribute("maxlength", "200");

  const submitBtn = document.createElement("button");
  submitBtn.type = "submit";
  submitBtn.className = "v2-btn v2-btn-inline";
  submitBtn.textContent = "추가";

  form.appendChild(typeSelect);
  form.appendChild(idInput);
  form.appendChild(statusSelect);
  form.appendChild(reasonInput);
  form.appendChild(submitBtn);

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const target_type = typeSelect.value.trim();
    const target_id = idInput.value.trim();
    const manual_status = statusSelect.value.trim();
    const reason = reasonInput.value.trim();

    if (!target_type) {
      window.alert("타입을 선택해 주세요.");
      return;
    }
    if (!target_id) {
      window.alert("대상ID를 입력해 주세요.");
      return;
    }
    if (!manual_status) {
      window.alert("상태를 선택해 주세요.");
      return;
    }
    if (!reason) {
      window.alert("사유를 입력해 주세요.");
      return;
    }

    try {
      await boardApi.createOverride({ target_type, target_id, manual_status, reason });
      typeSelect.value = "";
      idInput.value = "";
      statusSelect.value = "";
      reasonInput.value = "";
      const root = document.getElementById("boardV2Root");
      if (root) {
        const state = await boardApi.fetchFullState();
        state.__overrides = await boardApi.fetchOverrides();
        _cachedState = state;
        window.injectOverridesSection(state.__overrides);
      }
    } catch (err) {
      window.alert("생성 중 오류가 발생했습니다.");
    }
  });

  card.appendChild(form);

  if (!overrides || overrides.length === 0) {
    const empty = document.createElement("p");
    empty.className = "v2-empty";
    empty.textContent = "수동 오버라이드가 없습니다.";
    card.appendChild(empty);
  } else {
    const list = document.createElement("ul");
    list.className = "v2-list";

    overrides.forEach((ov) => {
      const li = document.createElement("li");
      li.className = "v2-list-item";

      const contentDiv = document.createElement("div");
      contentDiv.className = "v2-override-row";

      const titleSpan = document.createElement("span");
      titleSpan.className = "v2-override-title";
      const overrideLabel =
        [ov.manual_status, [ov.target_type, ov.target_id].filter(Boolean).join("/")].filter(Boolean).join(" · ") ||
        ov.title ||
        "오버라이드";
      titleSpan.textContent = overrideLabel;

      const active = ov.is_active !== false;
      const badge = document.createElement("span");
      badge.className = active ? "v2-status-badge -auto" : "v2-status-badge";
      badge.textContent = active ? "활성" : "비활성";

      contentDiv.appendChild(titleSpan);
      contentDiv.appendChild(badge);

      if (active) {
        const deactivateBtn = document.createElement("button");
        deactivateBtn.type = "button";
        deactivateBtn.className = "v2-btn v2-btn-inline v2-btn-deactivate";
        deactivateBtn.textContent = "비활성화";
        deactivateBtn.addEventListener("click", async (e) => {
          e.stopPropagation();
          if (!window.confirm("이 오버라이드를 비활성화할까요?")) return;
          try {
            await boardApi.deactivateOverride(ov.id);
            const root = document.getElementById("boardV2Root");
            if (root) {
              const state = await boardApi.fetchFullState();
              state.__overrides = await boardApi.fetchOverrides();
              _cachedState = state;
              window.injectOverridesSection(state.__overrides);
            }
          } catch (err) {
            window.alert("오버라이드 비활성화에 실패했습니다.");
          }
        });
        contentDiv.appendChild(deactivateBtn);
      }

      li.appendChild(contentDiv);

      if (ov.reason) {
        const reasonSpan = document.createElement("span");
        reasonSpan.className = "v2-item-meta";
        reasonSpan.textContent = ov.reason;
        li.appendChild(reasonSpan);
      }

      if (ov.reason || ov.description || ov.impact_summary) {
        li.classList.add("v2-modal-clickable");
        li.addEventListener("click", (function(overrideTitle, overrideText) {
          return function() {
            window.boardV2OpenTextModal(overrideTitle, overrideText);
          };
        })(overrideLabel, ov.description || ov.reason || ov.impact_summary || ""));
      }

      list.appendChild(li);
    });

    card.appendChild(list);
  }

  section.appendChild(card);
  return section;
}

function injectOverridesSection(overrides) {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const layout = root.querySelector(".v2-layout");
  if (!layout) return;

  const existing = document.getElementById("v2-overrides-container");
  if (existing) existing.remove();

  const container = document.createElement("div");
  container.id = "v2-overrides-container";
  container.appendChild(renderOverridesSection(overrides));
  layout.appendChild(container);
}

// Expose globally for board-v2.js to call
window.injectOverridesSection = injectOverridesSection;
