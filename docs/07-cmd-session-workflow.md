# CMD Session Workflow

## Goal
Use short shell commands to start, log, and close a working session without manually handling session IDs.

## Commands
Start a session:

```bash
bash scripts/workon.sh codex cmd 0-myplan "morning planning" gpt-5.1
```

Log a message to the active session:

```bash
bash scripts/worklog.sh user "0-myplan 구조 점검 시작"
```

Log assistant-style progress:

```bash
bash scripts/worklog.sh assistant "후보 프로젝트 3개를 우선으로 좁힘"
```

Check current session:

```bash
bash scripts/workstatus.sh
```

End the active session:

```bash
bash scripts/workdone.sh "0-myplan 구조 점검 완료"
```

## Runtime State
- the active session is stored in `data/runtime/current_session.json`
- this is a local convenience pointer, not the canonical source of truth
- the canonical source of truth remains SQLite

## Next Step
Wrap real tools like `codex`, `gemini`, or `kilo` with these commands so session logging happens automatically.

## Wrapper Commands
Start a tool and auto-open/close a session:

```bash
bash scripts/codex-work.sh 0-myplan "morning planning" gpt-5.1
bash scripts/gemini-cli-work.sh 107-edu-limone-dev "candidate review" gemini-2.5-flash
bash scripts/kilo-work.sh 0-a-control "ops review"
bash scripts/opencode-work.sh 0-conmand-center "quick inspection"
bash scripts/windsurf-work.sh 0-conmand-center "ide review"
bash scripts/antigravity-work.sh 0-conmand-center "ide review"
```

Rules:
- the second argument can be a project folder name under `workdiary` or an absolute path
- the wrapper changes directory into that workspace before launching the tool
- the session is started automatically
- when the tool exits, the session is closed automatically
- canonical agent names stored in SQLite:
  - `codex`
  - `gemini-cli`
  - `antigravity`
  - `windsurf`
  - `kilo`
  - `opencode`

## Foreign Transcript Import
If a tool session was run outside the wrapper, import the saved transcript into an existing session:

```bash
python scripts/import_codex_session.py --session-id <session_id> --project 0-a-control --cwd G:\Ddrive\BatangD\task\workdiary\0-a-control --file path\to\codex.log
python scripts/import_gemini_cli_session.py --session-id <session_id> --project 0-a-control --cwd G:\Ddrive\BatangD\task\workdiary\0-a-control --file path\to\gemini.log
python scripts/import_windsurf_session.py --session-id <session_id> --project 0-a-control --cwd G:\Ddrive\BatangD\task\workdiary\0-a-control --file path\to\windsurf.log
```

If `--file` is omitted, the importer looks for:

```text
data/runtime/transcripts/<session_id>.log
```

### Transcript Profiles
- `codex`: bootstrap block, Codex chrome, token usage, resume hint 제거
- `gemini-cli`: CLI usage/help 배너 제거
- `windsurf`: IDE chrome/Cascade 배너 제거
- transcript detail 화면에서는 `정리본`과 `원문`을 모두 볼 수 있음

### Import Verification Session Cleanup
- importer 검증용 세션은 제목에 `verification` 또는 `importer verification`을 포함
- 검증이 끝난 세션은 장기 운영 판단 근거로 쓰지 않음
- 필요 시 `sessions_html/` 확인 후 DB에서 별도 정리하거나 상태를 검증용으로 메모
- 운영 세션과 검증 세션을 혼동하지 않도록 최근 세션 리뷰 시 제목 기준으로 구분

## Quest Report → External Verdict → 다음 퀘스트 흐름
1. **퀘스트 보고**: `scripts/worklog.sh user`로 보고 내용을 남기고, `report_quest_progress`가 `data/queue/reports/`에 JSON을 생성하며 퀘스트 상태를 `pending`으로 전환한다.
2. **external verdict 대기**: 외부 에이전트(예: Gemini) 워커가 report JSON을 판독해 `data/queue/verdicts/`에 verdict JSON을 기록한다. 이동안 CMD UI에는 동일 퀘스트 카드가 유지되지만 "판정 대기" 배지가 붙는다.
3. **ingest & 업데이트**: `queue_worker.py`가 verdict를 ingest해 `quests`/`plan_items` 및 `current_state`를 갱신한다. verdict 결과가 `done/partial/hold`로 반영되며 pending 배지는 제거된다.
4. **다음 퀘스트 협의**: verdict가 완료되면 `recommended_next_quest`가 채워지고, CLI에서 다음 퀘스트를 선택하거나 새 보고를 작성한다.

## 테스트 체크리스트
| 케이스 | 절차 | 기대 결과 |
| --- | --- | --- |
| pending만 있을 때 | 보고만 제출하고 verdict 대기 | 메인 카드 유지 + pending 배지, `current_state.current_quest` 동일 |
| hold만 있을 때 | 수동으로 hold 판정 적용 | hold 배지, `recommended_next_quest`에 대체 필요 메시지 |
| pending→partial | 보고 후 partial verdict JSON 투입 | quests/plan_items=partial, pending 배지 제거, `restart_point` 반영 |
| pending→done | 보고 후 done verdict JSON 투입 | quests/plan_items=done, 다음 퀘스트 자동 추천 |
| pending→hold | 보고 후 hold verdict JSON 투입 | hold 배지, 대체 퀘스트 권고 |

## UI 가이드 한 줄
- pending 상태는 메인 카드를 바꾸지 말고 "판정 대기" 보조 배지로만 표시하며, 주 임무/현재 퀘스트 카드 수는 항상 1개씩 유지한다.
