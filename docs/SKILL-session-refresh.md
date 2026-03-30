# SKILL: Session Refresh

## Description

이 스킬은 세션 보존본을 DB에서 sessions/ 폴더로 export하고, 선택적으로 HTML 표시층을 생성하는 표준 절차를 정의합니다.

**목적**: sessions/를 세션의 전체 보존본으로 유지합니다.

---

## Trigger Conditions

이 스킬을 사용하는 경우:

1. **세션 보존본 갱신** — 최신 세션을 DB에서 sessions/로 export하려 할 때
2. **새 세션 시작 전** — 이전 작업 맥락을 확인해야 할 때
3. **세션 누적 시** — 읽기 좋은 구조로 정리해야 할 때
4. **사용자 요청 시** — 명시적으로 세션 갱신을 요청할 때

---

## 표준 명령

### Unix/WSL
```bash
bash scripts/refresh_sessions.sh
```

### Windows
```cmd
refresh-sessions.bat
```

또는 직접:
```cmd
python scripts\export_sessions.py
python scripts\generate_session_html.py
```

---

## 예상 출력

| 출력 | 위치 |
|------|------|
| 세션 보존본 (Markdown) | `sessions/YYYY-MM-DD/*.md` |
| 세션 인덱스 | `sessions/INDEX.md` |
| HTML 표시층 (선택) | `sessions_html/index.html` |

---

## 세션 파일 구조

각 세션 파일은 다음을 포함합니다:

| 층 | 역할 | 포함 내용 |
|---|------|-----------|
| **Metadata** | 세션 기본 정보 | ID, 시간, Agent, Model 등 |
| **Summary** | 짧은 요약 (보조층) | Intent, Actions, Decisions, Next Start |
| **Dialogue** | 전체 대화 흐름 | USER / ASSISTANT / TOOL 메시지 |
| **Transcript** | 원시 세션 기록 | cleaned + raw transcript |

### 중요: 요약은 보조층입니다

- Summary는 파일 상단에 짧은 박스로만 존재합니다
- 본문 전체를 Summary로 대체하지 않습니다
- AI 응답이 없으면 "assistant 응답 없음"을 명시합니다

---

## 실행 절차

1. `scripts/export_sessions.py` 실행
   - `data/control_tower.db`의 `sessions` 테이블 읽기
   - 각 세션을 전체 보존본 Markdown으로 변환
   - Dialogue + Transcript 포함
   - `sessions/INDEX.md` 갱신

2. `scripts/generate_session_html.py` 실행 (선택)
   - Markdown을 HTML로 변환
   - `sessions_html/` 구조 생성
   - Summary 박스 + Dialogue 카드 + Transcript 토글

---

## 실패 조건

다음은 실패로 간주합니다:

1. **요약만 남기기** — 전체 대화를 생략하면 실패
2. **비표준 명령어 사용** — 표준 스크립트 대신 ad-hoc Python 명령 실행
3. **DB 수정** — export 중 DB 스키마나 데이터 변경
4. **대화 생략** — Dialogue 섹션이 비어있으면 실패

---

## Recovery 시 읽기 순서

세션 복원 시 다음 순서로 읽습니다:

1. **current urgent state** 확인
2. **관련 sessions archive** 확인 (이 폴더의 .md 파일)
3. **sessions_html**로 빠른 탐색
4. **raw transcript / DB source_records** 확인
5. **summary/current quest**로 압축

---

## 관련 파일

- `scripts/export_sessions.py` — DB → Markdown export
- `scripts/generate_session_html.py` — Markdown → HTML 변환
- `scripts/refresh_sessions.sh` — 통합 실행 스크립트 (Unix/WSL)
- `refresh-sessions.bat` — Windows 래퍼
- `sessions/README.md` — 세션 아카이브 구조 설명
- `sessions/TEMPLATE.md` — 세션 노트 템플릿
- `sessions_html/README.md` — HTML 표시층 설명

---

## 핵심 원칙

- **전체 보존, 요약은 보조** — 세션의 전체 대화 흐름을 보존합니다
- **표준 명령만 사용** — export는 항상 표준 스크립트로 실행합니다
- **읽기 좋은 출력** — Markdown(소스)과 HTML(보기) 모두 사용 가능
- **DB 수정 금지** — 이 작업은 읽기/내보내기 전용입니다
