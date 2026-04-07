# 지원사업 대시보드 작업공간

이 폴더는 지원사업 공고를 `URL 기반으로 수집`하고, 메타데이터를 `DB`에 저장하며, 공고별 원문/첨부를 `폴더 단위로 보관`하고, 최종적으로 `HTML로 다시 보기` 위한 작업공간이다.

## 목표

- 사용자는 공고 URL만 넣는다.
- 수집기는 제목/마감일/주관기관/첨부파일/원문 링크를 추출한다.
- 공고별 원문 자료는 폴더에 저장한다.
- 정규화된 메타데이터는 DB에 저장한다.
- HTML 렌더러는 DB와 공고 폴더를 읽어 다시 보기 화면을 만든다.
- 회사별 AI 판단은 나중에 붙여도 되도록 구조를 분리한다.

## 1차 범위

- `bizinfo.go.kr` 같은 주요 공고 사이트부터 사이트별 어댑터 방식으로 수집
- 공고별 폴더 생성
- 원문 HTML 스냅샷 저장
- 첨부파일 링크 목록 저장
- 선택적으로 첨부파일 다운로드
- 대시보드용 HTML 생성

## 기본 구조

- `config/`: 수집기/렌더러 설정
- `data/db/`: SQLite 등 로컬 DB 파일 위치
- `data/notices/`: 공고별 폴더 보관
- `data/cache/`: 임시 다운로드/파싱 캐시
- `schemas/`: 내부 데이터 스키마 문서
- `prompts/`: 무료모델/고급모델용 프롬프트
- `scripts/`: 수집, 변환, 렌더링 스크립트
- `templates/`: HTML 템플릿
- `output/`: 생성된 대시보드 HTML
- `.env`: 실제 설정 파일 (git에 포함되지 않음)
- `.env.example`: 설정 예시 파일

### 코드 구조 (scripts/)

```
scripts/
├── local_server.py      # 라우터 (HTTP 요청 분기)
├── common/
│   ├── constants.py    # 상수 (상태 레이블, 색상)
│   └── utils.py        # 유틸 함수 (escape_html, 날짜 파싱)
├── repositories/
│   └── notice_repo.py  # DB 접근 (조회, 저장, 삭제)
├── services/
│   └── notice_service.py  # 비즈니스 로직 (수집)
├── renderers/
│   └── pages.py        # HTML 렌더링 (메인, 상세)
├── ai_provider.py      # AI 분석 (provider별 분기)
└── settings.py         # 설정 로더 (.env)
```

**역할 분리:**
- `local_server.py`: 라우팅만 - GET/POST 분기, 응답 전달
- `repositories/`: DB만 - SQLite 직접 접근
- `services/`: 로직만 - 수집, 외부 URL 호출
- `renderers/`: HTML만 - 문자열 생성
- `common/`: 공통 - 여러 곳에서 쓰는 유틸

## 권장 흐름

1. `URL 입력`
2. `사이트 어댑터 선택`
3. `메타 추출`
4. `공고 폴더 생성`
5. `DB upsert`
6. `HTML 재생성`

## AI 분석 기능

AI 분석은 선택 기능입니다. 현재는 Groq API만 실제 연결되어 있으며, NVIDIA와 Modal은 자리만 마련되어 있습니다.

### 설정 방법

1. `.env.example` 파일을 복사해서 `.env` 파일 생성
2. 사용したい provider 선택: `AI_PROVIDER=groq`
3. 해당 provider의 API 키 입력

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일을 편집하여 API 키 입력
# Windows: notepad .env
# Mac/Linux: nano .env
```

### 지원 provider

| Provider | 상태 | 설명 |
|----------|------|------|
| Groq | ✅ 구현됨 | OpenAI 호환 API, 빠르고 저렴 |
| NVIDIA | 🔜 준비중 | NVIDIA NIM API |
| Modal | 🔜 준비중 | Modal API |

### API 키 발급

- **Groq**: https://console.groq.com/
- **NVIDIA**: https://build.nvidia.com/
- **Modal**: https://modal.com/

### 사용법

상세 페이지에서 "AI 분석 실행" 버튼을 클릭하면:
1. 공고 정보가 AI provider로 전송됨
2. 분석 결과가 자동으로 DB에 저장됨
3. 화면에 결과가 표시됨

### API 직접 호출

```bash
# AI 분석 실행
curl -X POST http://127.0.0.1:8766/analyze-ai \
  -H "Content-Type: application/json" \
  -d '{"notice_id": "PBLN_000000000119288"}'
