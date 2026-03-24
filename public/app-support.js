/**
 * Support Grid rendering module
 */

function normalizeProjectLabel(value) {
  const raw = String(value || "").trim();
  if (!raw) return "unknown";
  return raw
    .replace(/^ipu-security$/i, "24-1-ipu-ai-firewall")
    .replace(/^\[?ipu-security\]?/i, "24-1")
    .replace(/IPU AI Security Filter/gi, "IPU AI Firewall")
    .trim();
}

function renderSupportGrid(state) {
  renderTodaySummarySection(state);
  renderUnfinishedPlansSection(state);
  renderPlansSection(state);
  renderSessionsSection(state);
  renderBriefsSection(state);
  renderExternalInboxSection(state);
  renderAgentStatusSection(state);
  renderWorkdiarySection(state);
  renderPriorityCandidatesSection(state);
  renderExternalContextPanel(state);
  renderDerivedSuggestionsSection().catch(() => {});
}

function normalizeSessionTitleLabel(value) {
  const raw = String(value || "").trim();
  const normalized = raw.toLowerCase();
  if (!raw) return "세션 정보 없음";
  if (normalized === "0-a-control new session") return "0-a-control 기본 세션";
  if (normalized === "0-a-control new opencode session") return "0-a-control OpenCode 세션";
  if (normalized === "0-a-control new codex session") return "0-a-control Codex 세션";
  if (normalized === "0-a-control new gemini-cli session") return "0-a-control Gemini CLI 세션";
  if (normalized === "0-a-control new kilo session") return "0-a-control Kilo 세션";
  return raw;
}

function renderSessionsSection(state) {
  renderSessions(); // Already defined in app-sessions.js and refined
}
