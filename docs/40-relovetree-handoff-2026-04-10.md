# Relovetree Handoff Note

> 작성일: 2026-04-10
> 프로젝트: [133-relovetree](/mnt/g/Ddrive/BatangD/task/workdiary/133-relovetree)

## 현재 상태

- 운영 URL: `https://lovetree.limone.dev`
- 프론트: plain HTML + plain CSS + 브라우저 JS
- 인증: Firebase Auth
- 앱 데이터: Netlify Functions + Neon/Postgres
- 구조 원칙:
  - Firebase는 로그인/세션만 담당
  - 앱 CRUD는 Firestore 호환 레이어를 거쳐 실제로 Neon/Postgres에 저장

## 먼저 볼 문서

1. [README.md](/mnt/g/Ddrive/BatangD/task/workdiary/133-relovetree/README.md)
2. [OPERATIONS.md](/mnt/g/Ddrive/BatangD/task/workdiary/133-relovetree/docs/ops/OPERATIONS.md)
3. [RUNBOOK.md](/mnt/g/Ddrive/BatangD/task/workdiary/133-relovetree/docs/ops/RUNBOOK.md)
4. [FIRESTORE_COMPAT_ANALYSIS.md](/mnt/g/Ddrive/BatangD/task/workdiary/133-relovetree/docs/analysis/FIRESTORE_COMPAT_ANALYSIS.md)
5. [DATABASE_NAMING_MIGRATION_PLAN.md](/mnt/g/Ddrive/BatangD/task/workdiary/133-relovetree/docs/plans/DATABASE_NAMING_MIGRATION_PLAN.md)

## 최근 핵심 정리

- 홈 화면 CSS/semantic class 복구 완료
- PWA/service worker 제거 완료
- 최근 방문한 트리 이름 정규화 완료
  - 내부 id 대신 `나의 러브트리`, `가져온 러브트리` 표시
- 인기 러브트리 fallback 복구 완료
- 테스트 계정 `displayName` 운영 정책 정리 완료
- Firebase Auth vs Neon/Postgres 역할 문서화 완료

## 테스트 계정 운영 원칙

- 유지 계정:
  - `qa.relovetree.20260409@gmail.com`
  - `qa-playwright-2@example.com`
- 삭제보다 재사용 우선
- 공개 화면 참여 시 이메일 대신 `displayName` 사용
- 권장 표시 이름:
  - `테스트 러버 A`
  - `테스트 러버 B`

## Alias 전환 상태

### 완료

- `src/owner-api-client.js`
- `src/shared.js`
- `src/owner-dialogs.js`
- `src/index-search.js`
- `src/index-data.js`
- `src/entries/community.js`
- `src/entries/admin.js`
- `src/auth.js`

### 보류

- `src/editor-bootstrap.js`

보류 이유:
- 에디터 초기화 코어
- `runtime.db` 시작점
- 영향 범위가 커서 별도 세션에서 집중 검증 필요

## 다음 세션 첫 작업 추천

1. `src/editor-bootstrap.js` 분석
2. 에디터 로드/저장/포크 흐름 기준 테스트 포인트 확정
3. 가능하면 최소 범위 alias 전환
4. 실브라우저에서 에디터 회귀 검증

## 운영 메모

- 결제는 현재 비활성 상태여도 정상
- App Check는 아직 운영 콘솔 작업이 남아 있을 수 있음
- `_FOSSIL_`, `relovetree.local.fossil`은 Git 배포 기준에선 보통 제외
- 다음 세션에서 혼동되면 "Firebase는 로그인, 데이터는 Neon"만 먼저 기억하면 됨
