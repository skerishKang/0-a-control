# Scripts Plan

예정 스크립트:

- `collect_notice.py`
  - URL 입력
  - 어댑터 선택
  - 메타 추출
  - 공고 폴더 생성
  - DB 저장

- `download_attachments.py`
  - 첨부파일 선택 다운로드

- `render_dashboard.py`
  - DB와 공고 폴더를 읽어 HTML 출력

- `adapter_bizinfo.py`
  - Bizinfo 상세 페이지 파서

## 1차 구현 우선순위

1. `adapter_bizinfo.py`
2. `collect_notice.py`
3. `render_dashboard.py`
