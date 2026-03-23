/**
 * Plans rendering module for Classic UI
 */

function renderPlansSection(state) {
  const current = state.currentState || {};
  const plans = state.plans || [];
  const markAsBrowsing = (id) => document.getElementById(id)?.parentElement.classList.add('panel-browsing');

  markAsBrowsing('dueSoonList');
  markAsBrowsing('shortTermList');
  markAsBrowsing('longTermList');
  markAsBrowsing('recurringList');

  setCountBadge("dueSoonCount", byBucket(plans, "dated").length);
  setCountBadge("shortTermCount", byBucket(plans, "short_term").length);
  setCountBadge("longTermCount", byBucket(plans, "long_term").length);
  setCountBadge("recurringCount", byBucket(plans, "recurring").length);

  const planFormatter = (item) => `
    <div class="list-item signal-item">
      <div class="signal-head">
        <strong>${escapeHtml(item.title)}</strong>
        <span class="session-badge verdict ${escapeHtml(item.status || "pending")}">${escapeHtml(labelStatus(item.status))}</span>
      </div>
      <span>${escapeHtml(item.due_at || labelBucket(item.bucket))}</span>
    </div>
  `;

  const detailFormatter = (secondary) => (i) => `
    <div class='list-item'><strong>${escapeHtml(i.title)}</strong> <span>${escapeHtml(secondary(i))}</span></div>
  `;

  renderCappedList("dueSoonList", byBucket(plans, "dated"), planFormatter, 3, "이번 달 예정된 고정 기한 일정이 없습니다.");
  document.getElementById("dueSoonList")?.parentElement?.addEventListener("click", () => {
    showDetailedList("기한 임박", "기한 고정 플랜", byBucket(state.plans, "dated"), detailFormatter((i) => i.due_at));
  }, { once: true });

  renderCappedList("shortTermList", byBucket(plans, "short_term"), planFormatter, 3, "현재 집중해야 할 단기 계획이 비어 있습니다.");
  document.getElementById("shortTermList")?.parentElement?.addEventListener("click", () => {
    showDetailedList("단기 플랜", "단기 계획", byBucket(state.plans, "short_term"), detailFormatter((i) => labelStatus(i.status)));
  }, { once: true });

  renderCappedList("longTermList", byBucket(plans, "long_term"), planFormatter, 3, "장기적 관점에서 준비 중인 프로젝트가 없습니다.");
  document.getElementById("longTermList")?.parentElement?.addEventListener("click", () => {
    showDetailedList("장기 플랜", "장기 계획", byBucket(state.plans, "long_term"), detailFormatter((i) => labelStatus(i.status)));
  }, { once: true });

  renderCappedList("recurringList", byBucket(plans, "recurring"), planFormatter, 3, "주기적으로 검토할 반복 일정이 설정되지 않았습니다.");
  document.getElementById("recurringList")?.parentElement?.addEventListener("click", () => {
    showDetailedList("반복 플랜", "반복 계획", byBucket(state.plans, "recurring"), detailFormatter((i) => labelStatus(i.status)));
  }, { once: true });
}
