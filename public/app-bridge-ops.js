/**
 * Bridge Quick Input - Plan parsing and creation
 */

let bridgeState = { parsed: null };

function openBridgePanel() {
  document.getElementById("bridgePanel").hidden = false;
  document.getElementById("bridgePanel").style.display = "block";
}

function closeBridgePanel() {
  document.getElementById("bridgePanel").hidden = true;
  document.getElementById("bridgePanel").style.display = "none";
  document.getElementById("bridgeInput").value = "";
  document.getElementById("bridgeResult").innerHTML = "";
  document.getElementById("bridgeCreatePlanBtn").disabled = true;
  bridgeState.parsed = null;
}

async function handleBridgeParse() {
  const text = document.getElementById("bridgeInput").value.trim();
  if (!text) return;

  const btn = document.getElementById("bridgeParseBtn");
  btn.disabled = true;
  btn.textContent = "정리 중...";

  try {
    const res = await fetchJson("/api/bridge/quick-input", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    bridgeState.parsed = res;

    const resultDiv = document.getElementById("bridgeResult");
    const candidates = res.candidates || [];
    const mainMission = res.main_mission;
    const currentQuest = res.current_quest;
    const summary = res.summary || {};

    const todayCandidates = candidates.filter(p => p.bucket === "today").sort((a, b) => (b.priority_score || 0) - (a.priority_score || 0));
    const datedCandidates = candidates.filter(p => p.bucket === "dated").sort((a, b) => (b.priority_score || 0) - (a.priority_score || 0));
    const holdCandidates = candidates.filter(p => p.bucket === "hold").sort((a, b) => (b.priority_score || 0) - (a.priority_score || 0));
    const otherCandidates = candidates.filter(p => !["today", "dated", "hold"].includes(p.bucket)).sort((a, b) => (b.priority_score || 0) - (a.priority_score || 0));

    const bucketLabels = {
      "today": "오늘",
      "dated": "기한",
      "hold": "보류",
      "short_term": "단기",
      "long_term": "장기",
      "recurring": "반복"
    };

    const bucketColors = {
      "today": "bridge-bucket-today",
      "dated": "bridge-bucket-dated",
      "hold": "bridge-bucket-hold",
      "short_term": "bridge-bucket-short",
      "long_term": "bridge-bucket-long",
      "recurring": "bridge-bucket-recurring"
    };

    let html = "";

    html += `<div class="bridge-summary">`;
    html += `<span class="bridge-count-badge bridge-bucket-today">${summary.today_count || 0}개 오늘</span>`;
    html += `<span class="bridge-count-badge bridge-bucket-dated">${summary.dated_count || 0}개 기한</span>`;
    html += `<span class="bridge-count-badge bridge-bucket-hold">${summary.hold_count || 0}개 보류</span>`;
    html += `</div>`;

    if (mainMission || currentQuest) {
      html += `<div class="bridge-priority-section">`;
      if (mainMission) {
        html += `<div class="bridge-highlight-card bridge-main-mission">
          <span class="bridge-priority-label">📌 메인 미션</span>
          <strong class="bridge-priority-title">${escapeHtml(mainMission.title)}</strong>
          <span class="bridge-priority-reason">${escapeHtml(mainMission.reason || "")}</span>
        </div>`;
      }
      if (currentQuest) {
        html += `<div class="bridge-highlight-card bridge-current-quest">
          <span class="bridge-priority-label">🎯 현재 퀘스트</span>
          <strong class="bridge-priority-title">${escapeHtml(currentQuest.title)}</strong>
          <span class="bridge-priority-reason">${escapeHtml(currentQuest.reason || "")}</span>
        </div>`;
      }
      html += `</div>`;
    }

    const renderCandidateSection = (items, label, icon) => {
      if (!items.length) return "";
      let section = `<div class="bridge-section">
  <p class="bridge-section-title">${icon} ${label} <span class="bridge-section-count">(${items.length}개)</span></p>
  <div class="bridge-candidates-list">`;
      items.forEach(p => {
        const score = p.priority_score ? `<span class="bridge-score-small">${p.priority_score}점</span>` : "";
        const due = p.due_date ? `<span class="bridge-due-small">${p.due_date}</span>` : "";
        section += `<div class="bridge-candidate-item">
  <span class="bridge-bucket-badge ${bucketColors[p.bucket] || ""}">${bucketLabels[p.bucket] || p.bucket}</span>
  <span class="bridge-candidate-title">${escapeHtml(p.title)}</span>
  <div class="bridge-candidate-meta">${score}${due}</div>
</div>`;
      });
      section += `</div></div>`;
      return section;
    };

    html += renderCandidateSection(todayCandidates, "오늘", "📅");
    html += renderCandidateSection(datedCandidates, "기한", "⏰");
    html += renderCandidateSection(holdCandidates, "보류", "⏸");
    html += renderCandidateSection(otherCandidates, "기타", "📋");

    resultDiv.innerHTML = html;

    document.getElementById("bridgeCreatePlanBtn").disabled = false;
  } catch (e) {
    alert("분류 실패: " + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "정리하기";
  }
}

async function handleBridgeCreatePlan() {
  if (!bridgeState.parsed?.candidates?.length) return;

  const btn = document.getElementById("bridgeCreatePlanBtn");
  btn.disabled = true;
  btn.textContent = "생성 중...";

  try {
    await fetchJson("/api/bridge/create-plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ candidates: bridgeState.parsed.candidates }),
    });

    alert("Plan이 생성되었습니다!");
    closeBridgePanel();
    loadAll();
  } catch (e) {
    alert("생성 실패: " + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Plan 생성";
  }
}

document.getElementById("openBridgePanelBtn")?.addEventListener("click", openBridgePanel);
document.getElementById("closeBridgePanelBtn")?.addEventListener("click", closeBridgePanel);
document.getElementById("bridgeParseBtn")?.addEventListener("click", handleBridgeParse);
document.getElementById("bridgeCreatePlanBtn")?.addEventListener("click", handleBridgeCreatePlan);
