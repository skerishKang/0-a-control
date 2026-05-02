# Production Rules
Project: Korean reconstruction of `2. Regular Expressions, Text Normalization, Edit Distance.pdf`

## 1. Purpose
This document defines the working rules for extracting, translating, and reconstructing the chapter into a Korean textbook-style version while preserving the source structure as closely as practical.

## 2. Environment Rule
- Codex operates in WSL by default.
- External or free models operate in Windows by default unless explicitly stated otherwise.
- Prompts written for external/free models should use Windows paths by default.
- If both path styles are needed, show Windows path first and WSL path second.

## 3. Source Hierarchy
Use sources in this order:
1. Source PDF
2. Page images
3. Structured extraction files
4. Translation drafts
5. Reconstruction drafts

The visual structure report is a layout baseline, not full text authority.

## 4. Translation Unit Rule
Work in logical blocks, not raw pages only.
Preferred units:
- heading block
- paragraph block
- bullet block
- table block
- figure caption block
- figure text block
- code block
- formula block
- exercise block
- bibliography block

## 5. Preservation Rule
The following must be preserved carefully:
- section numbering
- figure numbering
- table/caption linkage
- code indentation
- regex syntax
- formula notation
- bibliography formatting where practical
- exercise numbering and order

## 6. Do Not Merge Rule
Do not merge the following into ordinary prose:
- regex
- code
- formulas
- tables
- figure captions
- margin keywords
- bibliography entries
- exercises

## 7. Translation Rule
- Translate prose faithfully.
- Do not summarize.
- Do not silently omit text.
- Mark unclear source text explicitly.
- Keep technical terms consistent.
- Decide term translations through glossary control, not ad hoc rewriting.

## 8. Diagram Rule
For diagrams and matrix/alignment visuals:
- separate diagram-internal text from body text
- decide case by case whether to keep English labels or replace them
- if replacement is risky, preserve original labels and translate in caption/body note

## 9. Template Rule
The following should be treated as distinct layout templates:
- chapter opener
- standard body page
- table-heavy page
- code/algorithm-heavy page
- formula/diagram-heavy page
- end matter page

## 10. QA Rule
Check at least the following at each stage:
- missing text
- wrong block classification
- broken numbering
- code corruption
- regex corruption
- formula corruption
- caption mismatch
- section heading mismatch
- page-to-page structural drift

## 11. Working Sequence
1. Visual structure baseline confirmed
2. Source text extracted by block
3. Extraction reviewed
4. Translation drafted by block
5. Translation reviewed with glossary
6. Reconstruction drafted
7. Layout QA against visual structure baseline
8. Final Korean textbook PDF assembled
