1. 변경 요약
   verdict_import.py 파일에서 파일 읽기 작업 중 발생할 수 있는 OSError(예: 권한 문제, 파일 삭제)를 처리하지 않아 worker가 crash할 수 있는 문제를 최소한의 수정으로 보강

2. 수정 파일
   G:\Ddrive\BatangD\task\workdiary\0-a-control\scripts\verdict_import.py

3. 핵심 수정 내용
   - 줄 134 주변: 기존 JSONDecodeError 전용 예외 처리를 OSError도 포함하도록 확장
     변경 전: except json.JSONDecodeError as exc:
     변경 후: except (json.JSONDecodeError, OSError) as exc:
   
   - 줄 146 주변: report_payload = _load_report_payload(report_ref) 호출에 OSError 예외 처리 추가
     추가 내용:
     try:
         report_payload = _load_report_payload(report_ref)
     except OSError as exc:
         logger.error("보고서 파일 읽기 오류: %s (%s)", report_ref, exc)
         move_to_failed(file_path)
         continue

4. 검증 방법
   1. 테스트 파일 준비: data/queue/verdicts/ 디렉터리에 테스트용 verdict JSON 파일 생성
   2. 파일 접근 차단: 테스트 파일의 읽기 권한 제거 (chmod 000) 또는 파일 삭제 시뮬레이션
   3. worker 실행: scripts/queue_worker.py 실행 후 로그 확인
   4. 기대 결과: 
      - "보고서 파일 읽기 오류" 또는 "JSON 파싱 실패 또는 파일 읽기 오류" 로그 출력
      - 문제가 있는 파일이 failed 디렉터리로 이동됨
      - worker가 crash하지 않고 계속 실행됨
   5. 복구 테스트: 파일 권한 복원 후 정상 처리되는지 확인