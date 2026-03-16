# 12. Telegram / External Input 저장 구조 설계

## 1. 목적

이 문서는 Telegram 메시지와 첨부파일을 `0-a-control` 안에서 어떻게 저장하고 확장할지 정리한다.

전제는 다음과 같다.

- 목표는 “메시지 앱 재구현”이 아니라, AI가 나중에 바로 참조할 수 있는 외부 자료 저장소를 만드는 것이다.
- 채팅창별로 DB를 여러 개 두지 않고, 하나의 SQLite DB 안에서 `source_id`, `chat_class`, `source_type`으로 구분한다.
- 현재의 `external_inbox` 흐름을 부정하지 않고, 다음 단계 확장을 준비한다.
- 이번 단계는 설계와 최소 준비가 중심이며, 대규모 마이그레이션은 하지 않는다.

## 2. 설계 결론

### 2-1. 지금 당장은 `external_inbox` 확장 방향을 유지한다

현 시점에서는 `telegram_messages` 같은 별도 메시지 테이블을 새로 만드는 것보다, `external_inbox`를 “외부 자료의 공통 메시지/아이템 레코드”로 유지하는 편이 맞다.

이유:

- 이미 UI, CLI, 상태 조회가 `external_inbox`를 기준으로 동작한다.
- Telegram 외에 email, 링크, 파일 입력도 같은 저장소 개념으로 다룰 수 있다.
- source별 분리는 `source_id`, `source_name`, `chat_class`, `source_type`로 충분히 표현 가능하다.
- 지금은 첨부파일 포함 고급 메시징 기능보다 “AI 참조 가능한 저장소”가 우선이다.

### 2-2. 다만 첨부파일은 장기적으로 child table 분리가 낫다

메시지 하나에 첨부가 여러 개 붙을 수 있으므로, 장기적으로는 다음 2계층이 가장 안정적이다.

1. `external_inbox`: 메시지/아이템 단위의 대표 레코드
2. `external_attachments` 같은 child table: 첨부파일 단위 레코드

이번 단계에서는 아직 새 테이블을 만들지 않는다. 대신 문서로 방향을 고정하고, 당장 필요한 최소 정보는 기존 `attachment_path`, `attachment_ref`, `metadata_json`에 실을 수 있게 둔다.

## 3. 메시지 레코드 기준 모델

### 3-1. `external_inbox`에서 유지할 핵심 필드

현재 테이블을 기준으로 다음 의미를 고정한다.

| 필드 | 의미 | 비고 |
| --- | --- | --- |
| `source_type` | telegram, email 등 외부 소스 종류 | 현재 사용 중 |
| `source_id` | 채팅방/채널/계정 식별자 | 하나의 DB 안에서 분리 기준 |
| `source_name` | 표시용 이름 | 현재 사용 중 |
| `external_message_id` | 원본 메시지 ID | Telegram의 `message_id` 대응 |
| `author` | 보낸 사람 이름 | 현재 사용 중 |
| `item_timestamp` | 실제 메시지 발생 시각 | 시간축 기준 |
| `imported_at` | 시스템 적재 시각 | 운영 추적 기준 |
| `item_type` | text, image, video, audio, file, link 등 | 현재는 text 중심 |
| `raw_content` | 텍스트 본문 또는 추출 텍스트 | AI 1차 참조용 |
| `attachment_path` | 대표 첨부 1개 또는 대표 경로 | 현재 필드 유지 |
| `metadata_json` | Telegram 고유 부가 정보 | 확장 완충지대 |

### 3-2. Telegram 전용 의미 매핑

Telegram 수집 시 아래처럼 매핑한다.

| Telegram 개념 | 저장 위치 |
| --- | --- |
| `chat_id` | `source_id` |
| chat title | `source_name` |
| chat class | `telegram_sources.chat_class`와 조합 |
| `message_id` | `external_message_id` |
| `reply_to_message_id` | 우선 `metadata_json.reply_to_message_id` |
| sender / author | `author` |
| message date | `item_timestamp` |
| sync/import time | `imported_at` |
| text / caption | `raw_content` |
| attachment summary | `attachment_path`, `attachment_ref`, `metadata_json.attachments` |

## 4. 다음 단계의 최소 확장안

### 4-1. 지금 스키마를 크게 깨지 않으면서 먼저 늘릴 수 있는 필드

다음 마이그레이션 후보는 작게 가져간다.

```sql
ALTER TABLE external_inbox ADD COLUMN mime_type TEXT;
ALTER TABLE external_inbox ADD COLUMN file_name TEXT;
ALTER TABLE external_inbox ADD COLUMN file_size INTEGER;
ALTER TABLE external_inbox ADD COLUMN reply_to_external_message_id TEXT;
```

