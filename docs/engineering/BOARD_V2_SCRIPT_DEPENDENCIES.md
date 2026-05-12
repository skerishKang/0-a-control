# Board V2 Script Dependency Map

Refs #116.

## Purpose

`public/board-v2.html` currently loads board-v2 scripts in a fixed order. This document records the dependency chain so future changes do not accidentally break global symbols or implicit initialization order.

This is a documentation-only baseline. It does not change runtime behavior.

## Current entrypoint

- HTML entrypoint: `public/board-v2.html`
- Runtime entrypoint: `public/board-v2.js`
- Primary root element: `#boardV2Root`
- Modal elements: `#v2Modal`, `#v2ModalTitle`, `#v2ModalBody`

## Current script order

The board currently depends on the following order:

1. `board-v2-api.js`
2. `board-v2-overrides.js`
3. `board-v2-handoff.js`
4. `board-v2-ops.js`
5. `board-v2-guardrails.js`
6. `board-v2-shared.js`
7. `board-v2-selectors.js`
8. `board-v2-phase.js`
9. `board-v2-render.js`
10. `board-v2-render-morning.js`
11. `board-v2-render-progress.js`
12. `board-v2-render-eod.js`
13. `board-v2-render-completed.js`
14. `board-v2.js`

## Producer / consumer map

| Producer | Expected globals or behavior | Known consumers |
| --- | --- | --- |
| `board-v2-api.js` | `boardApi` API facade | `board-v2.js`, optional panel modules |
| `board-v2-shared.js` | shared state, formatting, escaping helpers | render modules, phase/selectors modules |
| `board-v2-selectors.js` | state selection helpers | phase/render modules |
| `board-v2-phase.js` | phase derivation and tab/status render helpers | `board-v2.js` |
| `board-v2-render.js` | shared render helpers such as list/brief/session/quick input rendering | phase-specific render modules |
| `board-v2-render-morning.js` | morning layout rendering | dispatch render path |
| `board-v2-render-progress.js` | progress layout rendering | dispatch render path |
| `board-v2-render-eod.js` | end-of-day layout rendering | dispatch render path |
| `board-v2-render-completed.js` | completed layout rendering | dispatch render path |
| `board-v2-overrides.js` | manual override fetch/render/action helpers | `board-v2.js` |
| `board-v2-handoff.js` | executor handoff panel helpers | `board-v2.js` |
| `board-v2-ops.js` | operations summary injection | `board-v2.js` |
| `board-v2-guardrails.js` | settings/guardrails injection | `board-v2.js` |
| `board-v2.js` | bootstraps polling, clock, modal, global action handlers | DOMContentLoaded |

## Fragile areas

1. `board-v2.js` assumes helper functions from earlier files already exist.
2. Render files depend on global state/helpers rather than explicit imports.
3. Inline handlers in generated HTML assume `window.boardV2*` functions are present.
4. Optional panel injectors are called through `window.*`, so missing scripts can fail late.

## Near-term guardrails

- Add new board-v2 scripts before `board-v2.js` unless they are explicitly lazy-loaded.
- Do not reorder `board-v2-shared.js`, selectors, phase, and render files without validating the board load path.
- Keep producer/consumer changes reflected in this document.
- Prefer adding a small explicit facade over adding more untracked globals.

## Migration path

A future refactor can move toward a single module entrypoint:

```html
<script type="module" src="/app/main.js"></script>
```

Suggested module layout:

```text
public/app/
  main.js
  api.js
  state.js
  phase.js
  render/
    shared.js
    morning.js
    progress.js
    eod.js
    completed.js
  panels/
    overrides.js
    handoff.js
    ops.js
    guardrails.js
```

The first migration PR should be behavior-preserving and should only convert one small helper cluster to explicit imports.