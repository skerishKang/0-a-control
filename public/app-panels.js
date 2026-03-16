/**
 * Panel Control Module
 */

function openReportPanel() {
  const panel = document.getElementById("reportPanel");
  const backdrop = document.getElementById("panelBackdrop");
  closeDetailPanel();
  closeExternalContextPanel();
  if (!panel || !backdrop) return;
  panel.hidden = false;
  panel.classList.add("open");
  panel.setAttribute("aria-hidden", "false");
  backdrop.hidden = false;
  document.body.classList.add("panel-open");
}

function closeReportPanel() {
  const panel = document.getElementById("reportPanel");
  const backdrop = document.getElementById("panelBackdrop");
  if (!panel || !backdrop) return;
  panel.classList.remove("open");
  panel.setAttribute("aria-hidden", "true");
  backdrop.hidden = true;
  document.body.classList.remove("panel-open");
  window.setTimeout(() => {
    if (!panel.classList.contains("open")) {
      panel.hidden = true;
    }
  }, 180);
}

function openDetailPanel(label, title, bodyHtml) {
  const panel = document.getElementById("detailPanel");
  const backdrop = document.getElementById("panelBackdrop");
  closeReportPanel();
  closeExternalContextPanel();
  if (!panel || !backdrop) return;
  document.getElementById("detailPanelLabel").textContent = label;
  document.getElementById("detailPanelTitle").textContent = title;
  document.getElementById("detailPanelBody").innerHTML = bodyHtml;
  panel.hidden = false;
  panel.classList.add("open");
  panel.setAttribute("aria-hidden", "false");
  backdrop.hidden = false;
  document.body.classList.add("panel-open");
}

function closeDetailPanel() {
  const panel = document.getElementById("detailPanel");
  const backdrop = document.getElementById("panelBackdrop");
  if (!panel || !backdrop) return;
  panel.classList.remove("open");
  panel.setAttribute("aria-hidden", "true");
  backdrop.hidden = true;
  document.body.classList.remove("panel-open");
  window.setTimeout(() => {
    if (!panel.classList.contains("open")) {
      panel.hidden = true;
    }
  }, 180);
}

function openExternalContextPanel() {
  const panel = document.getElementById("externalContextPanel");
  const backdrop = document.getElementById("panelBackdrop");
  closeReportPanel();
  closeDetailPanel();
  if (!panel || !backdrop) return;
  panel.hidden = false;
  panel.classList.add("open");
  panel.setAttribute("aria-hidden", "false");
  backdrop.hidden = false;
  document.body.classList.add("panel-open");
  if (window.refreshExternalContextPanelData) {
    window.refreshExternalContextPanelData();
  }
}

function closeExternalContextPanel() {
  const panel = document.getElementById("externalContextPanel");
  const backdrop = document.getElementById("panelBackdrop");
  if (!panel || !backdrop) return;
  panel.classList.remove("open");
  panel.setAttribute("aria-hidden", "true");
  backdrop.hidden = true;
  document.body.classList.remove("panel-open");
  window.setTimeout(() => {
    if (!panel.classList.contains("open")) {
      panel.hidden = true;
    }
  }, 180);
}

function closeSessionPanel() {
  // Placeholder for session panel closure if needed
}
