# Legacy CSS Split Audit

**Issue:** #87  
**Date:** May 12, 2026  
**Status:** Audit Complete

## 1. Target Files and Current Line Counts

| File | Lines | Status |
|------|-------|--------|
| public/styles.css | 883 | > 500 |
| public/panels-detail.css | 634 | > 500 |

## 2. File Structure Analysis

### public/styles.css (883 lines)

**Responsibility Groups:**

1. **Global/Base Styles (1-52)**
   - CSS custom properties (`:root`) - lines 1-14
   - Global reset (`*`) - lines 16-18
   - Body base styles - lines 20-32

2. **Zone Section Wrappers (34-72)**
   - `.zone-section`, `.zone-title` - lines 35-52
   - `.zone-mission`, `.zone-support`, `.zone-review` - lines 54-72

3. **Agent Status Badges (112-135)**
   - `.agent-status-badge.working`, `.idle`, `.stale`, `.error`, `.unavailable`

4. **Layout/Shell Styles (137-220)**
   - `.layout`, `.hero-card`, `.panel` - lines 137-152
   - `.panel-head`, `.count-badge` - lines 89-110

5. **Component/Card Styles (154-451)**
   - `.hero-card` variants - lines 158-445
   - `.mission-progress` - lines 286-303
   - `.criteria-box`, `.quest-focus-box` - lines 317-352
   - `.mission-grid` - lines 354-372

6. **Form/Input/Button Styles (608-445)**
   - `.quest-form`, `.field` - lines 608-632
   - `.mission-reason-btn`, `.mission-subhead-btn` - lines 231-264
   - `.header-action-btn` - lines 266-284

7. **Responsive/Media Query Sections (201-737)**
   - `@media (max-width: 860px)` - lines 201-220
   - `@media (max-width: 760px)` - lines 447-451
   - `@media (max-width: 860px)` (second block) - lines 701-737

8. **Bridge Panel Styles (739-1035)**
   - `.bridge-panel`, `.bridge-header`, `.bridge-content` - lines 739-772
   - Bridge candidate/items styles - lines 745-1008

### public/panels-detail.css (634 lines)

**Responsibility Groups:**

1. **Panel/Side Panel Styles (1-60)**
   - `.side-panel`, `.side-panel-header`, `.side-panel-body` - lines 1-60
   - `.panel-backdrop` - lines 55-60

2. **Verdict Card Styles (62-103)**
   - `.verdict-card`, `.verdict-summary` - lines 62-94

3. **Detail/Side Panel Content (105-290)**
   - `.detail-body`, `.detail-section`, `.reading-flow` - lines 105-124
   - `.conversation-thread`, `.conversation-row` - lines 263-334

4. **Filter/Chip Styles (131-152, 354-365)**
   - `.filter-chip-row`, `.filter-chip` - lines 131-152, 354-365

5. **External Context Layout (154-240)**
   - `.external-context-layout` - lines 183-191
   - `.external-context-list-panel`, `.external-context-detail-panel` - lines 193-218

6. **Telegram-Specific Styles (409-712)**
   - `.telegram-sync-btn` - lines 409-432
   - `.telegram-status-chip` - lines 621-642
   - `.telegram-setup-hint` - lines 643-664
   - `.telegram-source-pill` - lines 666-712

7. **Responsive Rules (434-739)**
   - `@media (max-width: 1040px)` - lines 434-442, 729-733
   - `@media (max-width: 720px)` - lines 735-739

## 3. Coupling Risks

### Stylesheet Load Order
- `styles.css` is the primary stylesheet; `panels-detail.css` is secondary
- Both share CSS custom properties from `styles.css` (`:root`)
- `panels-detail.css` depends on `--panel`, `--line`, `--text`, `--muted`, `--accent`, `--red` from `styles.css`

### Shared CSS Custom Properties
- `:root` variables defined in `styles.css` (lines 1-14)
- Used in both files: `--panel`, `--line`, `--text`, `--muted`, `--accent`, `--red`

### Global Selectors
- `*.panel`, `*.card` styles in `styles.css` may affect elements in `panels-detail.css`
- `.filter-chip` defined in both files (potential override conflict)

### HTML References
- `public/index.html` loads `styles.css`
- `panels-detail.css` is loaded conditionally via HTML templates or JS

## 4. Proposed Safe Split Phases

### Phase 1: Extract Bridge Panel CSS
**Target:** `styles.css` lines 739-1035 (bridge component)
- Creates `public/css/components/bridge.css`
- Self-contained component with minimal dependencies
- Low risk - only affects bridge panel

### Phase 2: Extract Telegram Panel CSS
**Target:** `panels-detail.css` lines 409-712 (Telegram-specific)
- Creates `public/css/components/telegram-panel.css`
- Panel-detail scoped, clear boundaries
- Medium risk - verify external-context dependencies

### Phase 3: Extract Form/Button Utilities
**Target:** Both files' button/form styles
- Creates `public/css/components/buttons.css`
- Shared utility classes
- Medium risk - verify all button variants work

### Phase 4: Extract Responsive Rules
**Target:** Media queries from both files
- Creates `public/css/responsive.css`
- Load after main stylesheets
- Low risk if loaded correctly

### Phase 5: Cleanup Unused Selectors
**Target:** Audit and remove unused selectors
- After visual verification
- Requires browser devtools analysis
- Low risk after confirmation

## 5. Explicit Non-Goals

- ❌ No visual redesign
- ❌ No selector renaming
- ❌ No HTML structure changes
- ❌ No JS behavior changes
- ❌ No server/backend changes
- ❌ No runtime data changes

## 6. Validation Requirements for Implementation PRs

Each implementation PR must pass:

```bash
# Stylesheet load order review
# grep selectors against public/*.html and public/*.js
# Verify no broken links
# Browser smoke/manual visual verification
# No runtime data staging
```

## 7. Recommended First Implementation Slice

### Phase 1: Extract Bridge Panel CSS

**Target Module:** `public/css/components/bridge.css` (new file)

**Content to extract:** `styles.css` lines 739-1035

**Expected changes:**
- Create `bridge.css` (~300 lines)
- Remove extracted lines from `styles.css`

**Risk Level:** LOW
- Self-contained component
- Clear boundaries
- Easy rollback

**Line reduction estimate:**
- `styles.css`: 883 → ~583 (-300 lines)

**Rollback Plan:**
1. Delete `bridge.css`
2. Restore extracted lines in `styles.css`
3. No HTML changes required

## 8. Summary

| Phase | Description | Risk | Line Reduction |
|-------|-------------|------|----------------|
| 1 | Bridge panel extraction | LOW | ~300 lines |
| 2 | Telegram panel extraction | MED | ~200 lines |
| 3 | Button/form utilities | MED | ~100 lines |
| 4 | Responsive rules | LOW | ~50 lines |
| 5 | Cleanup unused | LOW | Variable |

**Recommended start:** Phase 1 (bridge panel extraction) - lowest risk, self-contained component