# 15. 배포 및 접근 경로 체크리스트

이 문서는 `0-a-control` 로컬 대시보드를 고정된 접근 경로로 운영할 때 필요한 최소 기준을 정리한다. 현재 서버는 개인 로컬 운영을 기본값으로 두며, 원격 접근은 명시적으로 열 때만 허용한다.

## 현재 기준

- 서버 진입점: `scripts/server.py`
- 기본 실행: `python scripts/server.py`
- 기본 주소: `http://127.0.0.1:4310`
- 셸 래퍼: `start-control-tower.sh`, `start-control-tower.bat`
- 기본 UI: `/board-v2.html`
- 루트 접근: `/` → `/board-v2.html` 리다이렉트

## 운영 모드

### 1. local-only 모드 (기본값, 권장)

가장 안전한 모드다. 같은 머신에서만 접근한다.

- `HOST=127.0.0.1` (기본값)
- `PORT=4310` (기본값)
- 같은 머신의 브라우저에서만 접근 가능
- 외부 네트워크, 공유기 포트포워딩, 공인 IP 노출을 사용하지 않음
- API guard가 기본적으로 local loopback 클라이언트만 허용

사용 예:

```bash
python scripts/server.py
# 브라우저에서 http://localhost:4310 접속
```

이 모드에서는 별도의 접근 제어 환경 변수를 설정할 필요가 없다.

### 2. LAN 모드

동일 사설망의 다른 장치에서 접근해야 할 때만 사용한다.

- `HOST=0.0.0.0`
- `PORT=4310` 또는 충돌 없는 포트
- 운영체제 방화벽에서 허용할 IP 대역을 제한한다.
- 공유기 포트포워딩을 열지 않는다.
- 신뢰하지 않는 네트워크에서는 사용하지 않는다.

API 접근을 허용하려면 다음 환경 변수를 설정한다:

```bash
# 읽기 API 허용 (대시보드 조회)
CONTROL_TOWER_ALLOW_NONLOCAL_READS=1

# 변경 API 허용 (상태 변경, verdict 등)
CONTROL_TOWER_ALLOW_NONLOCAL_MUTATIONS=1
```

### 3. 원격/인터넷 접근 모드

인터넷에서 접근하려는 경우 **직접 Python 서버를 공개하지 않는다**. 반드시 reverse proxy 또는 터널 앞단에서 TLS와 접근 제어를 적용한다.

권장 구성:

- Python 서버는 `127.0.0.1:4310`에만 바인딩한다.
- Nginx, Caddy, Cloudflare Tunnel, Tailscale, Zero Trust Access 등 외부 접근 계층을 앞에 둔다.
- TLS를 적용한다.
- 접근 허용 사용자를 제한한다.
- 서버 방화벽에서 Python 서버 포트를 외부에 직접 공개하지 않는다.

## API 접근 guard

서버는 `scripts/server_request_guard.py`를 통해 모든 API 요청의 출처를 검증한다.

### 기본 동작

| 경로 | 기본 접근 | 설명 |
|------|-----------|------|
| `/api/health` | public | 헬스체크. smoke test 등에서 사용 |
| 그 외 `/api/*` GET | local only | 읽기 API. loopback 클라이언트만 허용 |
| `/api/*` POST/PATCH | local only | 변경 API. loopback 클라이언트만 허용 |

### 비local 접근 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `CONTROL_TOWER_ALLOW_NONLOCAL_READS` | unset (거부) | 비local 읽기 허용 |
| `CONTROL_TOWER_ALLOW_NONLOCAL_MUTATIONS` | unset (거부) | 비local 변경 허용 |

**Truthy 값:** `1`, `true`, `yes`, `on` (대소문자 구분 없음)

예시:

```bash
# 읽기만 허용 (대시보드 조회 전용)
CONTROL_TOWER_ALLOW_NONLOCAL_READS=1

# 읽기 + 변경 모두 허용
CONTROL_TOWER_ALLOW_NONLOCAL_READS=1
CONTROL_TOWER_ALLOW_NONLOCAL_MUTATIONS=1
```

### guard 검증 로직

비local 접근이 활성화되지 않은 경우, 요청이 허용되려면 다음을 모두 충족해야 한다:

1. 클라이언트 주소가 loopback (`127.0.0.1`, `::1`, `localhost`)
2. `Host` 헤더가 loopback 주소이거나 비어 있음
3. `Origin` 헤더가 loopback 주소이거나 비어 있음

## 비local 접근 경고

`CONTROL_TOWER_ALLOW_NONLOCAL_READS` 또는 `CONTROL_TOWER_ALLOW_NONLOCAL_MUTATIONS`를 활성화하면 다음 데이터가 네트워크를 통해 노출될 수 있다:

- 개인 작업 컨텍스트 (plans, quests, decisions)
- Telegram에서 가져온 메시지 및 세션 로그
- 에이전트 출력 및 세션 기록
- 큐/verdict 레코드
- 작업 일지 및 brief 데이터

**이 데이터는 개인 작업 도구의 민감한 내용이다.** 비local 접근을 활성화하기 전에 반드시 아래 체크리스트를 확인하라.

## 환경 변수 참조

