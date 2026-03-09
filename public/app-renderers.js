/**
 * Common Renderers and Helper UI components
 */

function showDetailedList(label, title, items, formatter) {
  const bodyHtml = `
    <div class="list detailed-list-in-panel reading-flow">
      ${items.map(formatter).join("")}
    </div>
  `;
  openDetailPanel(label, title, bodyHtml);
}

// Low-level helper functions for list rendering are still here
// Section-specific high-level renderers moved to app-support.js or app-hero.js
