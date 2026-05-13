# Static Asset Version Query Policy

## Reference

0-a-control adopts the **LoveBud/LoveTree manual static asset version query pattern** as the basis for this policy. That project's convention has proven effective for a static-deployment environment without a build pipeline, and this document codifies the same approach for 0-a-control.

## Format

```text
v=YYYYMMDD-ISSUE-REV
```

| Part       | Meaning                                                   |
|------------|-----------------------------------------------------------|
| `YYYYMMDD` | Date the change was made.                                 |
| `ISSUE`    | GitHub issue number that motivated the version bump.      |
| `REV`      | Sequential revision counter starting at 1 for that issue. |

### Example

```html
<link rel="stylesheet" href="/css/components/v1-base.css?v=20260513-183-1" />
```

The full version string tells any reader **when**, **why**, and **how many times** the entry asset has been refreshed without needing to diff the file or check git history.

## When to Bump

Bump the version query **only** when a production deployment includes a meaningful change to a directly loaded CSS or JS entry asset, or to a child asset that is reached through such an entry asset.

### 1. Changed directly loaded entry asset

A CSS or JS file that is loaded directly by an HTML `<link>` or `<script>` tag has been modified. The version string on *that* asset's URL must be bumped.

```html
<!-- Before -->
<link rel="stylesheet" href="/panels-base.css?v=20260513-183-1" />

<!-- After: panels-base.css was modified for issue 189 -->
<link rel="stylesheet" href="/panels-base.css?v=20260517-189-1" />
```

### 2. Changed child/imported asset requires parent entry bump

If a CSS `@import` chain or JS module dependency is modified, the **top-level entry asset** that loads it must be bumped. Do not add an unrelated query string to every child file.

```text
Scenario:
  index.html loads <link href="/panels-base.css">
  panels-base.css imports "/css/components/v1-base.css"

Action:
  v1-base.css is changed.

Effect:
  panels-base.css must be bumped because the HTML entry reference is the
  browser-visible cache-busting point for this dependency chain.
```

**Rule of thumb:** The version query belongs on the URL the HTML entry page loads directly. If a child changes, bump the parent entry reference that makes the changed child reachable.

## What NOT to Do

| Practice | Why Not |
|----------|---------|
| **Repo-wide query rewrite** | Do not write a script or tool that rewrites every `?v=` in every HTML file. Each bump is intentionally localized to the affected entry asset only. |
| **Simple numeric `v=1`** | `v=1` conveys no information about when, why, or how many times an asset was updated. Repeated collisions across unrelated changes defeat cache busting. |
| **Unrelated asset bump** | Only bump the asset references whose content path actually changed. Bumping a CSS file when the deployed JS changed is noise and makes diffs harder to review. |
| **Automatic timestamp injection** | Do not add server-side runtime timestamps or build-time timestamp injection. This defeats long-term caching and forces clients to re-download assets unnecessarily. |
| **Cache-Control / `_headers` / service worker changes in this issue** | HTTP caching headers, Cloudflare Pages `_headers` files, and service worker cache strategies are out of scope for this policy document and must be addressed separately if needed. |

## Rationale

### Smaller diffs

A manual version bump produces a single-line diff in the HTML file that owns the reference. No generated files, no lockfiles, no CI config changes.

### Easier regression tracking

Because the version string encodes the issue number and date, anyone inspecting a deployed page can cross-reference which deployment introduced which asset version. This is useful when a regression appears and the first question is which CSS or JS version was active.

### Static Pages-style deployment needs explicit versions

0-a-control is intended to remain compatible with static hosting that serves files directly from a Git-based origin without a build step. There is no template engine, no asset pipeline, and no server-side variable injection to stamp URLs automatically. Manual version queries are the simplest approach that works with zero infrastructure changes.

## PR Review Checklist

When reviewing a PR that bumps static asset version queries, verify:

- [ ] Only entry assets loaded directly by HTML `<link>` or `<script>` tags are bumped.
- [ ] Each bumped asset reference corresponds to an actual content change in that PR or a changed imported child asset.
- [ ] Version format matches `v=YYYYMMDD-ISSUE-REV` exactly.
- [ ] No orphan `?v=` strings remain on unchanged or unrelated assets.
- [ ] No Cache-Control, `_headers`, or service worker files are modified unless explicitly authorized by a separate issue.
- [ ] No unrelated assets are bumped.
- [ ] The `ISSUE` portion of the version string matches the issue motivating the bump.
- [ ] `REV` starts at 1 and increments only when the same asset has already been bumped in a prior PR for the same issue.
- [ ] The change is in a dedicated branch, not on `main`.
- [ ] Runtime, generated, private, log, and session files are not touched by policy-only PRs.
