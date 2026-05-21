from __future__ import annotations


def classify_conversation(text: str) -> dict:
    """
    Classify conversation text into planning layers and extract suggested plans.
    """
    text_lower = text.lower()
    rules = [
        {
            "layer": "today",
            "bucket": "today",
            "keywords": ["오늘", "지금", "당장", "today"],
            "weight": 5,
        },
        {
            "layer": "short_term",
            "bucket": "short_term",
            "keywords": ["이번 주", "다음 주", "short"],  # '주간' 제거: '매주 + 주간' 충돌 시 recurring 우선
            "weight": 4,
        },
        {
            "layer": "long_term",
            "bucket": "long_term",
            "keywords": ["장기", "후반", "long"],
            "weight": 3,
        },
        {
            "layer": "recurring",
            "bucket": "recurring",
            "keywords": ["매주", "반복", "정기", "매월", "recurring"],
            "weight": 3,
        },
        {
            "layer": "dated",
            "bucket": "dated",
            "keywords": ["기한", "마감", "까지", "due", "deadline"],
            "weight": 4,
        },
        {
            "layer": "hold",
            "bucket": "hold",
            "keywords": ["보류", "대기", "hold", "waiting"],
            "weight": 2,
        },
        {
            "layer": "project",
            "bucket": "short_term",
            "keywords": ["프로젝트", "project"],
            "weight": 2,
        },
        {
            "layer": "philosophy",
            "bucket": "long_term",
            "keywords": [
                "철학",
                "아이디어",
                "방향",
                "principle",
                "philosophy",
                "체제",
                "책임",
                "판단",
                "작업",
                "운영",
                "체계",
            ],
            "weight": 1,
        },
    ]

    scored = []
    for rule in rules:
        hits = sum(1 for keyword in rule["keywords"] if keyword in text_lower)
        if hits:
            # (스코어, -weight, 인덱스, rule) 순서로 저장하여 동점 시 먼저 나온 규칙이 선택되도록 함
            scored.append((hits * rule["weight"], -rule["weight"], rules.index(rule), rule))

    if scored:
        _, _, _, best = max(scored)
        layer = best["layer"]
        bucket = best["bucket"]
    else:
        layer = "short_term"
        bucket = "short_term"

    title = text.split("\n")[0][:100]

    return {
        "layer": layer,
        "bucket": bucket,
        "title": title,
        "description": text[:500],
        "suggested_plans": [
            {
                "title": title,
                "bucket": bucket,
                "description": text[:500],
                "priority_score": 50,
            }
        ],
    }


