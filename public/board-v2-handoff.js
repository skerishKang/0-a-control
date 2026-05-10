// ── Executor Handoff Panel ──
const HANDOFF_SAFETY_RULES = [
  "main 직접 수정/push 금지",
  "PR merge 금지 unless explicitly instructed",
  "issue close 금지 unless explicitly instructed",
  "secret/token/session/private data/raw runtime payload 출력 금지",
  "runtime data stage 금지",
  "tests/__init__.py 추가 금지",
  "python scripts/server.py 직접 foreground 실행 금지",
  "use python scripts/smoke_server.py for smoke validation",
  "broad codebase exploration 금지",
  "line-ending/full-file rewrite churn 금지"
];

const TASK_SPECIFIC = {
  "Local Code Executor": [
    "branch creation/update",
    "code changes allowed only within scope",
    "CLI validation required",
    "no python scripts/server.py foreground",
    "no runtime data stage",
    "targeted diff only"
  ],
  "Browser QA Executor": [
    "URL tested",
    "source branch/HEAD confirmation",
    "no code changes",
    "screenshot redaction if needed",
    "console/network safety checks",
    "report PASS/HOLD/NOT_RUN"
  ],
  "GitHub Ops Executor": [
    "issue/PR metadata actions only",
    "no code changes",
    "no merge/issue close unless explicitly instructed",
    "verify repo and issue/PR number before mutation",
    "report URLs and blocked actions"
  ],
  "Long-running Local Loop Executor": [
    "repeat same PR fixes only",
    "max loop limit: 3 cycles",
    "stop conditions:",
    "  - validation failure not obvious",
    "  - scope expansion",
    "  - server/storage changes needed",
    "  - full-file churn",
    "  - runtime data staged",
    "report after each cycle"
  ],
  "Diff Cleanup Executor": [
    "no feature expansion",
    "restore line endings/formatting",
    "reduce full-file replacement to targeted hunks",
    "preserve existing functional fixes",
    "validate diff before commit"
  ]
};

function getHandoffPrompt(taskType, context) {
  const header = `[CTO → ${taskType}] 실행자 핸드오프 프롬프트`;
  const safety = HANDOFF_SAFETY_RULES.map(r => `- ${r}`).join("\n");
  const taskSpec = (TASK_SPECIFIC[taskType] || []).map(r => `- ${r}`).join("\n");
  const reportTemplate = `Report:
- Branch:
- PR URL:
- HEAD SHA:
- Changed files:
- Implementation summary:
- Prompt types included:
- Copy behavior:
- Diff targeted, no full-file churn: YES/NO
- Validation results:
- Runtime data staged: NO/YES
- Browser verification: PASS/NOT_RUN/FAIL
- Final recommendation:
  - PASS → CTO review
  - HOLD → sanitized blocker`;

  const contextParts = [];
  if (context.repo) contextParts.push(`- Repo: ${context.repo}`);
  if (context.issueNumber) contextParts.push(`- Issue: #${context.issueNumber}`);
  if (context.prNumber) contextParts.push(`- PR: #${context.prNumber}`);
  if (context.branch) contextParts.push(`- Branch: ${context.branch}`);
  if (context.expectedHead) contextParts.push(`- Expected HEAD: ${context.expectedHead}`);
  if (context.taskName) contextParts.push(`- Task: ${context.taskName}`);

  const contextBlock = contextParts.length > 0 ? `\n\n- Context:\n${contextParts.join("\n")}` : "";

  return taskSpec
    ? `${header}${contextBlock}\n\n- Safety rules:\n${safety}\n\n- Task-specific:\n${taskSpec}\n\n${reportTemplate}`
    : `${header}${contextBlock}\n\n${safety}\n\n${reportTemplate}`;
}

