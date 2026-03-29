# 0-a-control-ops Skill

이 스킬은 로컬 운영 대시보드 `0-a-control` (`http://localhost:4310/board-v2.html`)의 반복적인 웹 작업을 자동화합니다.

## 트리거 조건
- `0-a-control 열어줘`
- `메인 미션/현재 퀘스트 요약해줘`
- `완료 탭 요약해줘`
- `0-a-control에 [텍스트] 입력해줘`
- `quick input 넣어줘`

## 핵심 워크플로

### 1. 현재 상태 요약 (Read Current State)
- **대상 URL**: `http://localhost:4310/board-v2.html`
- **단계**:
  1. 페이지 접속 후 `.v2-root` 요소가 나타날 때까지 대기.
  2. 다음 요소에서 텍스트 추출:
     - 메인 미션: `.v2-mission-title`
     - 현재 퀘스트: `.v2-quest-title`
     - Why Now: `.v2-why-now-box`
  3. 추출한 내용을 한국어로 간결하게 요약하여 보고.

### 2. 완료 내역 요약 (Read Completed Work)
- **대상 URL**: `http://localhost:4310/board-v2.html`
- **단계**:
  1. 페이지 접속.
  2. 텍스트가 "완료"인 `.v2-phase-tab` 버튼 클릭.
  3. 목록(`ul.v2-list`)이 렌더링될 때까지 대기.
  4. '오늘 완료', '최근 완료' 섹션의 항목들을 읽어 요약 보고.

### 3. 빠른 입력 제출 (Submit Quick Input)
- **대상 URL**: `http://localhost:4310/board-v2.html`
- **단계**:
  1. 페이지 접속.
  2. `textarea#v2QuickInput` 요소를 찾아 사용자가 요청한 [텍스트] 입력.
  3. `window.boardV2SubmitQuickInput()`을 호출하는 버튼을 클릭하거나 `Enter` 키 전송.
  4. 제출 성공 여부를 UI 변화를 통해 확인 후 보고.

## 운영 규칙
- **스크린샷**: 모든 작업 완료 후 최종 상태를 스크린샷(`.png`)으로 남겨 검증 자료로 활용.
- **예외 처리**: 
  - 로컬 서버(`localhost:4310`) 접속 불가 시 즉시 중단 및 보고.
  - 예상 셀렉터가 없거나 UI 구조가 변경된 경우 무리하게 추측하지 말고 중단 후 보고.
- **간결성**: 결과 보고는 불필요한 미사여구 없이 정보 위주로 한국어 요약.

## 제약 사항
- 일반적인 웹 브라우징이 아닌, 정해진 `0-a-control` 로컬 사이트 운영에만 사용.
- 모르는 구조의 페이지 탐색은 일반 브라우저 도구 기능을 사용하고, 이 스킬은 **반복 운영**에만 적용.
