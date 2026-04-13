---
name: session-refresh
description: "세션 노트를 DB에서 export하고 읽기 좋은 구조로 갱신한다. sessions/ 폴더를 운영 메모리 canonical 소스로 유지."
---

# session-refresh

## 언제 쓰는지

- 작업 세션을 마친 후 ("세션 갱신해줘")
- 새 세션을 시작하기 전 맥락 정리
- 많은 세션이 누적되어 정리가 필요할 때
- ops-close 모드에서 마감 시 세션 갱신 단계
- 사용자가 명시적으로 "refresh sessions" 요청

## 입력으로 기대하는 정보

1. `data/control_tower.db`의 `sessions` 테이블
2. `data/control_tower.db`의 `source_records` 테이블
3. 기존 `sessions/` 폴더 구조

## 실행 절차

### Step 1: 세션 export

Unix/WSL 환경:

```bash
bash scripts/refresh_sessions.sh
```

Windows 환경:

```cmd
python scripts\export_sessions.py
```

또는 Windows 래퍼:

```cmd
refresh-sessions.bat
```

`export_sessions.py`가 하는 일:
1. `data/control_tower.db`의 `sessions` 테이블을 읽는다
2. 각 세션을 Markdown 노트로 변환한다
3. `sessions/YYYY-MM-DD/` 폴더에 저장한다
4. `sessions/INDEX.md`를 갱신한다

세션 노트 구조는 Intent/Actions/Decisions/Artifacts/Next Start/Raw Refs 형식을 따른다.

### Step 2: HTML 갱신 (선택)

```bash
python scripts/generate_session_html.py
```

이 단계는 선택 사항이다. Markdown 노트만으로 충분하면 생략한다.

### Step 3: 결과 확인

```bash
ls -lt sessions/ | head -5
cat sessions/INDEX.md | head -20
```

확인 항목:
- `sessions/INDEX.md`가 갱신되었는가
- 최근 세션 파일이 생성되었는가
- 날짜 폴더 구조가 올바른가

### Step 4: 결과 출력

```
세션 갱신 완료

Export된 세션: {N}개
INDEX.md 갱신: 완료
HTML 생성: {완료/건너뜀}

최근 세션:
- {날짜}/{세션파일명}
- {날짜}/{세션파일명}
```

## 출력 형식

- 한국어로 출력한다.
- export된 세션 수와 최근 파일 목록을 표시한다.

## 실패/누락 시 fallback

| 상황 | fallback |
|------|----------|
| `refresh_sessions.sh` 실행 불가 | 직접 `python scripts/export_sessions.py` 실행 |
| DB 접근 불가 | "DB 접근 불가. 세션 갱신을 건너뜁니다" 안내 |
| `generate_session_html.py` 없음 | Markdown export만 수행 |
| export 결과가 transcript dump | "운영 노트가 아닌 transcript가 생성됨. export 로직 점검 필요" 경고 |
| `sessions/` 폴더 없음 | 자동 생성 후 export 수행 |

## 관련 파일/스크립트

- `scripts/export_sessions.py` — DB → Markdown export
- `scripts/generate_session_html.py` — Markdown → HTML 변환
- `scripts/refresh_sessions.sh` — 통합 실행 스크립트 (Unix/WSL)
- `refresh-sessions.bat` — Windows 래퍼
- `.kilo/rules-ops-close/01-closing-rules.md` — ops-close 모드 세부 규칙
- `AGENTS.md` — Memory Hierarchy 섹션

## 제한 사항

- 이 skill은 **읽기/내보내기 전용**이다. DB 스키마나 원시 데이터를 수정하지 않는다.
- 세션 노트는 Intent/Actions/Decisions/Artifacts/Next Start 구조를 유지해야 한다.
- transcript dump가 아닌 운영 메모리를 생성하는 것이 목표다.
- 표준 명령어(`refresh_sessions.sh` 또는 `export_sessions.py`)만 사용한다. 직접 Python 명령어로 ad-hoc export하지 않는다.