function renderHandoffSection() {
  const section = document.createElement("section");
  section.className = "v2-rail-section";

  const label = document.createElement("span");
  label.className = "v2-section-label";
  label.textContent = "실행자 핸드오프";
  section.appendChild(label);

  const card = document.createElement("div");
  card.className = "v2-rail-card";

  // Task type selector
  const select = document.createElement("select");
  select.id = "v2HandoffTaskType";
  select.className = "v2-override-select";
  const taskTypes = [
    "Local Code Executor",
    "Browser QA Executor",
    "GitHub Ops Executor",
    "Long-running Local Loop Executor",
    "Diff Cleanup Executor"
  ];
  taskTypes.forEach(tt => {
    const option = document.createElement("option");
    option.value = tt;
    option.textContent = tt;
    select.appendChild(option);
  });

  // Context fields
  const ctxRepo = document.createElement("input");
  ctxRepo.type = "text";
  ctxRepo.id = "v2HandoffRepo";
  ctxRepo.className = "v2-override-input";
  ctxRepo.setAttribute("placeholder", "Repo (e.g. owner/repo)");
  ctxRepo.setAttribute("maxlength", "100");

  const ctxIssue = document.createElement("input");
  ctxIssue.type = "text";
  ctxIssue.id = "v2HandoffIssue";
  ctxIssue.className = "v2-override-input";
  ctxIssue.setAttribute("placeholder", "Issue #");
  ctxIssue.setAttribute("maxlength", "20");

  const ctxPR = document.createElement("input");
  ctxPR.type = "text";
  ctxPR.id = "v2HandoffPR";
  ctxPR.className = "v2-override-input";
  ctxPR.setAttribute("placeholder", "PR #");
  ctxPR.setAttribute("maxlength", "20");

  const ctxBranch = document.createElement("input");
  ctxBranch.type = "text";
  ctxBranch.id = "v2HandoffBranch";
  ctxBranch.className = "v2-override-input";
  ctxBranch.setAttribute("placeholder", "Branch");
  ctxBranch.setAttribute("maxlength", "100");

  const ctxHead = document.createElement("input");
  ctxHead.type = "text";
  ctxHead.id = "v2HandoffHead";
  ctxHead.className = "v2-override-input";
  ctxHead.setAttribute("placeholder", "Expected HEAD SHA");
  ctxHead.setAttribute("maxlength", "40");

  const ctxTask = document.createElement("input");
  ctxTask.type = "text";
  ctxTask.id = "v2HandoffTask";
  ctxTask.className = "v2-override-input";
  ctxTask.setAttribute("placeholder", "Task name");
  ctxTask.setAttribute("maxlength", "200");

  // Prompt output
  const output = document.createElement("textarea");
  output.id = "v2HandoffPrompt";
  output.className = "v2-textarea v2-handoff-prompt";
  output.rows = 8;
  output.readOnly = true;
  output.value = getHandoffPrompt(taskTypes[0], {});

  // Copy button row
  const copyRow = document.createElement("div");
  copyRow.className = "v2-handoff-copy-row";

  const copyBtn = document.createElement("button");
  copyBtn.type = "button";
  copyBtn.className = "v2-btn v2-btn-secondary v2-btn-inline";
  copyBtn.textContent = "복사";

  const copyFeedback = document.createElement("span");
  copyFeedback.id = "v2HandoffFeedback";
  copyFeedback.className = "v2-handoff-feedback";
  copyFeedback.textContent = "";

  // Helper to get current context
  function getCurrentContext() {
    return {
      repo: ctxRepo.value.trim(),
      issueNumber: ctxIssue.value.trim(),
      prNumber: ctxPR.value.trim(),
      branch: ctxBranch.value.trim(),
      expectedHead: ctxHead.value.trim(),
      taskName: ctxTask.value.trim()
    };
  }

  // Helper to update prompt
  function updatePrompt() {
    output.value = getHandoffPrompt(select.value, getCurrentContext());
    copyFeedback.textContent = "";
  }

  // Event handlers
  select.addEventListener("change", updatePrompt);

  ctxRepo.addEventListener("input", updatePrompt);
  ctxIssue.addEventListener("input", updatePrompt);
  ctxPR.addEventListener("input", updatePrompt);
  ctxBranch.addEventListener("input", updatePrompt);
  ctxHead.addEventListener("input", updatePrompt);
  ctxTask.addEventListener("input", updatePrompt);

  copyBtn.addEventListener("click", async () => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(output.value);
        copyFeedback.textContent = "복사됨";
      } else {
        output.select();
        document.execCommand("copy");
        copyFeedback.textContent = "복사됨";
      }
      setTimeout(() => { copyFeedback.textContent = ""; }, 2000);
    } catch (e) {
      output.select();
      copyFeedback.textContent = "수동으로 복사해주세요";
    }
  });

  copyRow.appendChild(copyBtn);
  copyRow.appendChild(copyFeedback);

  card.appendChild(select);
  card.appendChild(ctxRepo);
  card.appendChild(ctxIssue);
  card.appendChild(ctxPR);
  card.appendChild(ctxBranch);
  card.appendChild(ctxHead);
  card.appendChild(ctxTask);
  card.appendChild(output);
  card.appendChild(copyRow);

  section.appendChild(card);
  return section;
}

function injectHandoffSection() {
  const root = document.getElementById("boardV2Root");
  if (!root) return;

  const existing = document.getElementById("v2-handoff-container");
  if (existing) existing.remove();

  const container = document.createElement("div");
  container.id = "v2-handoff-container";
  container.appendChild(renderHandoffSection());

  const layout = root.querySelector(".v2-layout");
  if (layout) {
    layout.appendChild(container);
    return;
  }

  root.appendChild(container);
}

// Expose globally for board-v2.js to call
window.injectHandoffSection = injectHandoffSection;
