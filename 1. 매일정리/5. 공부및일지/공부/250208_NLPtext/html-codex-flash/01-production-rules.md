# Production Rules
Project: study-oriented annotated Korean edition of `2. Regular Expressions, Text Normalization, Edit Distance.pdf`

## 1. Purpose
This workflow is for building a content-accurate Korean study edition with annotations.
It is not a page-faithful PDF reconstruction workflow.

Primary output goals:
1. accurate source text
2. faithful Korean translation
3. short but useful study notes
4. block-structured content for later HTML rendering

## 2. Environment Rule
- Codex operates in WSL by default.
- External or free models operate in Windows by default unless explicitly stated otherwise.
- Prompts written for external/free models should use Windows paths by default.
- If both path styles are needed, show Windows path first and WSL path second.

## 3. Source Hierarchy
Use sources in this order:
1. source PDF
2. page images
3. structured extraction blocks
4. Korean translation blocks
5. study-note blocks
6. HTML assembly drafts

## 4. Block Rule
Work in logical blocks.
Preferred block types:
- chapter_title
- section_title
- subsection_title
- paragraph
- dialogue
- table
- figure_caption
- formula
- code
- margin_note
- reference
- other

## 5. Content Preservation Rule
The following must be preserved carefully:
- section numbering
- figure numbering
- code indentation
- regex syntax
- formula notation
- table row order
- reference spelling
- paragraph order

## 6. Translation Rule
- Translate faithfully.
- Do not summarize.
- Do not silently omit source content.
- If source text is unclear, mark it as `[unclear]`.
- Preserve technical meaning even if the Korean phrasing must be slightly adjusted for readability.
- Keep terminology consistent across pages.

## 7. Reference Rule
- References should normally remain in the original source form.
- Do not localize author names inside bibliographic references unless explicitly requested.
- Example:
  - keep `Weizenbaum (1966)`
  - do not rewrite it as a translated citation label

## 8. Study Note Rule
Study notes are not summaries of the whole page.
Each note should help the user study the block.

Each `study_note` should focus on one or more of:
- what this block means
- why it matters
- what is easy to misunderstand
- what prior knowledge helps

Study notes should:
- be short
- be useful
- avoid restating the block line by line
- avoid adding unsupported claims

## 9. Special Block Rule
- regex/code:
  preserve symbols, spacing, and line breaks as much as possible
- formula:
  preserve notation; explain meaning in Korean translation or note
- table:
  keep row order and separate caption if present
- margin_note:
  short translation allowed
- reference:
  source form preferred

## 10. QA Rule
Check at least the following:
- missing text
- duplicated text
- broken numbering
- code corruption
- regex corruption
- formula corruption
- mistranslated technical term
- note that drifts beyond the source

## 11. Output Rule
Default working format for each block:
- type
- source_text
- korean_translation
- study_note

Page-level format:
- `# Page N`
- `## Block N`
- `- type:`
- `- source_text:`
- `- korean_translation:`
- `- study_note:`

Formatting guidance:
- Keep one block per semantic unit.
- Keep page headers/footers as `other` only when they are actually visible.
- If a sentence clearly continues onto the next page, do not fabricate the ending.
- In that case, translate faithfully and mark continuation naturally, for example:
  - `[다음 페이지에서 계속]`
- References stay in source form unless explicitly requested otherwise.
- Book titles should be translated naturally when appropriate.
  - Example: `Speech and Language Processing` -> `음성 및 언어 처리`
- Avoid minor Korean wording mistakes caused by rushed OCR interpretation.
  - Example: `single character` should be `단일 문자` or `문자 하나`, not `마침표 하나`

## 12. Working Sequence
1. extract source text
2. translate faithfully into Korean
3. add study note
4. review for missing or duplicated content
5. store as structured blocks
6. later assemble into HTML
