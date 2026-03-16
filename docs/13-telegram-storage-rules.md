# 13. Telegram 저장 규칙

## 목적

이 문서는 `0-a-control`에서 Telegram 메시지와 첨부파일을 어떻게 저장하는지에 대한 운영 규칙을 고정한다.

목표는 Telegram을 다시 구현하는 것이 아니라:

- 대화 원문을 시간축대로 보존하고
- 첨부 원본을 로컬에 보관하고
- AI가 나중에 DB와 파일 경로를 바로 참조할 수 있게 만드는 것이다.

## 기준 저장소

Telegram 메시지의 canonical 저장소는 현재 `external_inbox`다.

- 하나의 DB만 사용한다.
- 채팅방별 DB를 따로 만들지 않는다.
- 구분은 `source_type`, `source_id`, `source_name`, `chat_class`로 한다.

핵심 시간 필드 의미:

- `item_timestamp`
  - 원래 메시지가 발생한 시각
  - 조회, 정렬, 시간순 재구성의 기준
- `imported_at`
  - 이 DB에 적재된 시각
  - 운영 추적과 동기화 상태의 기준

## 첨부파일 저장 원칙

첨부 원본은 DB에 직접 넣지 않고 파일로 저장한다.

- DB는 경로와 메타데이터를 가진다.
- 파일시스템은 원본 보관소 역할을 맡는다.

현재 기준 경로:

```text
data/blobs/telegram/<chat_name>/<yyyy-mm-dd>/<chat_name>_<yyyy-mm-dd>_<message_id>_<original_name>
```

예시:

```text
data/blobs/telegram/강혜림/2026-03-09/강혜림_2026-03-09_45248_invoice.pdf
data/blobs/telegram/로컬봇/2026-03-09/로컬봇_2026-03-09_8124_chart.png
```

규칙:

1. 폴더는 `채팅방 이름 / 날짜` 단위로 나눈다.
2. 파일명에는 아래 요소를 넣는다.
   - 채팅방 이름
   - 날짜
   - Telegram `message_id`
   - 원본 파일명
3. 원본 파일명이 없으면 `<message_id>_<kind>` 기반 이름을 쓴다.
4. 파일명에 쓸 수 없는 문자는 `_`로 정리한다.

이 규칙의 이유:

- 사람이 폴더만 봐도 어디서 온 파일인지 바로 알 수 있다.
- 같은 이름의 파일이 많아도 `message_id`로 충돌을 줄일 수 있다.
- AI가 `attachment_path`만 받아도 출처를 유추하기 쉽다.

## DB에 저장할 첨부 정보

현재 `external_inbox`에서 유지하는 기준:

- `attachment_path`
  - 로컬 원본 파일 경로
- `attachment_ref`
  - 원본 파일명 또는 외부 참조 이름
- `item_type`
  - `text`, `image`, `audio`, `video`, `file`
- `metadata_json`
  - `mime_type`, `file_size`, `attachment_name` 등의 확장 메타데이터

즉:

- 첨부 원본은 파일로 저장
- DB에는 찾기 위한 경로와 메타데이터만 저장

## 자동 동기화와 백필 구분

### 자동 동기화

자동 동기화는 핵심4개 채팅의 최근 새 메시지를 증분 적재하는 경로다.

- 기준: `telegram_sources.last_message_id`
- 목적: 최근 메시지 누적
- 빈도: 하루 5회 등 운영 스케줄에 맞춤

### 백필(import)

백필은 예전 대화를 나중에 한 번에 가져오는 경로다.

- 과거 대화 export
- 수동 import
- AI나 별도 스크립트 기반 정리

백필은 나중에 적재해도 `item_timestamp` 기준으로 원래 시간축에 들어가야 한다.

## AI 참조 원칙

AI는 Telegram 앱을 직접 읽는 것이 아니라, 다음 순서로 참조한다.

1. `external_inbox`에서 메시지와 메타데이터를 찾는다.
2. 텍스트는 `raw_content`를 읽는다.
3. 첨부가 필요하면 `attachment_path`를 따라 실제 파일을 연다.

즉 이 저장 구조의 목적은:

- 메시지를 미리 저장해두고
- 필요할 때 AI가 빠르게 찾게 하는 것

## 구현 메모

현재 기준 파일:

- `scripts/telegram_service.py`
- `scripts/telegram_cli.py`
- `scripts/telegram_db.py`

관련 설계 배경 문서:

- `docs/12-telegram-external-storage-design.md`

이 문서는 설계 배경보다 더 직접적인 운영 규칙 문서다.
