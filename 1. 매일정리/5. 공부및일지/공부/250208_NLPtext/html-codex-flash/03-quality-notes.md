# Quality Notes

Use these notes when reviewing early outputs from the free model.

## Accepted Direction
- `source_text / korean_translation / study_note` is the correct block structure for this workflow.
- Study notes should help learning, not reproduce layout.
- Content accuracy is more important than visual fidelity.

## Early Corrections To Apply
- Keep references in source form.
  - Example: `Weizenbaum (1966)` should remain as-is.
- Avoid small mistranslations caused by rushed OCR interpretation.
  - Example: `single character` should not become `마침표 하나`.
- Prefer consistent technical term handling.
  - `corpus` -> `말뭉치(corpus)` on first mention, then use a consistent shorter form
- Study notes should explain, not merely paraphrase.

## Review Checklist
- Is any source content missing?
- Is any content duplicated?
- Are regex strings preserved exactly?
- Are tables still readable row by row?
- Are references preserved?
- Is the Korean translation faithful?
- Does the study note add value without overreaching?
