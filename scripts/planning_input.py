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
            "keywords": ["\uc624\ub298", "\uc9c0\uae08", "\ub2f9\uc7a5", "today"],
            "weight": 5,
        },
        {
            "layer": "short_term",
            "bucket": "short_term",
            "keywords": ["\uc774\ubc88 \uc8fc", "\uc8fc\uac04", "\ub2e4\uc74c \uc8fc", "short"],
            "weight": 4,
        },
        {
            "layer": "long_term",
            "bucket": "long_term",
            "keywords": ["\uc7a5\uae30", "\ud6c4\ubc18", "long"],
            "weight": 3,
        },
        {
            "layer": "recurring",
            "bucket": "recurring",
            "keywords": ["\ub9e4\uc8fc", "\ubc18\ubcf5", "\uc815\uae30", "\ub9e4\uc6d4", "recurring"],
            "weight": 3,
        },
        {
            "layer": "project",
            "bucket": "short_term",
            "keywords": ["\ud504\ub85c\uc81d\ud2b8", "project"],
            "weight": 2,
        },
        {
            "layer": "philosophy",
            "bucket": "long_term",
            "keywords": [
                "\ucca0\ud559",
                "\uc544\uc774\ub514\uc5b4",
                "\ubc29\ud5a5",
                "principle",
                "philosophy",
                "\uccb4\uc81c",
                "\ucc45\uc784",
                "\ud310\ub2e8",
                "\uc791\uc5c5",
                "\uc6b4\uc601",
                "\uccb4\uacc4",
            ],
            "weight": 1,
        },
    ]

    scored = []
    for rule in rules:
        hits = sum(1 for keyword in rule["keywords"] if keyword in text_lower)
        if hits:
            scored.append((hits * rule["weight"], -rule["weight"], rule))

    if scored:
        _, _, best = max(scored)
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
            "\uc624\ub298",
            "today",
            "\uc9c0\uae08",
            "\ub2f9\uc7a5",
            "\uc624\ub298 \ud560 \uc77c",
            "\uc624\ub298 \uc6b0\uc120",
            "today tasks",
        },
        "dated": {
            "\uae30\ud55c",
            "\ub9c8\uac10",
            "due",
            "deadline",
            "\uae30\ud55c \uc77c\uc815",
            "\ub9c8\uac10 \uc77c\uc815",
        },
        "hold": {
            "\ubcf4\ub958",
            "\ub300\uae30",
            "hold",
            "waiting",
            "\uc784\uc2dc \ubcf4\ub958",
        },
        "short_term": {
            "\ub2e8\uae30",
            "\ub2e8\uae30 \ud50c\ub79c",
            "\ub2e8\uae30\ud50c\ub79c",
            "short term",
            "short-term",
            "\uc774\ubc88 \uc8fc",
            "\uc774\ubc88\uc8fc",
            "\uc624\ub298 \ud6c4 \ub2e8\uae30",
        },
        "long_term": {
            "\uc7a5\uae30",
            "long term",
            "long-term",
            "\uc911\uc7a5\uae30",
        },
        "recurring": {
            "\ubc18\ubcf5",
            "\uc815\uae30",
            "\ub9e4\uc77c",
            "\ub9e4\uc8fc",
            "\ub9e4\uc6d4",
            "recurring",
        },
    }

    bucket_order = ["today", "dated", "hold", "short_term", "long_term", "recurring"]
    sections = {bucket: [] for bucket in bucket_order}

    bullet_pattern = re.compile(r"^\s*[-*\u2022\u00b7]\s*")
    section_pattern = re.compile(r"\s*[:\uff1a]\s*$")
    date_pattern = re.compile(r"(?<!\d)(\d{1,2})\s*[/.-]\s*(\d{1,2})(?!\d)")
    time_pattern = re.compile(r"(\d{1,2})\s*\uc2dc")

    urgent_keywords = [
        "\uc624\ub298",
        "\uc9c0\uae08",
        "\ub2f9\uc7a5",
        "\uae34\uae09",
        "\uae09",
        "urgent",
        "asap",
        "\ub9c8\uac10",
        "\uae30\ud55c",
    ]
    actionable_keywords = [
        "\ubb38\uc758",
        "\ud655\uc778",
        "\ud1b5\ud654",
        "\uc5f0\ub77d",
        "\uccb4\ud06c",
        "\ubcf4\ub0b4\uae30",
        "\uc791\uc131",
        "\uc900\ube44",
        "\uc81c\ucd9c",
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
            "reason": "\uc624\ub298 \ubaa9\ub85d\uc5d0\uc11c \uba3c\uc800 \ubd99\uc7a1\uc544\uc57c \ud560 \uc9d1\uc911 \ub300\uc0c1 \ud56d\ubaa9",
            "priority_score": score,
        }
    elif dated_items:
        title, bucket, score = max(dated_items, key=lambda item: item[2])
        main_mission = {
            "title": title,
            "bucket": bucket,
            "reason": "\uae30\ud55c\uc774 \uac00\uae4c\uc6cc \uba3c\uc800 \ud655\uc778\ud574\uc57c \ud558\ub294 \ud56d\ubaa9",
            "priority_score": score,
        }
    elif candidates:
        top = candidates[0]
        main_mission = {
            "title": top["title"],
            "bucket": top["bucket"],
            "reason": "\uc6b0\uc120\uc21c\uc704\uac00 \uac00\uc7a5 \ub192\uc740 \ud56d\ubaa9",
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
            "reason": "\uc9c0\uae08 \ubc14\ub85c \uc2e4\ud589 \uac00\ub2a5\ud55c \ub2e4\uc74c \ud589\ub3d9",
            "priority_score": score,
        }
    elif today_items:
        title, bucket, score = today_items[0]
        current_quest = {
            "title": title,
            "bucket": bucket,
            "reason": "\uc624\ub298 \ud56d\ubaa9 \uc911 \uba3c\uc800 \ucc29\uc218\ud560 \ud6c4\ubcf4",
            "priority_score": score,
        }
    elif candidates:
        top = candidates[0]
        current_quest = {
            "title": top["title"],
            "bucket": top["bucket"],
            "reason": "\ud604\uc7ac \ubaa9\ub85d\uc5d0\uc11c \uac00\uc7a5 \uba3c\uc800 \uc7a1\uc744 \uc218 \uc788\ub294 \ud56d\ubaa9",
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
