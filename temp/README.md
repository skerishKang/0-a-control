# YouTube Brief 임시 파일 보관소

이 폴더는 `47-youtube-brief` 프로젝트의 **임시 작업 디렉토리**입니다.

## 목적

YouTube 영상 요약을 DB에 등록할 때 다음과 같은 흐름으로 사용됩니다:

1. **사용자**가 AI에게 YouTube 요약을 붙여넣기
2. **AI**가 요약 내용을 `temp/` 폴더에 `.txt` 파일로 저장
3. **사용자/AI**가 `ingest-brief` 명령으로 DB 등록
4. **등록 완료 후** 원본 파일 자동 삭제

## 사용 방법

```bash
# DB에 등록 (temp 폴더의 파일을 처리)
python scripts/youtube_brief_cli.py ingest-brief

# 또는 특정 파일 지정
python scripts/youtube_brief_cli.py ingest-brief --input-file "temp/summary.txt"
```

## 파일 형식

파일명은 자유롭지만, 내용은 다음 메타 정보를 포함해야 합니다:

```
[채널명]: 채널이름
[영상 제목]: 제목
[유튜브 주소]: https://youtube.com/watch?v=...
[게시 날짜]: 2026-04-17

### 1. 초상세 타임라인 내러티브
[타임라인 내용]

### 2. 요약 한 줄
[한 줄 요약]

### 3. 핵심 키워드
**키워드1, 키워드2**

...
```

또는 볼드 형식도 지원:
```
**채널명**: 채널이름
**영상 제목**: 제목
**유튜브 주소**: https://...
**게시 날짜**: 2026-04-17
```

## 주의사항

- 이 폴더의 파일들은 **임시 저장소**입니다.
- DB 등록 성공 후 **자동 삭제**됩니다.
- Git 추적 대상이 아닙니다 (`.gitignore`에 포함).
- 수동으로 파일을 넣을 때는 같은 형식을 유지하세요.

## 관련 위치

- **실제 프로젝트 루트**: `G:\Ddrive\BatangD\task\workdiary\47-youtube-brief\`
- **DB 파일**: `47-youtube-brief/data/youtube_brief.db`
- **웹 UI**: `http://127.0.0.1:4324`
