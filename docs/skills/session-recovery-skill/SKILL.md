# SKILL.md: 에이전트 작업 연속성 및 세션 복구 (Session Recovery & Continuity)

## 🎯 목적 (Purpose)
에이전트(Codex, Antigravity 등) 간의 작업 중단이나 세션 교체 시, 로컬에 저장된 과거 기록을 분석하여 **"즉시 업무를 이어서 시작할 수 있는 상태"**로 맥락을 복원합니다.

## 🛠️ 데이터 소스 (Data Sources)
스킬 실행 시 다음 경로의 데이터를 우선적으로 탐색합니다:
1. **Codex SQLite**: `~/.codex/state_5.sqlite` (스레드 메타데이터 및 세션 정보)
2. **Codex History**: `~/.codex/history.jsonl` (대화 원문 로그)
3. **로컬 세션 저장소**: `G:\Ddrive\BatangD\task\workdiary\0-a-control\sessions\` 및 `sessions_html/`
4. **프로젝트 문서**: `task.md`, `walkthrough.md`, `implementation_plan.md`

## 🏗️ 3단계 복구 설계 (3-Layer Architecture)
복원된 정보는 반드시 다음 3개 층으로 구분하여 보고해야 합니다.

### 1계층: 원문층 (Raw Source)
- 분석 대상이 된 원래의 로그 파일 경로와 스레드 ID를 명시합니다.
- 요약이 왜곡될 경우를 대비하여 언제든 원문으로 돌아갈 수 있는 링크를 제공합니다.

### 2계층: 복원층 (Operational Recovery)
- **Done**: 완료된 구체적인 작업 내역
- **Remaining**: 아직 해결되지 않은 주제나 비어있는 맥락
- **Next Action**: 지금 바로 실행해야 할 '작은 첫걸음'
- **Handoff Quality**: 현재 복원된 맥락의 충분성 판단 (추가 질문 필요 여부)

### 3계층: 표시층 (Display)
- 사람이 읽기 좋은 형태로 대시보드화하거나 브리핑 요약본을 제공합니다.

## 🧩 주요 관리 토픽 (Key Topics)
복구 시 다음 주제들을 우선적으로 매칭하여 분류합니다:
- **`아파트 (Apartment)`**: 재무 대시보드, 관리규약, 감사보고서 관련 작업
- **`메가존 (Megazone)`**: 외부 협업 및 프로젝트 운영 관련 이슈
- **`board-v2` / `0-a-control`**: 시스템 자체 기능 개선 및 스킬 개발
- **`기타 운영 이슈`**: 잡수입, 커뮤니티 관리 등 일상 작업

## 🚀 실행 가이드 (Execution Guide)

### 트리거 프롬프트 예시
- "이전 Codex 세션 복원해줘"
- "최근 아파트 관련 작업 어디까지 했는지 로그 읽어서 정리해줘"
- "Codex 세션 history.jsonl 분석해서 다음 액션 알려줘"

### 분석 원칙 (Rules)
1. **증거 기반**: 추측하지 말고 실제 로그 파일의 시간대와 메시지 내용을 바탕으로 기술합니다.
2. **답변 누락 고지**: 에이전트의 답변(Assistant Reply)이 로그에 없을 경우, 사용자 메시지만으로 맥락을 추론했음을 명확히 밝힙니다.
3. **연속성 우선**: 단순 요약이 아니라 '재진입 전략(Re-entry Strategy)'을 제시하는 데 집중합니다.

---
> [!TIP]
> 세션 복구 후 항상 "지금 바로 이어서 할까요?"라는 질문과 함께 첫 번째 액션을 제안하십시오.
