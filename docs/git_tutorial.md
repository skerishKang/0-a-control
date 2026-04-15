# Git 튜토리얼 for 0-a-control

이 문서는 **Git** 기본 사용법, 브랜치 작업, 커밋 & 푸시 흐름을 단계별로 설명합니다. Windows CMD/PowerShell 환경을 기준으로 작성했습니다.

---

## 1️⃣ 기본 설정 (한 번만 수행)
```bash
# 사용자 정보 설정 (필수)
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# 기본 에디터 (선택)
git config --global core.editor "code --wait"  # VSCode
```

## 2️⃣ 현재 저장소 상태 확인
```bash
# 현재 브랜치와 변경사항 확인
git status
```
> 위 명령을 실행하면 `modified`, `untracked` 파일이 표시됩니다.

## 3️⃣ 변경 내용 스테이징
- **전체 파일 스테이징**
```bash
git add .
```
- **특정 파일만 스테이징**
```bash
git add path/to/file.md
```

> `git status` 로 다시 확인해 스테이징된 파일이 `Changes to be committed` 에 나타나는지 확인합니다.

## 4️⃣ 커밋 만들기
```bash
# 커밋 메시지는 간결하고 목적을 명시합니다.
git commit -m "feat: Add git tutorial and update docs"
```
> 커밋 후 `git log --oneline -5` 로 최근 커밋을 확인할 수 있습니다.

## 5️⃣ 원격 저장소와 연결
프로젝트가 GitHub 등 원격에 연결되어 있지 않다면 아래와 같이 추가합니다.
```bash
# 원격 저장소 URL (예시)
git remote add origin https://github.com/yourusername/0-a-control.git
```
> 기존에 `origin` 이 있을 경우 `git remote set-url origin <new-url>` 로 변경합니다.

## 6️⃣ 푸시 (push) 하기
### 6‑1 기본 푸시 (main 브랜치)
```bash
git push origin main
```
### 6‑2 새 브랜치 만들고 푸시
```bash
# 브랜치 만들고 바로 전환
git checkout -b feature/my-branch

# 작업 후 커밋 → 푸시 (원격에 브랜치 생성)
git push -u origin feature/my-branch
```
> `-u` 옵션은 이후 `git push` / `git pull` 시 브랜치를 자동으로 추적하도록 합니다.

## 7️⃣ 브랜치 관리
### 7‑1 브랜치 리스트 보기
```bash
git branch -vv   # 로컬
git branch -r        # 원격
```
### 7‑2 브랜치 전환
```bash
git checkout main   # 기존 브랜치로 전환
```
### 7‑3 브랜치 삭제 (로컬)
```bash
git branch -d feature/my-branch
```
### 7‑4 원격 브랜치 삭제
```bash
git push origin --delete feature/my-branch
```

## 8️⃣ 병합 (Merge) 와 기본 충돌 해결
```bash
# main 브랜치에 병합
git checkout main
git merge feature/my-branch
```
- 충돌이 발생하면 파일을 열어 **HEAD** 와 **incoming** 부분을 확인하고, 원하지 않는 부분을 삭제 후 저장합니다.
- 충돌 해결 후:
```bash
git add conflicted-file.md
git commit   # 자동으로 충돌 해결 커밋 메시지 생성
```

## 9️⃣ 서브모듈 (submodule) 다루기
현재 `deep-live-cam` 과 `diffusion-canvas` 는 서브모듈처럼 보입니다.
```bash
# 서브모듈 상태 확인
git submodule status

# 서브모듈 변경 내용 커밋
cd deep-live-cam
git add .
git commit -m "update deep-live-cam scripts"
cd ..
git add deep-live-cam
```
> 서브모듈을 커밋하고 최상위 저장소에서도 `git commit` 으로 포함시켜야 원격에 푸시됩니다.

## 🔟 자주 쓰는 명령 정리
| 상황 | 명령 |
|------|------|
| 변경사항 확인 | `git status` |
| 최근 커밋 보기 | `git log --oneline -5` |
| 파일 스테이징 | `git add <path>` |
| 전체 스테이징 | `git add .` |
| 커밋 | `git commit -m "msg"` |
| 원격 푸시 | `git push` |
| 새 브랜치 생성·전환 | `git checkout -b <branch>` |
| 현재 브랜치 확인 | `git branch` |
| 병합 | `git merge <branch>` |
| 충돌 해결 후 커밋 | `git add . && git commit` |

---

## ✅ 실습 체크리스트 (본인 확인용)
1. `git config` 로 사용자 정보 입력
2. `git status` 로 현재 변경 내용 파악
3. `git add .` → `git commit -m "test commit"`
4. `git checkout -b test-branch`
5. 파일 하나 수정 후 커밋 & 푸시 (`git push -u origin test-branch`)
6. `git merge test-branch` 로 main에 병합
7. 서브모듈(`deep-live-cam`) 변경 커밋

위 단계들을 차례대로 실행하면 **커밋** 과 **푸시** 를 자유롭게 할 수 있습니다.

---

> 궁금한 점이 있으면 이 파일을 참고하거나 `git help <command>` 로 상세 도움말을 확인하세요.
