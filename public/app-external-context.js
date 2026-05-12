/**
 * app-external-context.js — External inbox context panel operations
 * Extracted from app.js (lines 223-333) to reduce file size below 500-line limit
 */

async function refreshExternalContextPanelData() {
  const status = state.externalContextStatus || "new";
  const category = state.externalContextSource && state.externalContextSource !== "all"
    ? `&category=${encodeURIComponent(
        state.externalContextSource === "core" ? "핵심4개" :
        state.externalContextSource === "stock" ? "주식큐레이터" :
        state.externalContextSource === "news" ? "뉴스" :
        state.externalContextSource === "general" ? "일반대화" : state.externalContextSource
      )}`
    : "";

  try {
    const payload = await fetchJson(`/api/external-inbox?limit=1000&status=${encodeURIComponent(status)}${category}`);
    state.externalInboxPanel = {
      items: payload?.items || [],
    };
    renderExternalContextPanel(state);
  } catch (error) {
    console.error("Failed to refresh external context panel:", error);
  }
}

window.refreshExternalContextPanelData = refreshExternalContextPanelData;

function mergeExternalContextThread(existingThread, payload) {
  if (!payload) return null;
  if (!existingThread || existingThread.source_id !== payload.source_id) {
    return {
      ...payload,
      loaded_days: Array.isArray(payload.loaded_days) ? payload.loaded_days : (payload.day ? [payload.day] : []),
      loadingOlder: false,
    };
  }

  const mergedMessages = [...(payload.messages || []), ...(existingThread.messages || [])];
  const dedupedMessages = Array.from(
    new Map(
      mergedMessages.map((message) => [
        `${message.id || ""}:${message.external_message_id || ""}:${message.display_timestamp || message.imported_at || ""}`,
        message,
      ])
    ).values()
  );
  dedupedMessages.sort((a, b) =>
    String(a.display_timestamp || a.item_timestamp || a.imported_at || "").localeCompare(
      String(b.display_timestamp || b.item_timestamp || b.imported_at || "")
    )
  );

  const loadedDays = Array.from(new Set([...(payload.loaded_days || []), ...(existingThread.loaded_days || [])])).sort();
  return {
    ...existingThread,
    ...payload,
    messages: dedupedMessages,
    loaded_days: loadedDays,
    loadingOlder: false,
  };
}

async function refreshExternalContextThread(sourceId) {
  if (!sourceId) {
    state.externalContextThread = null;
    renderExternalContextPanel(state);
    return;
  }

  try {
    const payload = await fetchJson(`/api/external-inbox/source?source_id=${encodeURIComponent(sourceId)}&day=today&limit=500`);
    state.externalContextThread = mergeExternalContextThread(null, payload);
    renderExternalContextPanel(state);
  } catch (error) {
    console.error("Failed to refresh external context thread:", error);
  }
}

window.refreshExternalContextThread = refreshExternalContextThread;

async function loadOlderExternalContextDay() {
  const thread = state.externalContextThread;
  if (!thread?.source_id || !thread.previous_day || thread.loadingOlder) {
    return;
  }

  const detail = document.getElementById("externalContextDetail");
  const previousHeight = detail ? detail.scrollHeight : 0;
  const previousTop = detail ? detail.scrollTop : 0;
  thread.loadingOlder = true;
  renderExternalContextPanel(state);

  try {
    const payload = await fetchJson(
      `/api/external-inbox/source?source_id=${encodeURIComponent(thread.source_id)}&before=${encodeURIComponent(thread.day)}&limit=500`
    );
    state.externalContextThread = mergeExternalContextThread(thread, payload);
    renderExternalContextPanel(state);

    if (detail) {
      requestAnimationFrame(() => {
        const currentDetail = document.getElementById("externalContextDetail");
        if (!currentDetail) return;
        currentDetail.scrollTop = currentDetail.scrollHeight - previousHeight + previousTop;
      });
    }
  } catch (error) {
    console.error("Failed to load older external context day:", error);
    if (state.externalContextThread) {
      state.externalContextThread.loadingOlder = false;
    }
    renderExternalContextPanel(state);
  }
}

window.loadOlderExternalContextDay = loadOlderExternalContextDay;