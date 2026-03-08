# 10. Verdict Prompt Spec

## 1. 목표
- 외부 에이전트(IDE, CLI, LLM)가 `quest_reports/`의 report JSON을 입력받아 표준 verdict JSON을 생성하도록 가이드를 제공한다.
- 본 스펙은 `docs/06-implementation-handoff.md`의 커맨드 규칙과 `docs/08-09`의 파이프라인/스키마를 준수한다.

## 2. 기본 프롬프트 구조
```
SYSTEM:
너는 개인 컨트롤 타워의 퀘스트 판정관이다. 아래 규칙을 따른다.
1. verdict.status는 done/partial/hold 중 하나여야 한다.
2. reason/restart_point/next_hint/plan_impact는 한국어로 간결하게 작성한다.
3. plan_impact는 today/short_term/long_term/recurring/dated 키를 모두 포함한다.
4. JSON 이외 내용을 출력하지 않는다.

USER:
{report_json}
```
- `{report_json}` 자리에는 report 파일 전체가 그대로 삽입된다.
- 추가 컨텍스트가 필요하면 `session_exports/` 경로를 열어 참고하되, 최종 출력은 단일 JSON.

## 3. LLM/CLI 호출 예시
```bash
cat quest_reports/20260309T053100Z-q123-s456.report.json \
  | python scripts/gemini_verdict.py \
  > quest_verdicts/20260309T053100Z-q123-s456.verdict.json
```
- `gemini_verdict.py`는 stdin 프롬프트를 그대로 모델에 전달하고 JSON 블록만 stdout으로 출력.
- 다른 모델을 쓰는 경우에도 동일 stdin/stdout 계약을 맞춘다.

## 4. 프롬프트 세부 규칙
1. **언어**: reason/restart_point/next_hint는 반드시 한국어.
2. **정확성**: completion_criteria 대비 실제 work_summary를 근거로 판단.
3. **재시작 지점**: 남은 일 또는 blocker를 구체적 행동으로 요약.
4. **next_hint**: 한 줄짜리 실천 단계.
5. **plan_impact**: 오늘/단기/장기/반복/기한 버킷에 미치는 변경점을 서술. 영향 없으면 `"--"`.
6. **confidence**: 모델이 자체적으로 추정한 0~1 사이 값 (선택 필드지만 권장).
7. **ai_tags**: 판정을 설명할 키워드 배열. 세션 필터링에 사용.

## 5. 실패 대비 지침
- 모델이 비JSON 텍스트를 섞어 출력할 수 있으므로 `scripts/gemini_verdict.py`처럼 JSON 추출기를 둔다.
- verdict JSON 유효성 검사에 실패하면 해당 에이전트는 즉시 재시도하거나 히스토리를 `session_exports/`에 기록한다.

## 6. 외부 에이전트 체크리스트
1. **입력 확인**: report JSON의 `quest_id`, `completion_criteria`, `plan_links`를 먼저 파악.
2. **판정 로직**:
   - done: completion_criteria 충족, remaining_work 없음.
   - partial: 의미 있는 진전 + remaining_work 존재.
   - hold: 진행 어려움 또는 blocker.
3. **출력 검증**:
   - schema_version 포함 여부 확인.
   - verdict.status 허용 값 확인.
   - plan_impact에 5개 버킷 모두 기입.
4. **파일 저장**: verdict 파일명은 report base name 재사용.
5. **재판정**: 동일 report 재판정 시 verdict JSON의 `metadata.verdict_seq`를 증가시켜 충돌 방지.

## 7. 재처리 전략
- `verdict_verifier.py` 같은 스크립트로 JSON Schema 검증 후 서버에 넘긴다.
- 실패 유형별 조치:
  1. **verdict 없음**: report 생성 후 `VERDICT_TIMEOUT_MIN` 초 경과 시 알림을 발생시키고 에이전트가 우선 처리.
  2. **JSON 파손**: `quest_verdicts/failed/{report_id}.json`으로 이동, 원본 report는 그대로 둬서 재시도 가능.
  3. **중복 처리**: ingest 측에서 첫 성공 verdict만 수용, 나머지는 `processed/duplicates/`로 이동.
  4. **동일 report 재판정**: `metadata.verdict_seq` 비교 후 더 큰 값만 최신으로 채택.

## 8. 참고 연결
- 파이프라인 흐름: `docs/08-file-verdict-pipeline.md`
- JSON 상세: `docs/09-json-contracts.md`
- 데이터베이스 및 상태 플로우: `docs/05-data-schema.md`, `docs/06-implementation-handoff.md`, `docs/07-cmd-session-workflow.md`
