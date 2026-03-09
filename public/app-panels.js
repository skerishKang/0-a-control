/**
 * Panel Control Module
 */

function openReportPanel() {
  const panel = document.getElementById("reportPanel");
  const backdrop = document.getElementById("panelBackdrop");
  closeDetailPanel();
  if (!panel || !backdrop) return;
  panel.hidden = false;
  panel.classList.add("open");
  panel.setAttribute("aria-hidden", "false");
  backdrop.hidden = false;
}

function closeReportPanel() {
  const panel = document.getElementById("reportPanel");
  const backdrop = document.getElementById("panelBackdrop");
  if (!panel || !backdrop) return;
  panel.classList.remove("open");
  panel.setAttribute("aria-hidden", "true");
  backdrop.hidden = true;
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
  if (!panel || !backdrop) return;
  document.getElementById("detailPanelLabel").textContent = label;
  document.getElementById("detailPanelTitle").textContent = title;
  document.getElementById("detailPanelBody").innerHTML = bodyHtml;
  panel.hidden = false;
  panel.classList.add("open");
  panel.setAttribute("aria-hidden", "false");
  backdrop.hidden = false;
}

function closeDetailPanel() {
  const panel = document.getElementById("detailPanel");
  const backdrop = document.getElementById("panelBackdrop");
  if (!panel || !backdrop) return;
  panel.classList.remove("open");
  panel.setAttribute("aria-hidden", "true");
  backdrop.hidden = true;
  window.setTimeout(() => {
    if (!panel.classList.contains("open")) {
      panel.hidden = true;
    }
  }, 180);
}

function closeSessionPanel() {
  // Placeholder for session panel closure if needed
}