def parse_quick_input(text: str) -> dict:
    """Parse Korean/English quick input into normalized plan candidates."""
    import re
    from datetime import datetime

    bucket_aliases = {
        "today": {
            "오늘",
            "today",
            "지금",
            "당장",
            "오늘 할 일",
            "오늘 우선",
            "today tasks",
        },
        "dated": {
            "기한",
            "마감",
            "due",
            "deadline",
            "기한 일정",
            "마감 일정",
        },
        "hold": {
            "보류",
            "대기",
            "hold",
            "waiting",
            "임시 보류",
        },
        "short_term": {
            "단기",
            "단기 플랜",
            "단기플랜",
            "short term",
            "short-term",
            "이번 주",
            "이번주",
            "오늘 후 단기",
        },
        "long_term": {
            "장기",
            "long term",
            "long-term",
            "중장기",
        },
        "recurring": {
            "반복",
            "정기",
            "매일",
            "매주",
            "매월",
            "recurring",
        },
    }

    bucket_order = ["today", "dated", "hold", "short_term", "long_term", "recurring"]
    sections = {bucket: [] for bucket in bucket_order}

    bullet_pattern = re.compile(r"^\s*[-*•·]\s*")
    section_pattern = re.compile(r"\s*[:：]\s*$")
    date_pattern = re.compile(r"(?<!\d)(\d{1,2})\s*[/.-]\s*(\d{1,2})(?!\d)")
    time_pattern = re.compile(r"(\d{1,2})\s*시")

    urgent_keywords = [
        "오늘",
        "지금",
        "당장",
        "긴급",
        "급",
        "urgent",
        "asap",
        "마감",
        "기한",
    ]
    actionable_keywords = [
        "문의",
        "확인",
        "통화",
        "연락",
        "체크",
        "보내기",
        "작성",
        "준비",
        "제출",
        "reply",
        "call",
        "email",
        "send",
        "check",
        "verify",
    ]

    def normalize_header(line: str) -> str | None:
        normalized = section_pattern.sub("", line.strip()).lower()
        normalized = re.sub(r"\s+", " ", normalized)
        for bucket, aliases in bucket_aliases.items():
            if normalized in {alias.lower() for alias in aliases}:
                return bucket
        return None

    current_bucket = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        bucket = normalize_header(line)
        if bucket:
            current_bucket = bucket
            continue

        item = bullet_pattern.sub("", line).strip()
        if not item:
            continue

        if current_bucket is None:
            current_bucket = "today"
        sections[current_bucket].append(item)

    if not any(sections.values()):
        sections["today"] = [
            bullet_pattern.sub("", line.strip())
            for line in text.splitlines()
            if line.strip()
        ]

    def estimate_priority_score(item: str, bucket: str) -> int:
        score = 50
        lowered = item.lower()

        if bucket == "today":
            score += 20
        elif bucket == "dated":
            score += 10
        elif bucket == "short_term":
            score += 5
        elif bucket == "hold":
            score -= 25
        elif bucket == "long_term":
            score -= 5

        if any(keyword in lowered for keyword in urgent_keywords):
            score += 15
        if any(keyword in lowered for keyword in actionable_keywords):
            score += 10
        if date_pattern.search(item):
            score += 8
        if time_pattern.search(item):
            score += 10
        if len(item) <= 24:
            score += 4

        return max(0, min(100, score))

    def extract_due_date(item: str) -> str | None:
        now = datetime.now()
        date_match = date_pattern.search(item)
        if date_match:
            month, day = int(date_match.group(1)), int(date_match.group(2))
            year = now.year if month >= now.month else now.year + 1
            return f"{year}-{month:02d}-{day:02d}"

        time_match = time_pattern.search(item)
        if time_match:
            hour = int(time_match.group(1))
            return f"{now.year}-{now.month:02d}-{now.day:02d}T{hour:02d}:00"

        return None

    candidates = []
    all_items = []

    for bucket in bucket_order:
        for item in sections[bucket]:
            priority_score = estimate_priority_score(item, bucket)
            candidate = {
                "title": item,
                "bucket": bucket,
                "description": f"[{bucket}] {item}",
                "priority_score": priority_score,
            }
            if bucket == "dated":
                due_date = extract_due_date(item)
                if due_date:
                    candidate["due_date"] = due_date

            candidates.append(candidate)
            all_items.append((item, bucket, priority_score))

    candidates.sort(key=lambda item: item["priority_score"], reverse=True)

    today_items = [(i, b, p) for i, b, p in all_items if b == "today"]
    dated_items = [(i, b, p) for i, b, p in all_items if b == "dated"]
    hold_items = [(i, b, p) for i, b, p in all_items if b == "hold"]

    main_mission = None
    if today_items:
        title, bucket, score = today_items[0]
        main_mission = {
            "title": title,
            "bucket": bucket,
            "reason": "오늘 목록에서 먼저 붙잡아야 할 집중 대상 항목",
            "priority_score": score,
        }
    elif dated_items:
        title, bucket, score = max(dated_items, key=lambda item: item[2])
        main_mission = {
            "title": title,
            "bucket": bucket,
            "reason": "기한이 가까워 먼저 확인해야 하는 항목",
            "priority_score": score,
        }
    elif candidates:
        top = candidates[0]
        main_mission = {
            "title": top["title"],
            "bucket": top["bucket"],
            "reason": "우선순위가 가장 높은 항목",
            "priority_score": top["priority_score"],
        }

    current_quest = None
    actionable_items = [
        (i, b, p)
        for i, b, p in all_items
        if any(keyword in i.lower() for keyword in actionable_keywords)
    ]
    if actionable_items:
        title, bucket, score = max(actionable_items, key=lambda item: item[2])
        current_quest = {
            "title": title,
            "bucket": bucket,
            "reason": "지금 바로 실행 가능한 다음 행동",
            "priority_score": score,
        }
    elif today_items:
        title, bucket, score = today_items[0]
        current_quest = {
            "title": title,
            "bucket": bucket,
            "reason": "오늘 항목 중 먼저 착수할 후보",
            "priority_score": score,
        }
    elif candidates:
        top = candidates[0]
        current_quest = {
            "title": top["title"],
            "bucket": top["bucket"],
            "reason": "현재 목록에서 가장 먼저 잡을 수 있는 항목",
            "priority_score": top["priority_score"],
        }

    return {
        "candidates": candidates,
        "main_mission": main_mission,
        "current_quest": current_quest,
        "summary": {
            "today_count": len(today_items),
            "dated_count": len(dated_items),
            "hold_count": len(hold_items),
            "total_count": len(candidates),
        },
    }
