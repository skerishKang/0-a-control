# Public repository boundary audit

This repository is a local-first personal control tower. It can contain operational context, local workflow configuration, imported message metadata, session summaries, and generated artifacts. The repository is public, so the safe boundary must be explicit.

## Current recommendation

Default recommendation: keep this repository code-focused and local-only.

The repository may remain public only if runtime data, local paths, secrets, generated sessions, personal archives, and imported conversation content stay out of Git. If those boundaries cannot be maintained, the safer operating choice is to make the repository private.

## Sensitive content categories

| Category | Risk | Current boundary |
| --- | --- | --- |
| Runtime database and state | May contain personal work context, Telegram-derived data, sessions, and local decisions | Keep under `data/runtime/` or configured runtime paths; do not commit |
| Session exports and generated logs | May reveal full agent/user work history | Keep local-only; `sessions/` is ignored |
| Local machine paths | Can reveal usernames, project locations, drive layout, or client context | Use placeholders in docs and examples |
| Telegram configuration and session files | Can provide access or reveal private chats/metadata | Keep session files and API credentials outside Git |
| Work diary or personal archive folders | Can contain private personal/professional notes | Keep outside this public repo unless deliberately redacted |
| Queue, verdict, and generated report artifacts | Can include agent outputs and operational decisions | Keep runtime queues local-only unless sanitized examples are needed |
| Historical commits | May contain already-removed sensitive content | Audit separately before assuming the public repo is clean |

## Must remain local-only

The following should not be tracked in this public repository:

- `data/config/tracked_projects.json`
- `data/runtime/`
- `data/blobs/`
- `sessions/`
- `sessions_html/`
- `session_exports/`
- Telegram session files
- `.env` or any file containing API credentials
- personal folders such as `대화/`, `1. 매일정리/`, or similar archive/work diary folders

## Acceptable public content

The following can remain public when reviewed:

- application source code
- tests
- sanitized documentation
- example configuration files with placeholders
- small synthetic fixtures that do not contain real personal data

## Existing guardrails

The repository currently has guardrails that reduce accidental exposure:

- `.gitignore` excludes local runtime artifacts and generated session exports.
- `scripts/check_repo_hygiene.py` scans tracked files for local-only paths and runtime artifacts.
- CI runs repository hygiene checks before tests.
- Runtime config uses example files and placeholders for local paths.

These guardrails reduce risk but do not replace periodic human review.

## Public/private decision rule

Use this rule:

- Keep public only if the repo contains code, tests, and sanitized docs.
- Make private if real user conversations, work diary records, client/project details, runtime DBs, or imported external messages need to live with the repo.
- Never rely on `.gitignore` alone for content that has already been committed; historical exposure requires separate review.

## Follow-up checklist

Before major releases or wider sharing:

- [ ] Run `python scripts/check_repo_hygiene.py`.
- [ ] Review `git ls-files` for generated folders or personal archives.
- [ ] Check docs for local absolute paths and private names.
- [ ] Confirm runtime data is outside Git.
- [ ] Decide whether a private archive repository is needed for personal/session material.
- [ ] If sensitive content was historically committed, decide whether history rewrite or repository privacy is required.
