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
  ];

  el.innerHTML = tabs
    .map(
      (tab) =>
        `<button class="v2-phase-tab${activePhase === tab.key ? " -active" : ""}" ` +
        `type="button" onclick="window.boardV2SetPhase('${tab.key}')">${tab.label}</button>`
    )
    .join("");
}

function renderStatusLabel(phase) {
  const el = document.getElementById("v2StatusLabel");
  if (!el) return;
  const isPreview = _localPreviewPhase !== null;
  el.textContent = isPreview ? `미리보기: ${getPhaseLabel(phase)}` : `상태: ${getPhaseLabel(phase)}`;
}

function dispatchRender(state, phase) {
  if (phase === "end-of-day") {
    renderEndOfDay(state);
  } else if (phase === "in-progress") {
    renderInProgress(state);
  } else {
    renderMorning(state);
  }
}

window.boardV2SetPhase = function boardV2SetPhase(phase) {
  _localPreviewPhase = phase;
  if (_cachedState) {
    const effectivePhase = getEffectivePhase(_cachedState);
    renderPhaseTabs(effectivePhase);
    renderStatusLabel(effectivePhase);
    dispatchRender(_cachedState, effectivePhase);
  }
};
