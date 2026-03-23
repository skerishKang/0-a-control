/**
 * Today Summary and Unfinished Plans rendering module for Classic UI
 */

function normalizeDayPhaseLabel(value) {
  return {
    "in-progress": "진행 중",
    morning: "아침 정리",
    midday: "진행 중",
    end_of_day: "마감 정리",
  }[String(value || "").trim()] || value || "미정";
}

function renderTodaySummarySection(state) {
  const targetId = "todaySummaryList";
  const container = document.getElementById(targetId);
  if (!container) return;
  const parentPanel = container.parentElement;
  if (parentPanel) parentPanel.classList.add("panel-browsing");

  const current = state.currentState || {};
  const progress = current.day_progress_summary || {};
  const verdict = current.recent_verdict || {};
  const datedPressure = current.dated_pressure_summary || [];
  const recommendedNext = current.recommended_next_quest || "";
  const dayPhase = current.day_phase || "";
  const todayDone = current.today_done_quests || [];
  const tomorrowFirst = current.tomorrow_first_quest || null;
  const confirmedStart = current.confirmed_starting_point || null;

  const items = [];
  const done = progress.done || 0;
  const partial = progress.partial || 0;

  // end-of-day 마감 처리 권장 신호
  if (dayPhase === "end-of-day") {
    items.push({ label: "마감", value: "정리 권장", type: "closing" });
  }

  if (done > 0) items.push({ label: "완료", value: `${done}건`, type: "done" });
  if (partial > 0) items.push({ label: "부분", value: `${partial}건`, type: "partial" });

  const questStatus = verdict.status || "none";
  if (questStatus === "done") {
    items.push({ label: "최근 판정", value: "완료", type: "done" });
  } else if (questStatus === "partial") {
    items.push({ label: "최근 판정", value: "부분", type: "partial" });
  } else if (questStatus === "hold") {
    items.push({ label: "최근 판정", value: "보류", type: "hold" });
  }

  if (datedPressure.length > 0) {
    const urgent = datedPressure[0];
    items.push({ label: "주의", value: urgent.title?.slice(0, 20) || "항목 없음", type: "risk" });
  }

  if (recommendedNext) {
    const short = recommendedNext.length > 25 ? `${recommendedNext.slice(0, 25)}...` : recommendedNext;
    items.push({ label: "다음", value: short, type: "action" });
  }

  if (tomorrowFirst && tomorrowFirst.title) {
    const short = tomorrowFirst.title.length > 20 ? `${tomorrowFirst.title.slice(0, 20)}...` : tomorrowFirst.title;
    items.push({ label: "내일 첫 퀘스트", value: short, type: "suggestion" });
  }

  if (items.length === 0) {
    container.innerHTML = `<div class="list-item empty">오늘 판단 요약이 아직 없습니다.</div>`;
  } else {
    container.innerHTML = items.slice(0, 4).map(item => `
      <div class="list-item summary-item">
        <span class="summary-label">${escapeHtml(item.label)}</span>
        <span class="summary-value ${item.type}">${escapeHtml(item.value)}</span>
      </div>
    `).join("");
  }

  if (parentPanel) {
    parentPanel.onclick = () => {
      const detailItems = [
        {
          title: "오늘 진행 요약",
          detail: `완료 ${done}건 / 부분 ${partial}건`,
        },
        {
          title: "최근 판정 상태",
          detail: verdict.status ? labelStatus(verdict.status) : "판정 없음",
        },
        {
          title: "추천 다음 행동",
          detail: recommendedNext || "추천 없음",
        },
        {
          title: "오늘 단계",
          detail: normalizeDayPhaseLabel(dayPhase),
        },
      ];

      // 오늘 완료된 quest 목록
      if (todayDone.length > 0) {
        detailItems.push({
          title: "--- 오늘 완료된 퀘스트 ---",
          detail: `${todayDone.length}건`,
        });
        todayDone.forEach((q) => {
          detailItems.push({
            title: `✓ ${q.title || "제목 없음"}`,
            detail: q.verdict_reason || q.updated_at || "",
          });
        });
      }

      // end-of-day 마감 권장 메시지
      if (dayPhase === "end-of-day") {
        detailItems.push({
          title: "🌙 마감 처리 권장",
          detail: "오늘 작업을 정리하고 미완료 항목의 재시작 전략을 정하세요. 미완료를 hold로 남기거나 단기 플랜으로 넘길 수 있습니다.",
        });
      }

      // 내일 첫 퀘스트 제안
      if (tomorrowFirst && tomorrowFirst.title) {
        const sourceLabel = tomorrowFirst.source === "today_hold" ? "오늘 미완료 → 계속" : "단기 플랜 → 이동";
        detailItems.push({
          title: `🌅 내일 첫 퀘스트`,
          detail: `<strong>${escapeHtml(tomorrowFirst.title)}</strong><br><span class="muted">${escapeHtml(tomorrowFirst.reason || "")} (${sourceLabel})</span>`,
        });
      }

      // confirmed_starting_point: 사용자가 확정한 내일 첫 퀘스트 (아직 자동 연동)
      if (confirmedStart && confirmedStart.title) {
        const isPromotable = !current.current_quest_id;
        const actionHtml = isPromotable
          ? `<div style="margin-top:8px; display:flex; gap:8px;">
               <button type="button" class="primary-btn" onclick="promoteStartingPoint()">이 약속으로 작업 시작</button>
               <button type="button" class="secondary-btn" onclick="clearStartingPoint()">이 약속 비우기</button>
             </div>`
          : `<div style="margin-top:8px; display:flex; gap:8px;">
               <button type="button" class="primary-btn" disabled title="이미 진행 중인 퀘스트가 있습니다">이 약속으로 작업 시작</button>
               <button type="button" class="secondary-btn" onclick="clearStartingPoint()">이 약속 비우기</button>
             </div>`;

        detailItems.push({
          title: `✅ 내일 첫 퀘스트 (확인됨)`,
          detail: `<strong>${escapeHtml(confirmedStart.title)}</strong><br><span class="muted">${escapeHtml(confirmedStart.reason || "")} · ${confirmedStart.confirmed_at || ""}</span>${actionHtml}`,
        });
      }

      // dated pressure
      datedPressure.slice(0, 5).forEach((item) => {
        detailItems.push({
          title: `주의 일정: ${item.title || "항목 없음"}`,
          detail: item.due_at || item.why_now || "세부 정보 없음",
        });
      });

      showDetailedList("오늘 운영 요약", "오늘 상태를 요약한 상세 보기", detailItems, (i) => `
        <div class='list-item'>
          <strong>${escapeHtml(i.title)}</strong>
          <p class='muted'>${escapeHtml(i.detail || "-")}</p>
        </div>
      `);
    };
  }
}

