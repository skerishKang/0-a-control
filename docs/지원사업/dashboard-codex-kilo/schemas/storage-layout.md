# Storage Layout

공고별 자료는 `data/notices/YYYY/MM/<slug>/` 아래에 저장한다.

예시:

```text
data/notices/2026/04/2026-xaas-선도-프로젝트/
  meta.json
  source.html
  normalized.md
  attachments/
```

## 파일 설명

- `meta.json`: 정규화된 공고 메타데이터 스냅샷
- `source.html`: 원문 HTML 저장본
- `normalized.md`: 사람이 빠르게 읽기 위한 정리본
- `attachments/`: 다운로드한 첨부파일

## 원칙

- DB가 조회의 기준이다.
- 폴더는 원문 보관과 재가공 산출물의 기준이다.
- 둘 다 유지하되 역할을 분리한다.
