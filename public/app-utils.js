const state = {
  currentState: null,
  plans: [],
  briefs: [],
  quests: [],
  sessions: [],
  workdiaryItems: [],
  priorityCandidates: [],
  sessionAgentFilter: "all",
  sessionRecordFilter: "all",
  sessionPanelRecords: [],
  activeSession: null,
  selectedDate: new Date().toISOString().split('T')[0],
};

const sessionAgentOptions = [{ value: "all", label: "전체" }, { value: "codex", label: "codex" }, { value: "gemini-cli", label: "gemini-cli" }, { value: "antigravity", label: "antigravity" }, { value: "windsurf", label: "windsurf" }, { value: "kilo", label: "kilo" }, { value: "opencode", label: "opencode" }];
const visibleSessionAgents = new Set(sessionAgentOptions.filter((option) => option.value !== "all").map((option) => option.value));
const sessionRecordOptions = [{ value: "all", label: "전체" }, { value: "user", label: "사용자" }, { value: "assistant", label: "모델" }, { value: "tool", label: "도구" }];

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return await response.json();
}

function formatItem(item, secondary) {
  return `<div class="list-item"><strong>${escapeHtml(item || "-")}</strong>${secondary ? `<span>${escapeHtml(secondary)}</span>` : ""}</div>`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function byBucket(plans, bucket) {
  return plans.filter((item) => item.bucket === bucket);
}

function labelBucket(bucket) {
  return {
    today: "오늘",
    short_term: "단기",
    long_term: "장기",
    recurring: "반복",
    dated: "기한고정",
  }[bucket] || bucket || "";
}

function labelStatus(status) {
  return {
    active: "진행중",
    pending: "판정대기",
    done: "완료",
    partial: "부분완료",
    hold: "보류",
    cancelled: "취소",
    queued: "대기중",
    closed: "종료",
    interrupted: "중단",
  }[status] || status || "";
}

function renderVerdictBadge(status) {
  if (!status) return "";
  const label = labelStatus(status);
  return `<span class="session-badge verdict ${escapeHtml(status)}">${escapeHtml(label)}</span>`;
}

function missionProgressPercent(status) {
  return {
    done: 100,
    partial: 60,
    active: 35,
    hold: 15,
    pending: 10,
  }[status] ?? 0;
}

function missionRiskText({ missionStatus, nextCore, currentQuestTitle }) {
  if (missionStatus === "done") {
    return "주 임무 완료 단계. 다음 핵심으로 전환 준비.";
  }
  if (missionStatus === "partial") {
    return `지금 재진입하지 않으면 ${nextCore?.title || currentQuestTitle || "다음 핵심"} 일정이 밀릴 수 있음.`;
  }
  if (missionStatus === "hold") {
    return "보류 장기화 시 오늘 주 임무 목표가 상실될 위험이 큼.";
  }
  if (missionStatus === "active") {
    return "현재 흐름을 유지하여 퀘스트 마무리에 집중할 것.";
  }
  return "오늘 중 재착수하지 않으면 주 임무 지연 확정적임.";
}

function formatDateTime(value) {
  if (!value) return "";
  const normalized = value.replace("T", " ").replace("+00:00", " UTC");
  return normalized.slice(0, 19) + (normalized.includes("UTC") ? " UTC" : "");
}

function formatRecentLabel(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return formatDateTime(value);
  const now = new Date();
  const diffMinutes = Math.floor((now.getTime() - date.getTime()) / 60000);
  if (diffMinutes < 1) return "방금";
  if (diffMinutes < 60) return `${diffMinutes}분 전`;
  const hh = String(date.getHours()).padStart(2, "0");
  const mm = String(date.getMinutes()).padStart(2, "0");
  if (
    now.getFullYear() === date.getFullYear() &&
    now.getMonth() === date.getMonth() &&
    now.getDate() === date.getDate()
  ) {
    return `오늘 ${hh}:${mm}`;
  }
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${month}-${day} ${hh}:${mm}`;
}

function formatShortDateTime(value) {
  if (!value) return "";
  return value.replace("T", " ").slice(5, 16);
}

function renderList(targetId, items, formatter, emptyMessage = "표시할 항목이 없습니다.") {
  const target = document.getElementById(targetId);
  if (!target) return;
  if (!items.length) {
    target.innerHTML = `<div class="list-item empty">${escapeHtml(emptyMessage)}</div>`;
    return;
  }
  target.innerHTML = items.map(formatter).join("");
}

function setCountBadge(targetId, count) {
  const target = document.getElementById(targetId);
  if (!target) return;
  target.textContent = `${count}건`;
}

function renderCappedList(targetId, items, formatter, limit = 4, emptyMessage = "표시할 항목이 없습니다.") {
  const target = document.getElementById(targetId);
  if (!target) return;
  if (!items || !items.length) {
    target.innerHTML = `<div class="list-item empty">${escapeHtml(emptyMessage)}</div>`;
    return;
  }
  
  const displayed = items.slice(0, limit);
  target.innerHTML = displayed.map(formatter).join("");
}

function summarizeVerdictReason(status, reason) {
  if (status === "done") return "완료 기준 충족. 다음 단계로 마감 권장.";
  if (status === "partial") return "의미 있는 진행 확인. 세부 보완 후 전환 필요.";
  if (status === "hold") return "조건 불충분으로 인한 일시 보류 및 재정의 권장.";
  return reason || "판정 근거 분석 중...";
}

function summarizeMissionReason(reason) {
  if (!reason) return "우선순위 설정 필요.";
  return reason
    .replace(/^급하고,\s*/u, "")
    .replace(/^미루기\s*쉽지만,\s*/u, "")
    .replace(/^반드시\s*해야\s*하는\s*/u, "")
    .replace(/^핵심\s*/u, "")
    .trim();
}