```

## AI 사용 위치

AI는 필수가 아니다.

- 1차 수집: 규칙 기반
- 요약/정규화: 무료모델 가능
- 회사 적합도/심화 판단: 고급모델

즉, 처음 버전은 AI 없이도 동작해야 한다.

## 사용법 (로컬 서버 - 권장)

로컬 서버를 사용하면 브라우저에서 직접 공고를 수집하고 관리할 수 있습니다.

### 1. 가장 쉬운 시작

프로젝트 폴더에서 `auto.bat`를 실행합니다.

- DB가 없으면 자동 초기화
- 로컬 서버 실행
- 브라우저에서 `http://127.0.0.1:8766` 자동 열기

### 2. 직접 실행

```bash
python scripts/local_server.py
```

### 2. 접속 주소

브라우저에서 다음 주소에 접속:
```
http://127.0.0.1:8766
```

### 3. 브라우저에서 할 수 있는 작업

- **URL 입력 후 공고 수집**: 상단 입력창에 bizinfo.go.kr 공고 URL 입력 후 "수집" 버튼
- **목록 보기**: 모든 공고를 상태/마감일/기관과 함께 확인
- **상세 페이지 보기**: 공고명 클릭 → 사업개요, 첨부파일, 원문 링크 등 확인
- **상태/메모/한줄요약 수정**: 상세 페이지 하단에서 상태 변경, 메모 입력
- **필터링**: 상태별 버튼(전체/신규/검토중/작성중/제출완료/합격/보류) 클릭
- **검색**: 제목, 기관, 요약으로 텍스트 검색

### 4. 종료 방법

서버 실행 콘솔에서 `Ctrl+C`를 누르세요.

---

## 사용법 (정적 HTML - Legacy)

정적 HTML 파일로만 사용하려면 아래 방법을 사용하세요. 현재는 로컬 서버 방식이 권장됩니다.

### 1. DB 초기화 (처음 한 번)

```bash
python scripts/init_db.py
```

### 2. 공고 수집

```bash
python scripts/collect_notice.py "https://www.bizinfo.go.kr/sii/siia/selectSIIA200Detail.do?pblancId=PBLN_000000000119288"
```

### 3. 상태/메모 업데이트

```bash
# 상태만 변경
python scripts/update_notice.py --notice-id PBLN_000000000119288 --status reviewing

# 메모 추가
python scripts/update_notice.py --notice-id PBLN_000000000119288 --note "NIPA형, 컨소시엄 필요"

# 한줄요약 추가
python scripts/update_notice.py --notice-id PBLN_000000000119288 --summary "SW기업-수요기업 컨소시엄형 XaaS 과제"

# 한 번에 여러 개
python scripts/update_notice.py --notice-id PBLN_000000000119288 --status reviewing --note "메모" --summary "한줄요약"
```

상태 값: `new`, `reviewing`, `writing`, `submitted`, `pass`, `hold`

### 4. 대시보드 생성

```bash
python scripts/render_dashboard.py
```

### 5. 대시보드 확인

브라우저에서 `output/site/index.html`을 열면:
- 상태별 필터 가능 (전체/신규/검토중/작성중/제출완료/합격/보류)
- 제목/기관/요약으로 검색 가능
- 각 공고의 상태, 한줄요약, 메모 유무 확인 가능

## 운영 흐름 예시

1. 공고 URL을 받아 수집: `python scripts/collect_notice.py <URL>`
2. 상태를 '검토중'으로 변경: `python scripts/update_notice.py --notice-id <ID> --status reviewing`
3. 관련メモ와 한줄요약 추가
4. 검토 후 상태를 '제출완료' 또는 'pass'로 변경
5. 대시보드에서 전체 현황 확인
