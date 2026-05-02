# Start Here

Project: Korean reconstruction workflow for `2. Regular Expressions, Text Normalization, Edit Distance.pdf`

This is the single entry document for external/free models.
If you are given only one file to start from, start from this file.

## 1. Execution Environment
- You are assumed to be a Windows-running external/free model.
- Use Windows paths by default.
- Do not assume WSL paths unless explicitly provided.

## 2. Required Read Order
Read these files in this exact order before doing any work:
1. `02-production-rules.md`
2. `01-visual-structure-report.md`
3. the task file explicitly assigned for this step

Do not skip the baseline files.

## 3. Baseline Documents
- `02-production-rules.md`
  - global production rules
  - source hierarchy
  - preservation rules
  - translation and QA rules
- `01-visual-structure-report.md`
  - accepted visual-structure baseline
  - page segmentation guidance
  - reconstruction risk areas

## 4. Current Task Routing
Use the file assigned for the current step.

Available task files:
- `03-extraction-task-prompt.md`
  - source text extraction by block

Future task files may include:
- translation prompt
- QA prompt
- glossary prompt

## 5. Working Rule
- Do not invent unseen content.
- Do not skip required baseline documents.
- Do not change the requested output format.
- Stay inside the requested page/section/block scope.
- Keep code, regex, formulas, tables, captions, and bibliography separated from normal prose.
- Mark unclear text explicitly.

## 6. Standard Invocation Pattern
If the user gives you only this file, do the following:
1. Read `02-production-rules.md`
2. Read `01-visual-structure-report.md`
3. Read the assigned task file
4. Execute only that task
5. Return output in the requested format

## 7. Current First Task
For the current workflow, the next active task file is:
- `03-extraction-task-prompt.md`

Unless the user explicitly redirects the workflow, start from that task file after reading the two baseline documents.
