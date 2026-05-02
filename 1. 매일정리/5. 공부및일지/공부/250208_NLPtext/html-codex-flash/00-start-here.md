# Start Here

Project: study-oriented annotated Korean edition workflow for `2. Regular Expressions, Text Normalization, Edit Distance.pdf`

This is the single entry document for external/free models.
If you are given only one file to start from, start from this file.

## 1. Execution Environment
- You are assumed to be a Windows-running external/free model.
- Use Windows paths by default.
- Do not assume WSL paths unless explicitly provided.

## 2. Project Goal
This workflow is not trying to reproduce the original PDF layout exactly.
The goal is:
- accurate source content extraction
- faithful Korean translation
- useful study notes for self-study
- later HTML reconstruction with collapsible annotations

Content accuracy is more important than visual fidelity.

## 3. Required Read Order
Read these files in this exact order before doing any work:
1. `01-production-rules.md`
2. the task file explicitly assigned for this step

Do not skip the baseline file.

## 4. Baseline Document
- `01-production-rules.md`
  - content-first production rules
  - translation and note-writing rules
  - QA rules

## 5. Current Task Routing
Use the file assigned for the current step.

Available task files:
- `02-extract-translate-annotate-prompt.md`
  - source extraction + Korean translation + study note draft

Future task files may include:
- translation revision prompt
- note enrichment prompt
- HTML assembly prompt
- QA prompt

## 6. Working Rule
- Do not invent unseen content.
- Do not skip source content.
- Do not change the requested output format.
- Stay inside the requested page scope.
- Keep regex, code, formulas, tables, captions, references, and margin notes separate from ordinary prose.
- Mark unclear source text explicitly.
- Prefer accuracy over speed.

## 7. Current First Task
For the current workflow, the next active task file is:
- `02-extract-translate-annotate-prompt.md`

Unless the user explicitly redirects the workflow, start from that task file after reading `01-production-rules.md`.