의도:

- 대표 첨부 1개 기준의 빠른 조회를 지원
- reply chain 참조를 메시지 레코드 수준에서 최소 지원
- 여러 첨부/고급 메타는 계속 `metadata_json`으로 완충

### 4-2. 첨부가 본격화되면 child table로 간다

여러 첨부를 제대로 다룰 단계에서는 별도 테이블이 적합하다.

초안:

```sql
CREATE TABLE external_attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inbox_id INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    external_message_id TEXT NOT NULL,
    attachment_index INTEGER NOT NULL DEFAULT 0,
    attachment_kind TEXT NOT NULL,          -- image, audio, video, file
    attachment_path TEXT NOT NULL,
    mime_type TEXT,
    file_name TEXT,
    file_size INTEGER,
    checksum_sha256 TEXT,
    created_at TEXT NOT NULL,
    metadata_json TEXT,
    UNIQUE(inbox_id, attachment_index)
);
```

이 테이블은 “나중 단계”이고, 지금 바로 만들 필요는 없다.

## 5. 파일 저장 구조

첨부 원본 파일은 DB에 직접 넣지 않고 로컬 파일로 저장한다.

권장 경로:

```text
data/blobs/telegram/<source_id>/<yyyy-mm-dd>/<message_id>/
```

예시:

```text
data/blobs/telegram/123456789/2026-03-10/4412/
  photo_0.jpg
  voice_0.ogg
  metadata.json
```

원칙:

- DB에는 경로와 핵심 메타만 저장한다.
- 실제 원본은 `data/blobs/telegram/...`에 둔다.
- 메시지 하나에 여러 첨부가 있으면 하위 디렉토리 한 곳에 모은다.
- 향후 checksum을 두면 중복 파일 감지에 유리하다.

## 6. 초기 백필(import)과 일상 sync 분리

### 6-1. 초기 1회 백필(import)

역할:

- 과거 Telegram 대화를 한 번에 넣는 경로
- 사용자가 export 파일 또는 정리된 입력 디렉토리를 제공하는 방식
- 메시지 발생 시각은 반드시 원래 시각을 `item_timestamp`에 넣는다

특징:

- `last_message_id`를 신뢰하지 않아도 된다
- 과거 메시지가 나중에 들어와도 `item_timestamp` 기준으로 제 위치에 정렬된다
- 첨부 원본도 함께 복사하거나 참조 경로를 기록할 수 있다

권장 입력:

- Telegram export JSON
- command-center에서 뽑은 chat dump
- 이미 정리된 `messages/`, `media/` 디렉토리

### 6-2. 일상 sync

역할:

- 핵심4개 중심의 증분 적재
- 현재 `sync-core`가 맡고 있는 루프 유지

특징:

- `telegram_sources.last_message_id`
- `telegram_sources.last_synced_at`

이 두 필드로 운영 추적을 계속 한다.

즉:

- 백필은 “옛 데이터 채우기”
- sync는 “새 데이터 증분 반영”

이 둘을 같은 책임으로 섞지 않는다.

## 7. AI 참조 흐름

AI가 외부 연락을 참조할 때의 기본 흐름은 다음과 같다.

1. 먼저 `external_inbox`에서 메시지/아이템을 찾는다.
2. 텍스트가 충분하면 `raw_content`만으로 참조한다.
3. 추가 확인이 필요하면 `attachment_path` 또는 향후 `external_attachments` 경로를 따라 실제 파일을 읽는다.

중요:

- 자동으로 모든 첨부를 모델 입력에 넣는 구조를 목표로 하지 않는다.
- 우선 목표는 “AI가 필요할 때 찾아볼 수 있는 저장소”다.
- 따라서 DB는 검색/정렬/참조 포인터 역할을, 파일 시스템은 원본 보관 역할을 맡는다.

## 8. 지금 당장 구현하지 않는 것

- Telegram 전용 대형 별도 테이블 전체 도입
- 채팅창별 독립 DB
- 첨부파일 자동 다운로드 전체 파이프라인
- OCR, STT, 썸네일 생성
- 첨부 다중 인덱싱 테이블의 즉시 도입
- AI 자동 주입 파이프라인

## 9. 다음 구현 순서 제안

1. `external_inbox`에 필요한 최소 추가 컬럼 후보(`mime_type`, `file_name`, `file_size`, `reply_to_external_message_id`) 검토
2. 백필 전용 import 경로 초안 작성
3. `data/blobs/telegram/...` 저장 규칙과 디렉토리 생성 로직 추가
4. 첨부가 실제로 들어오기 시작하면 `external_attachments` 도입 여부 결정
5. UI에서는 “원래 시각”과 “적재 시각”을 분리해 보여줄지 후속 결정
