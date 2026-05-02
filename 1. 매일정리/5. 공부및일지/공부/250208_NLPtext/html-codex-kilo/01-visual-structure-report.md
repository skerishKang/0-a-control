# Visual Structure Report
Source PDF: `2. Regular Expressions, Text Normalization, Edit Distance.pdf`
Status: accepted as working visual-structure baseline
Purpose: layout and reconstruction reference only, not source-of-truth for full text transcription

## 1. Document Overview
- Total pages: 29
- Overall flow:
  - Chapter opener
  - 2.1 Regular Expressions
  - 2.2 Words
  - 2.3 Corpora
  - 2.4 Text Normalization
  - 2.5 Minimum Edit Distance
  - 2.6 Summary
  - Bibliographical and Historical Notes
  - Exercises
- This report is used as the working baseline for page structure, section flow, visual block types, and reconstruction planning.

## 2. Visual Style Summary
- Chapter opener uses a distinct layout from body pages.
- Section and subsection headings are visually prominent and color-coded.
- Body text is single-column textbook style.
- Margin keywords/callouts appear in outer margin areas.
- Tables are frequent and visually styled, often with captioning tied to figure numbering.
- Code, regex examples, and algorithms are visually separated from body paragraphs.
- Mathematical formulas and matrix/alignment diagrams appear in the edit-distance section.
- Bibliographical notes and exercises are separate end sections with different density and structure.

## 3. Page-Level Structural Notes
- Pages 1-2:
  - Chapter opener, dialogue/example, introduction, transition into 2.1
- Pages 3-10:
  - Regular expressions section
  - Many tables, operator examples, regex examples, ELIZA-related examples
- Pages 11-13:
  - Words and corpora
  - Vocabulary/statistics concepts and corpus discussion
- Pages 14-21:
  - Text normalization
  - Unix tools, tokenization, multilingual examples, BPE, stemming, sentence segmentation
- Pages 22-25:
  - Minimum edit distance
  - Alignment diagrams, formulas, recurrence, pseudocode, matrix examples
- Pages 26-29:
  - Summary
  - Bibliographical and Historical Notes
  - Exercises
  - References-like end matter

## 4. Reconstruction Risk Areas
- Margin notes may expand awkwardly in Korean if treated literally.
- Tables are numerous and will need row-height and caption handling.
- Regex/code/formula blocks must not be merged into normal prose.
- Diagram-internal text may need separate treatment from main body translation.
- Chapter opener needs its own template.
- End matter may require different layout handling from the main text.

## 5. Recommended Work Segments
- Segment A: pages 1-2
- Segment B: pages 3-10
- Segment C: pages 11-13
- Segment D: pages 14-21
- Segment E: pages 22-25
- Segment F: pages 26-29

## 6. Scope Rule
This file is a visual-structure baseline.
It should be used for:
- work segmentation
- reconstruction planning
- layout QA
- block classification guidance

It should not be used as:
- final source text
- final translation source
- exact OCR authority
