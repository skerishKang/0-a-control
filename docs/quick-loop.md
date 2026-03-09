# 0-a-control: Quick Operating Loop Cheat Sheet

Use this to quickly check what to say to Codex or what command to run.

## 1. Daily Operating Loop (What to say)

| Phase | Command | Conversation Utterance (Example) |
| :--- | :--- | :--- |
| **Morning** | `status` | "Codex, 브리핑. 주 임무와 오늘 첫 퀘스트 정하자." |
| **Midday** | `status` | "흐름이 좀 끊겼네. 상태 보고하고 다음 퀘스트 다시 잡아줘." |
| **In-Progress** | `status` | "퀘스트 보고: [내용]. 완료 판정 부탁해." |
| **End-of-Day** | `status` | "오늘 마감하자. 한 일, 남은 일, 내일 첫 퀘스트 정리." |

## 2. External Inbox Workflow (How to process)

| Step | Command | Purpose |
| :--- | :--- | :--- |
| **Fetch** | `fetch --status new` | 오늘 들어온 raw 데이터 조회 |
| **Summarize** | `summarize` | 요약 후 계획 후보 추출 |
| **Review** | `mark-reviewing <id>` | 검토 대상 표시 |
| **Approve** | `approve "<id> <bucket>"` | 계획 반영 (today/short_term) |
| **Cleanup** | `reject <id> / archive <id>` | 불필요 항목 정리 |

## 3. Top 10 Command Examples

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
