// Delegated event handlers for board-v2 render output.
// Keeps render modules free of inline event attributes.
(function setupBoardV2DelegatedActions() {
  function getActionTarget(event) {
    return event.target?.closest?.("[data-v2-action]") || null;
  }

  document.addEventListener("input", function handleBoardV2Input(event) {
    if (event.target?.id === "v2QuickInput") {
      window.boardV2SyncQuickInputDraft?.();
    }
  });

  document.addEventListener("click", function handleBoardV2Click(event) {
    const target = getActionTarget(event);
    if (!target) return;

    const action = target.getAttribute("data-v2-action");
    if (!action) return;

    if (action === "quick-input-submit") {
      event.preventDefault();
      window.boardV2SubmitQuickInput?.();
      return;
    }

    if (action.startsWith("overdue-")) {
      event.preventDefault();
      event.stopPropagation();
      const id = target.getAttribute("data-v2-item-id") || "";
      const title = target.getAttribute("data-v2-item-title") || "";

      if (action === "overdue-done") {
        window.boardV2ActionOverdueDone?.(id, title);
      } else if (action === "overdue-reschedule") {
        window.boardV2ActionOverdueReschedule?.(id, title);
      } else if (action === "overdue-hold") {
        window.boardV2ActionOverdueHold?.(id, title);
      }
    }
  });
})();
