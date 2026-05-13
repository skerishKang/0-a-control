# Static Asset Version Query Policy

## Reference

0-a-control adopts the **LoveBud/LoveTree manual static asset version query pattern** as the basis for this policy. That project's convention has proven effective for a static-deployment environment without a build pipeline, and this document codifies the same approach for 0-a-control.

## Format

```
v=YYYYMMDD-ISSUE-REV
```

| Part       | Meaning                                                    |
|------------|------------------------------------------------------------|
| `YYYYMMDD` | Date the change was made (UTC).                            |
| `ISSUE`    | GitHub issue number that motivated the version bump.       |
| `REV`      | Sequential revision counter starting at 1 for that issue.  |

### Example

```html
<link rel="stylesheet" href="/css/components/v1-base.css?v=20260513-183-1" />
```

The full version string tells any reader **when**, **why**, and **how many times** the entry asset has been refreshed — without needing to diff the file or check git history.

## When to Bump

Bump the version query **only** when a production deployment includes a meaningful change to a directly loaded CSS or JS entry asset.

### 1. Changed directly loaded entry asset

A CSS or JS file that is loaded directly by an HTML `<link>` or `<script>` tag has been modified. The version string on *that* asset's URL must be bumped.

```html
<!-- Before -->
<link rel="stylesheet" href="/panels-base.css?v=20260513-183-1" />

<!-- After (panel-base.css was modified) -->
<link rel="stylesheet" href="/panels-base.css?v=20260513-183-1" />
<!-- Wait — content changed, so bump: -->
<link rel="stylesheet" href="/panels-base.css?v=20260517-189-1" />
```

### 2. Changed child/imported asset requires parent entry bump

If a CSS `@import` chain or JS module dependency is modified, the **top-level entry asset** that loads it must be bumped — not the child asset (which is never loaded directly by the HTML).

```
Scenario:
  index.html loads <link href="/panels-base.css">
  panels-base.css @imports "/css/components/v1-base.css"

Action: v1-base.css is changed.
Effect: panels-base.css must be bumped because the browser only caches
        panels-base.css. The @imported child has no separate URL to cache-bust.
```

**Rule of thumb:** The version query lives on the URL the browser fetches. If a child changes, bump the parent that references it.

## What NOT to Do

| Practice | Why Not |
|----------|---------|
| **Repo-wide query rewrite** | Do not write a script or tool that rewrites every `?v=` in every HTML file. Each bump is intentionally localized to the affected entry asset only. |
| **Simple numeric `v=1`** | `v=1` conveys no information about when, why, or how many times an asset was updated. Repeated collisions (`v=1` reused across unrelated changes) defeat cache busting entirely. |
| **Unrelated asset bump** | Only bump the asset(s) whose content actually changed. Bumping a CSS file when the deployed JS changed is noise — it invalidates a cache unnecessarily and makes diffs harder to review. |
| **Automatic timestamp injection** | Do not add server-side `?t=${Date.now()}` or build-time timestamp injection. This defeats long-term caching entirely and forces every client to re-download every asset on every page load. |
| **Cache-Control / `_headers` / service worker changes in this issue** | HTTP caching headers, Cloudflare Pages `_headers` files, and service worker cache strategies are out of scope for this policy document and will be addressed separately if needed. |

## Rationale

### Smaller diffs

A manual version bump produces a single-line diff (`?v=...` → `?v=...`) in the HTML file that owns the reference. No generated files, no lockfiles, no CI config changes.

### Easier regression tracking

Because the version string encodes the issue number (`ISSUE`) and date (`YYYYMMDD`), anyone inspecting a deployed page can immediately cross-reference which deployment introduced which asset version. This is especially valuable when a regression appears in production and the question is "which version of the CSS was active when that happened?"

### Static Pages-style deployment needs explicit versions

0-a-control is deployed on Cloudflare Pages (or similar static hosts) that serve files directly from a Git-based origin without a build step. There is no template engine, no asset pipeline, and no server-side variable injection to stamp URLs automatically. Manual version queries are the simplest approach that works with zero infrastructure changes.

## PR Review Checklist

When reviewing a PR that bumps static asset version queries, verify:

- [ ] Only entry assets (loaded directly by HTML `<link>` / `<script>`) are bumped.
- [ ] Each bumped asset corresponds to an actual content change in that PR.
- [ ] Version format matches `v=YYYYMMDD-ISSUE-REV` exactly.
- [ ] No orphan `?v=` strings remain on unchanged assets.
- [ ] No Cache-Control, `_headers`, or service worker files are modified unless explicitly authorized by a separate issue.
- [ ] No unrelated assets (e.g., CSS in a JS-only PR) are bumped.
- [ ] The `ISSUE` portion of the version string matches the PR or the issue motivating the bump.
- [ ] `REV` starts at 1 and increments only when the same asset has already been bumped in a prior PR for the same issue.
- [ ] The change is in a dedicated branch, not on `main`.
