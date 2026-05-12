function renderList(items, emptyText, metaFormatter, itemActionsRenderer) {
  if (!items || !items.length) {
    return `<p class="v2-empty">${escapeHtml(emptyText)}</p>`;
  }

  return `
    <ul class="v2-list">
      ${items.map((item) => {
        const meta = metaFormatter(item);
        const clickableClass = item.description || item.reason || item.impact_summary ? " v2-modal-clickable" : "";
        const dataAttrs = clickableClass
          ? `data-v2-modal="open" data-v2-modal-title="${escapeHtml(item.title)}" data-v2-modal-content="${escapeHtml(item.description || item.reason || item.impact_summary || "")}"`
          : "";
        
        // Plan bucket badge logic
        const bucket = item.bucket || item.status;
        const bucketLabel = formatPlanLabel(bucket);
        const hasBucketLabel = bucket && bucketLabel && bucket !== 'active' && bucket !== 'done';
        const bucketClass = hasBucketLabel ? ` v2-plan-badge-${bucket}` : "";

        const actionsHtml = itemActionsRenderer ? itemActionsRenderer(item) : "";

        return `
          <li class="v2-list-item${clickableClass}" ${dataAttrs}>
            <div style="display:flex; align-items:flex-start; gap:0;">
              ${hasBucketLabel ? `<span class="v2-plan-badge${bucketClass}">${escapeHtml(bucketLabel)}</span>` : ""}
              <span class="v2-item-title" style="flex:1;">${escapeHtml(item.title)}</span>
            </div>
            <span class="v2-item-meta${meta.isDue ? ' -due' : ''}">${escapeHtml(meta.text)}</span>
            ${actionsHtml}
          </li>
        `;
      }).join("")}
    </ul>
  `;
}

function renderBriefList(items) {
  if (!items || !items.length) {
    return `<p class="v2-empty">브리프가 없습니다.</p>`;
  }

  return `
    <ul class="v2-list v2-list-compact">
      ${items.map((item) => {
        const title = item.title || "브리프";
        const content = item.content_md || "내용이 없습니다.";
        return `
          <li class="v2-list-item v2-modal-clickable" data-v2-modal="open" data-v2-modal-title="${escapeHtml(title)}" data-v2-modal-content="${escapeHtml(content)}">
            <span class="v2-item-title">${escapeHtml(title)}</span>
            <span class="v2-item-meta">${escapeHtml(summarizeBrief(item))}</span>
          </li>
        `;
      }).join("")}
    </ul>
  `;
}

function renderSessionList(items) {
  if (!items || !items.length) {
    return `<p class="v2-empty">최근 세션이 없습니다.</p>`;
  }

  return `
    <ul class="v2-list v2-list-compact">
      ${items.map((item) => `
        <li class="v2-list-item">
          <span class="v2-item-title">${escapeHtml(item.title || item.project_key || "세션")}</span>
          <span class="v2-item-meta">${escapeHtml(item.agent_name || "agent")} · ${escapeHtml(formatSessionStatus(item.status))}</span>
        </li>
      `).join("")}
    </ul>
  `;
}

function renderQuickInputSection() {
  return `
    <section class="v2-quick-input-card">
      <span class="v2-section-label">빠른 입력</span>
      <textarea id="v2QuickInput" class="v2-quick-input-textarea" 
        placeholder="오늘 할 일, 기한, 아이디어 등을 자유롭게 입력하세요 (Enter: 전송)">${escapeHtml(_quickInputDraft)}</textarea>
      <div class="v2-quick-input-actions">
        <button type="button" class="v2-btn v2-btn-primary v2-btn-inline" data-v2-action="quick-input-submit">전송</button>
      </div>
    </section>
  `;
}

function renderOverdueActions(item) {
  return `
    <div class="v2-item-actions">
      <button class="v2-action-btn -done" type="button" data-v2-action="overdue-done" data-v2-item-id="${escapeHtml(item.id)}" data-v2-item-title="${escapeHtml(item.title)}">완료</button>
      <button class="v2-action-btn -move" type="button" data-v2-action="overdue-reschedule" data-v2-item-id="${escapeHtml(item.id)}" data-v2-item-title="${escapeHtml(item.title)}">재배치</button>
      <button class="v2-action-btn -hold" type="button" data-v2-action="overdue-hold" data-v2-item-id="${escapeHtml(item.id)}" data-v2-item-title="${escapeHtml(item.title)}">보류</button>
    </div>
  `;
}
