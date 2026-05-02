# html-codex-flash

이 폴더는 교재 PDF를 다음 순서로 가공하는 작업 루트입니다.

1. 이미지 분할본 준비
2. 페이지별 `md` 원고 생성
3. 검수 및 교정
4. PDF별 `merged` 합본 생성
5. PDF별 `html` 생성

## 핵심 안내 문서

- `00-start-here.md`
  - 전체 작업 시작점
- `01-production-rules.md`
  - 출력 형식과 제작 규칙
- `02-extract-translate-annotate-prompt.md`
  - 페이지 추출/번역/주석 기본 프롬프트
- `03-quality-notes.md`
  - 품질 점검 기준
- `04-format-sample-page-01-02.md`
  - 결과 포맷 샘플
- `05-revision-prompt.md`
  - 교정용 프롬프트
- `06-working-status.md`
  - 현재 진행 상태 기록

이 7개 파일은 이후 다른 PDF 작업에도 계속 재사용하는 공통 규칙 문서입니다.

## 폴더 구조

각 PDF는 별도 작업 폴더를 가집니다.

- `02-regular-expressions-text-normalization-edit-distance/`
- `03-n-gram-language-models/`
- `04-naive-bayes-and-sentiment/`

각 PDF 폴더 내부 구조:

- `pages/`
  - 2페이지 단위 `md` 원고
  - 예: `01-pages-01-02.md`
- `merged/`
  - 전체 합본
- `html/`
  - 개별 읽기용 HTML
  - 최종적으로 `index.html` 포함 가능

## 권장 운영 순서

### 1. 새 PDF 시작

1. `jpg분할/` 아래에 페이지 이미지 준비
2. `html-codex-flash/XX-pdf-name/` 폴더 생성
3. 내부에 `pages/`, `merged/`, `html/` 생성

### 2. MD 작성

페이지 묶음 단위로 저장:

- `01-pages-01-02.md`
- `02-pages-03-04.md`
- `03-pages-05-06.md`

형식:

- `source_text`
- `korean_translation`
- `study_note`

### 3. 검수

`saved: ...md`가 오면 다음을 점검:

- 페이지/블록 누락 여부
- 한국어 비문
- 페이지 넘김 처리
- block 번호 흐름

### 4. HTML 변환

`pages/*.md`를 같은 번호의 `html/*.html`로 변환:

- `01-pages-01-02.md` -> `01-pages-01-02.html`

권장 방식:

- 첫 HTML을 템플릿으로 사용
- 이후 동일한 구조로 반복 생성

### 5. 목차 생성

개별 HTML이 다 만들어지면:

- `html/index.html`

을 만들어 전체 파일을 링크합니다.

## 메모

- `pages`가 원본 작업물입니다.
- `html`은 읽는 뷰입니다.
- `merged`는 전체 원고를 합친 중간 산출물입니다.
- 먼저 `md`를 확정하고, 그 다음 `html`로 가는 흐름을 기본으로 합니다.
