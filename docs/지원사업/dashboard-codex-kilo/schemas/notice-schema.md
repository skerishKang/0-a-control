# Notice Schema

## notice

- `id`: 내부 ID
- `source_site`: 예: `bizinfo`
- `source_url`: 사용자가 넣은 URL
- `source_notice_id`: 사이트 내부 공고 ID. 예: `PBLN_...`
- `title`: 공고명
- `category`: 사이트 분류값
- `posted_at`: 등록일
- `apply_start`: 접수 시작일
- `apply_end`: 접수 종료일
- `ministry`: 소관부처·지자체
- `agency`: 사업수행기관
- `apply_method`: 신청 방식
- `apply_site_url`: 접수처 URL
- `source_origin_url`: 출처 바로가기 URL
- `contact`: 문의처
- `summary_html`: 사업개요 원문 HTML
- `summary_text`: 정리된 텍스트
- `status`: `new`, `reviewing`, `writing`, `submitted`, `pass`
- `storage_path`: 공고 폴더 상대경로
- `created_at`
- `updated_at`

## attachment

- `id`
- `notice_id`
- `section_name`: `첨부파일`, `본문출력파일`
- `name`
- `view_url`
- `download_url`
- `local_path`
- `downloaded`: boolean
- `sort_order`

## company_fit

이 테이블은 나중 단계에서 사용한다.

- `id`
- `notice_id`
- `company_id`
- `fit_score`
- `fit_reason`
- `risk_notes`
- `model_name`
- `created_at`
