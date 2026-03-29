# Study Assistant Protocol (3-Part Architecture)

When the user provides a transcript or course materials, follow this 3-part structure to generate the Study Guide:

## 1. [ORIGINAL] 원문 및 번역 (Original & Translation)
- **English**: 사용자가 제공한 영문 전문을 그대로 보관합니다.
- **Korean Translation**: 영문 전문을 의미 단위로 끊어 자연스러운 한국어로 번역하여 병기합니다. 
- HTML 템플릿 하단의 `Original Transcript` 섹션에 두 언어를 나란히 혹은 위아래로 배치합니다.

## 2. [CORE] 핵심 및 학습 포인트 (Study Core)
- **Primary Lesson**: 이번 섹션의 핵심 주제 1가지.
- **Key Concepts**: 주요 용어 3~5개 추출 및 설명.
- **Recall Quiz**: 학습 내용을 복습할 수 있는 퀴즈 2~3개.

## 3. [SUMMARY] 요약 및 구조화 (Summary & Structure)
- 전체 강의 내용을 논리적 흐름에 따라 3~5분량의 불렛 포인트로 요약합니다.

---

**Trigger:** "이 대본 정리해줘" (Summarize this transcript)
**Output:** 한 페이지 내에서 상단(Summary) -> 중단(Study Core) -> 하단(Original/Translation) 순서로 배치된 HTML 코드.
