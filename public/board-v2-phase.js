function getAutoPhase(state) {
  const phase = state.day_phase || "morning";
  if (phase === "end-of-day") return "end-of-day";
  if (
    phase === "in-progress" ||
    phase === "midday" ||
    phase === "verdict-pending" ||
    state.current_quest_id ||
    (state.current_quest && state.current_quest.id)
  ) return "in-progress";
  return "morning";
}

function getEffectivePhase(state) {
  return _localPreviewPhase || getAutoPhase(state);
}

function getPhaseLabel(phase) {
  const mapping = {
    morning: "아침",
    midday: "진행",
    "in-progress": "진행",
    "end-of-day": "마감",
  };
  return mapping[phase] || phase;
}

function renderPhaseTabs(activePhase) {
  const el = document.getElementById("v2PhaseTabs");
  if (!el) return;

  const tabs = [
    { key: "morning", label: "아침" },
    { key: "in-progress", label: "진행" },
    { key: "end-of-day", label: "마감" },
    { key: "history", label: "완료" },
  ];

  el.innerHTML = tabs
    .map(
      (tab) =>
        `<button class="v2-phase-tab${activePhase === tab.key ? " -active" : ""}" ` +
        `type="button" onclick="window.boardV2SetPhase('${tab.key}')">${tab.label}</button>`
    )
    .join("");
}

function getPhaseReason(state, phase, isPreview) {
  if (isPreview) return "사용자 선택 항목 미리보기";
  
  if (state.day_phase_reason && phase === state.day_phase) {
    return state.day_phase_reason;
  }

  const mapping = {
    morning: "하루를 계획하는 아침 브리핑 시간입니다.",
    "in-progress": "활성 퀘스트가 있거나 집중 작업 시간대입니다.",
    midday: "집중 작업 시간대입니다.",
    "end-of-day": "오늘을 마무리하고 내일을 설계할 시간입니다.",
  };
  return mapping[phase] || "시스템 판단에 따른 현재 단계입니다.";
}

function renderStatusLabel(state, phase) {
  const el = document.getElementById("v2StatusLabel");
  if (!el) return;
  const isPreview = _localPreviewPhase !== null;
  const label = getPhaseLabel(phase);
  const reason = getPhaseReason(state, phase, isPreview);

  if (isPreview) {
    el.innerHTML = `
      <div style="display:flex; flex-direction:column; align-items:flex-end; gap:2px;">
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="v2-status-badge -preview">미리보기</span>
          <span class="v2-status-text">${label}</span>
          <button type="button" class="v2-status-reset-btn" onclick="window.boardV2ResetPhase()">자동 상태로 복귀</button>
        </div>
        <span class="v2-status-reason">${escapeHtml(reason)}</span>
      </div>
    `;
  } else {
    el.innerHTML = `
      <div style="display:flex; flex-direction:column; align-items:flex-end; gap:2px;">
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="v2-status-badge -auto">자동 상태</span>
          <span class="v2-status-text">${label}</span>
        </div>
        <span class="v2-status-reason">${escapeHtml(reason)}</span>
      </div>
    `;
  }
}

function dispatchRender(state, phase) {
  if (phase === "end-of-day") {
    renderEndOfDay(state);
  } else if (phase === "in-progress") {
    renderInProgress(state);
  } else if (phase === "history") {
    if (typeof renderHistory === "function") {
      renderHistory(state);
    }
  } else {
    renderMorning(state);
  }
}

window.boardV2SetPhase = function boardV2SetPhase(phase) {
  _localPreviewPhase = phase;
  if (_cachedState) {
    const effectivePhase = getEffectivePhase(_cachedState);
    renderPhaseTabs(effectivePhase);
    renderStatusLabel(_cachedState, effectivePhase);
    dispatchRender(_cachedState, effectivePhase);
  }
};

window.boardV2ResetPhase = function boardV2ResetPhase() {
  _localPreviewPhase = null;
  if (_cachedState) {
    const autoPhase = getAutoPhase(_cachedState);
    renderPhaseTabs(autoPhase);
    renderStatusLabel(_cachedState, autoPhase);
    dispatchRender(_cachedState, autoPhase);
  }
};
