# 0-a-control: Quick Operating Loop Cheat Sheet

Use this to quickly check what to say to Codex or what command to run.

## 0. Archive 읽기 (모든 단계의 전제)

모든 단계에서 **먼저 current state를 보고, 관련 archive만 선택적으로 읽습니다.**

| 언제 | 무엇을 | 명령어 |
|------|--------|--------|
| 아침 | 최근 세션 목록 | `ls -lt sessions/ \| head -3` |
| 아침 | 특정 세션 읽기 | `cat sessions/YYYY-MM-DD/filename.md` |
| 작업 중 | 세션 복원 | `codex 세션 복원해줘` |
| 마감 | 오늘 세션 확인 | `ls sessions/$(date +%Y-%m-%d)/` |

**읽기 기준**: 전체를 읽을 필요 없음. 오늘 주제와 관련된 세션만.

## 1. Daily Operating Loop

| Phase | Time | What To Say |
| :--- | :--- | :--- |
| **아침** | 1분 | "어제 archive 확인하고 오늘 주 임무 정하자." |
| **작업 중** | 30초 | "퀘스트 보고: [내용]. 완료 판정 부탁해." |
| **재정렬** | 30초 | "흐름 끊겼네. 상태 보고 다음 퀘스트 잡아줘." |
| **마감** | 2분 | "오늘 마감. 한 일, 남은 일, 내일 첫 퀘스트 정리." |

## 2. Archive 관련 명령어

| 목적 | 명령어 |
|------|--------|
| 세션 export | `python scripts/export_sessions.py` |
| HTML 생성 | `python scripts/generate_session_html.py` |
| 통합 실행 | `bash scripts/refresh_sessions.sh` |
| 세션 복원 | `codex 세션 복원해줘` |
| 특정 주제 복원 | `board-v2 관련 codex 세션 복원해줘` |

## 3. External Inbox Workflow

| Step | Command | Purpose |
| :--- | :--- | :--- |
| **Fetch** | `fetch --status new` | 오늘 들어온 raw 데이터 조회 |
| **Summarize** | `summarize` | 요약 후 계획 후보 추출 |
| **Review** | `mark-reviewing <id>` | 검토 대상 표시 |
| **Approve** | `approve "<id> <bucket>"` | 계획 반영 (today/short_term) |
| **Cleanup** | `reject <id> / archive <id>` | 불필요 항목 정리 |

## 4. Top 10 Command Examples

1. `python scripts/operating_loop_cli.py status`
2. `python scripts/inbox_cli.py fetch --time-range 6h --status new`
3. `python scripts/inbox_cli.py summarize --sources self_chat kang_hyerim_chat`
4. `python scripts/inbox_cli.py approve "1 today, 2 short_term"`
5. `python scripts/inbox_cli.py mark-reviewing 10 11`
6. `python scripts/inbox_cli.py archive 12 --reason "참고용"`
7. `python scripts/inbox_cli.py reject 13 --reason "스팸"`
8. `python scripts/inbox_cli.py digest --time-range 1d`
9. `python scripts/operating_loop_cli.py prompt --phase morning`
10. `python scripts/operating_loop_cli.py checklist --phase in-progress`

## 5. 언제 archive를 읽고 언제 안 읽는지

| 상황 | 행동 |
|------|------|
| 오늘 주제와 관련된 어제 세션이 있으면 | 해당 세션 Dialogue 읽기 |
| 관련 세션이 없으면 | 건너뜀 |
| 작업 중 맥락이 기억 안 나면 | 관련 세션 일부 재확인 |
| 새 세션 시작 | `codex 세션 복원해줘` |
| 주제가 명확하면 | archive 건너뜀 |
