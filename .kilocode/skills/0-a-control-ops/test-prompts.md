# 0-a-control-ops 테스트 프롬프트

## 워크플로우 1: 현재 상태 요약

```
0-a-control 열어서 현재 메인 미션이랑 현재 퀘스트 요약해줘
```

**기대 결과:**
- API `/api/current-state` 호출
- `main_mission_title`, `current_quest_title`, `main_mission_reason` 출력
- 한국어 5줄 이내 요약

---

## 워크플로우 2: 완료 탭 요약

```
0-a-control에서 오늘 뭐 완료했는지 확인해줘
```

**기대 결과:**
- API `/api/current-state` 호출
- `today_done_quests`, `recent_verdict`, `day_progress_summary` 출력
- 완료 항목 목록 또는 "없음" 표시

---

## 워크플로우 3: Quick Input 제출

```
0-a-control quick input에 "스킬 검증 테스트 입력입니다" 넣어줘
```

**기대 결과:**
- `POST /api/bridge/quick-input` 호출
- 제출 성공/실패 여부 출력
- 성공 시 "입력 내용: ..." + "제출 결과: 성공"
