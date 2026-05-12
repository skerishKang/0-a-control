/**
 * Session utility/pure functions
 */

function deriveSessionDecision(session, records) {
  if (session.summary_md) return session.summary_md;
  const modelRecord = records.find((record) => record.role === "assistant" || record.role === "tool");
  return modelRecord?.content || "세션 종료 시점의 작업 결과를 바탕으로 판단 요약이 필요합니다.";
}

function deriveSessionNextAction(session, records) {
  if (Array.isArray(session.actions_json) && session.actions_json.length) {
    return session.actions_json.join(", ");
  }
  const lastUserRecord = [...records].reverse().find((record) => record.role === "user");
  if (lastUserRecord?.content) return lastUserRecord.content;
  return "세션 마지막 흐름을 바탕으로 다음 시작 지점을 정리해야 합니다.";
}

function findLatestRecordBySourceType(records, sourceType) {
  return [...records].reverse().find((record) => record.source_type === sourceType);
}

function getAgentBadgeClass(agentName) {
  const name = (agentName || "").toLowerCase();
  if (name.includes("codex")) return "agent-codex";
  if (name.includes("gemini")) return "agent-gemini-cli";
  if (name.includes("windsurf")) return "agent-windsurf";
  return "agent-generic";
}

function classifySession(session) {
  const title = (session.title || "").toLowerCase();
  const agent = (session.agent_name || "").toLowerCase();
  const summary = (session.summary_md || "").trim();

  // 1. Test sessions
  if (["test", "dev", "debug", "smoke", "meta", "dummy"].some(k => title.includes(k)) || agent === "tester") {
    return "test";
  }
  // 2. Simulated sessions
  if (["sim", "model", "mock"].some(k => title.includes(k))) {
    return "simulated";
  }
  // 3. Operational sessions
  if (session.has_quest_verdict || summary.length > 20) {
    return "operational";
  }
  return "unknown";
}

// Analyze session for badges (similar to generate_session_html.py)
function analyzeSessionForBadges(session) {
  const summary = session.summary_md || "";
  const contentLength = summary.length;
  
  // Length badge
  let lengthBadge = "short";
  let lengthColor = "#999";
  if (contentLength >= 1500) { lengthBadge = "medium"; lengthColor = "#f39c12"; }
  if (contentLength >= 2500) { lengthBadge = "long"; lengthColor = "#27ae60"; }
  
  // Value badge based on content keywords
  let valueBadge = "empty";
  let valueColor = "#e74c3c";
  let valueLabel = "비어있음";
  
  const lowerSummary = summary.toLowerCase();
  if (summary.includes("완료") || summary.includes("종료") || lowerSummary.includes("done") || lowerSummary.includes("complete") || lowerSummary.includes("ended")) {
    valueBadge = "decisions"; valueColor = "#27ae60"; valueLabel = "결정";
  } else if (summary.includes("다음") || lowerSummary.includes("next") || lowerSummary.includes("continue")) {
    valueBadge = "next-action"; valueColor = "#3498db"; valueLabel = "다음";
  } else if (summary.includes("-") || summary.includes("*")) {
    valueBadge = "actions"; valueColor = "#9b59b6"; valueLabel = "행동";
  } else if (contentLength > 30) {
    valueBadge = "transcript-only"; valueColor = "#f39c12"; valueLabel = "기록";
  }
  
  return { lengthBadge, lengthColor, valueBadge, valueColor, valueLabel };
}

function normalizeSessionLengthLabel(value) {
  const key = String(value || "").trim().toLowerCase();
  if (key === "short") return "짧음";
  if (key === "medium") return "중간";
  if (key === "long") return "길음";
  return value || "";
}

function normalizeSessionTitle(value, projectKey) {
  const raw = String(value || "").trim();
  const normalized = raw.toLowerCase();
  if (!raw) return projectKey || "세션";
  if (normalized === "0-a-control new session") return "0-a-control 기본 세션";
  if (normalized === "0-a-control new opencode session") return "0-a-control OpenCode 세션";
  if (normalized === "0-a-control new codex session") return "0-a-control Codex 세션";
  if (normalized === "0-a-control new gemini-cli session") return "0-a-control Gemini CLI 세션";
  if (normalized === "0-a-control new kilo session") return "0-a-control Kilo 세션";
  return raw;
}

// Generate 1-line preview from summary
function generateSessionPreview(session) {
  const summary = session.summary_md || "";
  if (!summary) return "세션 요약 없음";
  
  // Get first meaningful line
  const lines = summary.split("\n").filter(l => l.trim());
  if (lines.length === 0) return "세션 요약 없음";
  
  // Return first line, truncated
  return lines[0].substring(0, 80) + (lines[0].length > 80 ? "..." : "");
}
