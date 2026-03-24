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

function normalizeSuggestionTitle(value) {
  return String(value || "")
    .replace(/IPU AI Security Filter/gi, "IPU AI Firewall")
    .replace(/security-filter/gi, "firewall")
    .trim();
}

function normalizeItemTypeLabel(value) {
  const key = String(value || "").trim().toLowerCase();
  if (!key || key === "item") return "항목";
  if (key === "file") return "파일";
  if (key === "folder") return "폴더";
  if (key === "project") return "프로젝트";
  return value || "항목";
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

function renderWorkdiarySection(state) {
  const targetId = "workdiaryList";
  const parentPanel = document.getElementById(targetId)?.parentElement;
  if (!parentPanel) return;
  parentPanel.classList.add("panel-browsing");

  // 자연 정렬 적용 (Intl.Collator 사용)
  const collator = new Intl.Collator(undefined, {numeric: true, sensitivity: 'base'});
  const items = (state.workdiaryItems || []).sort((a, b) => collator.compare(a.name, b.name));

  setCountBadge("workdiaryCount", items.length);

  const formatter = (item) => `
    <div class="list-item candidate-item">
      <div class="candidate-head">
        <strong>${escapeHtml(item.name)}</strong>
        <span class="candidate-rank">${escapeHtml(normalizeItemTypeLabel(item.item_type))}</span>
      </div>
      <span class="candidate-reason">${escapeHtml(formatDateTime(item.modified_at).slice(0, 16) || "-")}</span>
    </div>
  `;

  renderCappedList(targetId, items, formatter, 3, "workdiary 스캔 결과가 비어 있거나 경로 설정이 필요합니다.");
  parentPanel.onclick = () => {
    showDetailedList("workdiary 상위 폴더", "폴더 목록 (자연 정렬)", items, (i) => `
      <div class='list-item'><strong>${escapeHtml(i.name)}</strong> <span class='muted'>${escapeHtml(i.modified_at)}</span></div>
    `);
  };
}

function renderPriorityCandidatesSection(state) {
  const targetId = "priorityCandidateList";
  const parentPanel = document.getElementById(targetId)?.parentElement;
  if (!parentPanel) return;
  parentPanel.classList.add("panel-browsing");

  const items = state.priorityCandidates || [];
  setCountBadge("priorityCandidateCount", items.length);

  const renderCandidate = (item) => `
    <div class="list-item candidate-item">
      <div class="candidate-head">
        <strong>${escapeHtml(item.name)}</strong>
      </div>
      <span class="candidate-reason">${escapeHtml(item.priority_reason || "-")}</span>
    </div>
  `;

  const formatter = (item) => renderCandidate(item);
  renderCappedList(targetId, items, formatter, 3, "우선순위를 분석할 만한 작업 데이터가 아직 충분하지 않습니다.");
  parentPanel.onclick = () => {
    showDetailedList("우선 검토 후보", "프로젝트 후보 목록", state.priorityCandidates, (i) => `
      <div class='list-item'>
        <strong>${escapeHtml(i.name)}</strong>
        <p class='muted'>${escapeHtml(i.priority_reason)} (점수: ${escapeHtml(String(i.priority_score ?? 0))})</p>
      </div>
    `);
  };
}

async function renderDerivedSuggestionsSection() {
  const targetId = "derivedSuggestionList";
  const container = document.getElementById(targetId);
  if (!container) return;
  const parentPanel = container.parentElement;
  if (parentPanel) parentPanel.classList.add("panel-browsing");

  try {
    const response = await fetch("/api/suggestions");
    const data = await response.json();
    const suggestions = data.suggestions || [];
    state.derivedSuggestions = suggestions;

    setCountBadge("derivedSuggestionCount", suggestions.length);

    if (suggestions.length === 0) {
      container.innerHTML = `<div class="empty-state">추천 퀘스트가 없습니다. CLI에서 새로고침 후 다시 확인하세요.</div>`;
      return;
    }

    container.innerHTML = suggestions.map((s) => {
      const source = normalizeProjectLabel(s.source_project || "unknown");
      return `
        <div class="list-item">
          <div class="candidate-head">
            <strong>[${escapeHtml(source)}] ${escapeHtml(normalizeSuggestionTitle(s.title))}</strong>
          </div>
          <span class="candidate-reason">${escapeHtml(s.why_now || "-")}</span>
        </div>
      `;
    }).join("");

    if (parentPanel) {
      parentPanel.onclick = () => {
        showDetailedList("프로젝트에서 온 추천 퀘스트", "추천 퀘스트 상세", state.derivedSuggestions || [], (i) => `
          <div class='list-item'>
            <strong>[${escapeHtml(normalizeProjectLabel(i.source_project || "unknown"))}] ${escapeHtml(normalizeSuggestionTitle(i.title || "-"))}</strong>
            <p class='muted'>${escapeHtml(i.why_now || "-")}</p>
            <p class='muted'>완료 기준: ${escapeHtml(i.completion_criteria || "-")}</p>
            <p class='muted'>다음 후보: ${escapeHtml(i.next_candidates || i.next_quest_candidates || "-")}</p>
          </div>
        `);
      };
    }
  } catch (error) {
    console.error("Failed to load derived suggestions", error);
    container.innerHTML = `<div class="empty-state">추천 퀘스트를 불러오지 못했습니다.</div>`;
  }
}
