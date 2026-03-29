# Session Full Archive Refactor Prompt

너는 `0-a-control`의 세션 export 구조를 재정의하는 엔지니어다.

작업 경로:
`G:\Ddrive\BatangD\task\workdiary\0-a-control`

핵심 목표:
- `sessions/`를 "운영용 요약 노트"가 아니라 **전체 세션 보존본**으로 바꾼다.
- `sessions_html/`는 그 전체 세션 보존본을 **읽기 좋게 렌더한 HTML 보기판**으로 바꾼다.
- 요약(summary)은 메인 본문이 아니라 **별도 보조층**으로 내린다.

중요한 개념:
1. `raw source`
   - DB source_records / transcript raw content
   - 가장 날것의 원문
2. `session archive`
   - 사람이 다시 읽을 수 있도록 정돈했지만
   - 내용 손실 없이 세션 전체 흐름이 살아 있는 보존본
3. `display layer`
   - `sessions_html/`
   - archive를 보기 좋게 렌더한 층
4. `summary layer`
   - intent / actions / decisions / next start 같은 압축 정보
   - 본문 대체가 아니라 보조 정보

이번 턴 목표:
- 현재 `scripts/export_sessions.py`
- 현재 `scripts/generate_session_html.py`
- 관련 README / 문서
를 아래 방향으로 바꾼다.

원하는 최종 구조:

## 1. sessions/
- 세션별 markdown 파일은 전체 세션 내용을 담아야 한다.
- 최소한 아래가 들어가야 한다.
  - metadata
  - summary block (짧게)
  - dialogue / source records 전체 흐름
  - raw transcript refs 또는 transcript block
  - 필요하면 cleaned/raw 구분
- 요약만 남기고 본문을 생략하면 안 된다.

## 2. sessions_html/
- `sessions/`의 전체 내용을 HTML로 렌더한다.
- 사용자가 브라우저에서 읽기 쉽게 보여줘야 한다.
- 원문/정리본 토글이 있으면 좋지만,
  핵심은 "전체 세션 내용이 빠지지 않는 것"이다.

## 3. summary
- summary는 상단 요약 카드나 summary box로만 둔다.
- 본문 전체를 summary로 대체하지 마라.

반드시 할 일:
1. 현재 구현이 요약 중심인 부분을 전체 보존형으로 바꿔라.
2. `sessions/README.md`를 새 철학에 맞게 수정해라.
3. `sessions_html/README.md`가 없으면 새로 만들어라.
4. `docs/SKILL-session-refresh.md`도 새 구조에 맞게 수정해라.
5. export/generate를 다시 실행했을 때
   - `sessions/`는 전체 보존형 markdown
   - `sessions_html/`는 그 렌더 결과
   가 되게 해라.
6. 기존 session recovery 문서와 충돌하는 문구가 있으면 최소 범위로 바로잡아라.

제약:
- DB 스키마는 함부로 바꾸지 마라.
- transcript raw 데이터를 삭제/축약하지 마라.
- "운영용으로 짧게 압축"하는 기존 철학을 본문 구조에 남기지 마라.
- 가장 작은 수정으로 방향만 정확히 바꿔라.

점검 기준:
1. `sessions/README.md`에 더 이상
   - "compressed session notes"
   - "not transcript dump"
   같은 문구가 중심 철학으로 남지 않는가
2. export된 markdown 하나를 열었을 때
   - 세션 전체 흐름이 실제로 보이는가
3. HTML 하나를 열었을 때
   - 요약만 보이는 게 아니라 전체 내용이 보이는가
4. summary는 보조층으로만 남아 있는가

우선적으로 볼 파일:
- `scripts/export_sessions.py`
- `scripts/generate_session_html.py`
- `scripts/session_summary.py`
- `sessions/README.md`
- `docs/SKILL-session-refresh.md`

가능하면 함께 점검:
- `docs/skills/session-recovery-skill/SKILL.md`
- `docs/skills/session-recovery-skill/05-operational-rollout.md`

검증:
- export 스크립트 실행
- html generate 스크립트 실행
- 생성된 `sessions/*.md` 1개 이상 직접 확인
- 생성된 `sessions_html/*.html` 1개 이상 직접 확인

출력 형식:
- 전체 판정: 통과 / 보완 필요
- 수정한 파일
- 구조적으로 어떻게 바뀌었는지
- 직접 확인한 생성 결과
- 남은 리스크

한 줄 결론:
- `sessions`는 전체 세션 archive,
- `sessions_html`은 그 archive의 display layer,
- summary는 별도 보조층
으로 재정의하는 작업이다.