### 서버 바인딩

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `HOST` | `127.0.0.1` | 서버 바인딩 주소 |
| `PORT` | `4310` | 서버 포트 |
| `DEBUG` | unset | 설정 시 HTTP 로그 출력 |

### 접근 제어

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `CONTROL_TOWER_ALLOW_NONLOCAL_READS` | unset | 비local 읽기 허용 (truthy: `1`, `true`, `yes`, `on`) |
| `CONTROL_TOWER_ALLOW_NONLOCAL_MUTATIONS` | unset | 비local 변경 허용 (truthy: `1`, `true`, `yes`, `on`) |

### Telegram 동기화

| 변수 | 설명 |
|------|------|
| `TELEGRAM_API_ID` | Telegram API ID |
| `TELEGRAM_API_HASH` | Telegram API hash |
| `CONTROL_TOWER_TELEGRAM_SESSION_PATH` | 선택 사항. Telegram 세션 파일 경로 override |

## 배포 전 체크리스트

### local-only (기본값)

- [ ] `python scripts/server.py`로 서버가 실행된다.
- [ ] `http://localhost:4310`에서 `/board-v2.html`이 열린다.
- [ ] `/api/health`가 `{ "ok": true }`를 반환한다.
- [ ] 로컬 데이터 파일과 세션 파일이 저장소에 커밋되지 않는다.
- [ ] `CONTROL_TOWER_ALLOW_NONLOCAL_READS`가 설정되어 있지 않다.
- [ ] `CONTROL_TOWER_ALLOW_NONLOCAL_MUTATIONS`가 설정되어 있지 않다.

### LAN

- [ ] 원격 장치에서 접근할 필요가 실제로 있다.
- [ ] `HOST=0.0.0.0` 사용 이유가 명확하다.
- [ ] 운영체제 방화벽에서 신뢰할 수 있는 사설 IP만 허용한다.
- [ ] 공유기 포트포워딩을 사용하지 않는다.
- [ ] 민감 데이터가 화면에 표시되는지 확인했다.
- [ ] 필요한 경우에만 `CONTROL_TOWER_ALLOW_NONLOCAL_READS=1`을 설정한다.
- [ ] 변경 API가 필요할 때만 `CONTROL_TOWER_ALLOW_NONLOCAL_MUTATIONS=1`을 설정한다.
- [ ] 노출되는 데이터 범위를 확인했다 (작업 컨텍스트, 세션 로그, Telegram 데이터 등).

### 인터넷 원격 접근

- [ ] **Python 서버 포트를 인터넷에 직접 열지 않는다.**
- [ ] reverse proxy, VPN, tunnel, Zero Trust Access 계층 중 하나를 사용한다.
- [ ] TLS가 적용되어 있다.
- [ ] 접근 허용 사용자가 제한되어 있다.
- [ ] 서버 프로세스 재시작 방식이 정해져 있다.
- [ ] 백업/복구 대상 데이터 경로가 정리되어 있다.
- [ ] 노출되는 데이터의 민감도를 평가했다.
- [ ] 접근 로그를 남길 수 있는 구조인지 확인했다.

## 권장 reverse proxy 개념

Python 서버:

- `HOST=127.0.0.1`
- `PORT=4310`

외부 접근 계층:

- HTTPS 종료
- 사용자 접근 제어
- 요청 크기 제한
- 접속 로그
- 필요 시 IP allowlist

## 프로세스 운영 기준

로컬에서는 터미널 실행으로 충분하다. 상시 운영하려면 다음 중 하나를 선택한다.

- Windows Task Scheduler
- NSSM 또는 유사한 Windows service wrapper
- systemd user service
- tmux/screen
- Docker 또는 compose wrapper

상시 운영 전 확인할 사항:

- 프로세스가 죽었을 때 재시작되는가
- 로그를 어디에 남기는가
- 데이터 백업 위치가 정해졌는가
- 환경 변수를 안전하게 주입하는가

## 백업 대상

최소 백업 대상:

- `data/` 중 운영 DB와 런타임 상태
- 필요한 경우 `data/runtime/`
- Telegram 세션 파일은 민감 파일로 취급한다.

백업 제외 권장:

- 캐시
- 임시 파일
- 로그 중 민감 내용이 섞일 수 있는 파일
- 개인 토큰 또는 세션 파일의 공개 저장소 커밋

## 현재 한계

- 서버 자체 인증 계층은 없다.
- 브라우저 UI는 로컬 개인 운영을 전제로 한다.
- 원격 다중 사용자 운영 모델은 정의되어 있지 않다.
- 실시간 push 채널은 없다.
- 원격 배포 시에는 앞단 접근 제어가 필수다.

## 후속 작업

- #9 설정 및 안전 가드레일 화면에서 현재 `HOST`, `PORT`, Telegram 설정 상태를 더 명확히 표시한다.
- #10 배포 및 접근 경로에서 선택한 배포 방식을 문서와 스크립트에 반영한다.
- #11 README 및 운영 사용법에서 이 문서를 빠른 시작 이후의 운영 문서로 연결한다.
- 인증이 필요한 경우 서버 레벨의 token middleware 또는 reverse proxy 기반 인증 중 하나를 선택한다.