function renderUnfinishedPlansSection(state) {
  const targetId = "unfinishedPlanList";
  const container = document.getElementById(targetId);
  if (!container) return;

  const plans = state.plans || [];
  const unfinished = plans.filter(p => p.status && !["done", "rejected", "archived"].includes(p.status));
  const count = unfinished.length;

  const countEl = document.getElementById("unfinishedPlanCount");
  if (countEl) countEl.textContent = String(count);

  if (count === 0) {
    container.innerHTML = `<div class="list-item empty">미완료 플랜이 없습니다.</div>`;
    return;
  }

  const topItems = unfinished.slice(0, 4);
  container.innerHTML = topItems.map(plan => `
    <div class="list-item">
      <div class="candidate-head">
        <strong>${escapeHtml(plan.title)}</strong>
        <span class="session-badge verdict ${escapeHtml(plan.status || "pending")}">${escapeHtml(labelStatus(plan.status))}</span>
      </div>
      <span class="candidate-reason">${escapeHtml(plan.due_at || labelBucket(plan.bucket) || "-")}</span>
    </div>
  `).join("");
}

window.promoteStartingPoint = async function promoteStartingPoint() {
  if (!window.confirm("어제 확정한 시작점으로 작업을 시작할까요?")) return;
  
  try {
    const response = await fetch("/api/tomorrow-first-quest/promote", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "승격에 실패했습니다.");
    }
    
    const modal = document.getElementById("detailedListModal");
    if (modal) modal.style.display = "none";
    
    if (window.loadAll) await window.loadAll();
    alert("퀘스트를 시작했습니다. 작업 일지를 유지하세요.");
  } catch (error) {
    console.error("Failed to promote starting point:", error);
    alert(`작업 시작 실패: ${error.message}`);
  }
};

window.clearStartingPoint = async function clearStartingPoint() {
  if (!window.confirm("확정된 시작점을 비울까요?")) return;
  
  try {
    const response = await fetch("/api/tomorrow-first-quest/clear", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "비우기에 실패했습니다.");
    }
    
    // 성공 시 모달 닫기 및 전체 새로고침
    const modal = document.getElementById("detailedListModal");
    if (modal) modal.style.display = "none";
    
    if (window.loadAll) await window.loadAll();
    alert("시작점을 비웠습니다.");
  } catch (error) {
    console.error("Failed to clear starting point:", error);
    alert(`비우기 실패: ${error.message}`);
  }
};
