# sessions/ - Session Archive

## Purpose

이 폴더는 세션의 **전체 보존본**을 저장합니다.

- 요약 메모가 아닙니다
- 세션의 전체 대화 흐름과 transcript가 포함됩니다
- 나중에 다시 읽어서 작업을 이어갈 수 있는 완전한 기록입니다

## 구조 (4층)

| 층 | 역할 | 위치 |
|---|------|------|
| **원문층** | DB source_records / transcript raw content | `data/control_tower.db` |
| **보존층** | 사람이 읽을 수 있게 정돈한 전체 세션 | `sessions/` (이 폴더) |
| **표시층** | 브라우저에서 읽기 좋은 HTML 렌더 | `sessions_html/` |
| **요약층** | Intent / Actions / Decisions 등 압축 정보 | 각 파일 상단 Summary 블록 |

### 중요: 요약층은 보조입니다

- Summary는 파일 상단에 짧은 박스로만 존재합니다
- 본문 전체를 Summary로 대체하지 않습니다
- 요약이 틀릴 수 있으므로 원문(본문)으로 언제든 돌아갈 수 있어야 합니다

## 파일 형식

각 세션 파일은 다음을 포함합니다:

```
# 제목

## Metadata          ← 세션 기본 정보
## Summary           ← 짧은 요약 (보조)
## Dialogue          ← 전체 대화 흐름 (USER / ASSISTANT / TOOL)
## Transcript        ← 원시 세션 기록 (cleaned + raw)
```

## 디렉토리 구조

```
sessions/
├── README.md             ← 이 파일
├── INDEX.md              ← 세션 목록
├── TEMPLATE.md           ← 세션 노트 템플릿
└── YYYY-MM-DD/
    └── YYYY-MM-DD_HHMM_<short-id>.md  ← 개별 세션 파일
```

## Recovery 시 읽기 순서

세션 복원 시 다음 순서로 읽습니다:

1. **current urgent state** 확인 (현재 상태 API)
2. **관련 sessions archive** 확인 (이 폴더의 .md 파일)
3. **sessions_html**로 빠른 탐색 (브라우저에서 검색)
4. **raw transcript / DB source_records** 확인 (부족할 때)
5. **summary/current quest**로 압축 (마지막 정리)

## Dialogue 섹션

전체 대화 흐름을 시간순으로 기록합니다:

```
### [2026-03-29T10:00:00] USER

사용자 메시지 내용

### [2026-03-29T10:00:05] ASSISTANT

AI 응답 내용
```

## Transcript 섹션

DB에 저장된 원시 세션 기록입니다:

- **Cleaned Transcript**: 불필요한 출력을 제거한 정리본
- **Raw Transcript**: 원본 그대로 (ANSI 코드, 시스템 메시지 포함)

## 표시층 (sessions_html/)

이 폴더의 내용을 브라우저에서 읽기 좋게 렌더링합니다:

- Summary는 상단 요약 박스
- Dialogue는 전체 대화 카드
- Transcript는 정리본/원문 토글

HTML은 보기용이지 원문 대체물이 아닙니다.

## AUTO.md 정렬

이 구조는 AUTO.md의 세션 흐름과 일치합니다:

- 세션 시작: AUTO.md → AGENTS.md → current-state → plans
- 세션 종료: 전체 대화를 sessions/에 저장
- 다음 세션: 이전 세션 노트를 읽고 맥락 파악 후 현재 작업 시작
