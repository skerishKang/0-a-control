from datetime import datetime, timedelta, time, timezone
import re

def parse_time_range(time_str: str) -> tuple[datetime, datetime]:
    """
    Parses time range strings like '6h', '1d', 'today-morning', '09:00-11:00'.
    Returns (start_time, end_time) in UTC.
    """
    now = datetime.now(timezone.utc)
    # Project assumes Asia/Seoul for local relative terms if needed, 
    # but for simplicity we use UTC for calculations unless specified.
    # For now, let's keep it consistent with the system's UTC assumption.
    
    today = now.date()
    
    # 1. '6h', '1d'
    match = re.match(r"^(\d+)([hd])$", time_str.strip().lower())
    if match:
        value, unit = int(match.group(1)), match.group(2)
        if unit == 'h': return now - timedelta(hours=value), now
        if unit == 'd': return now - timedelta(days=value), now

    # 2. 'today-...'
    if time_str == "today-morning": return datetime.combine(today, time(6, 0)).replace(tzinfo=timezone.utc), datetime.combine(today, time(12, 0)).replace(tzinfo=timezone.utc)
    if time_str == "today-afternoon": return datetime.combine(today, time(12, 0)).replace(tzinfo=timezone.utc), datetime.combine(today, time(18, 0)).replace(tzinfo=timezone.utc)
    if time_str == "today-evening": return datetime.combine(today, time(18, 0)).replace(tzinfo=timezone.utc), datetime.combine(today, time(23, 59, 59)).replace(tzinfo=timezone.utc)
    
    # 3. '09:00-11:00' (today)
    match = re.match(r"^(\d{2}:\d{2})-(\d{2}:\d{2})$", time_str.strip())
    if match:
        start_t = datetime.strptime(match.group(1), "%H:%M").time()
        end_t = datetime.strptime(match.group(2), "%H:%M").time()
        return datetime.combine(today, start_t).replace(tzinfo=timezone.utc), datetime.combine(today, end_t).replace(tzinfo=timezone.utc)

    # 4. '2026-03-09 09:00-11:00'
    match = re.match(r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})-(\d{2}:\d{2})$", time_str.strip())
    if match:
        date_part = match.group(1)
        start_dt = datetime.strptime(f"{date_part} {match.group(2)}", "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        end_dt = datetime.strptime(f"{date_part} {match.group(3)}", "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        return start_dt, end_dt

    # Fallback/Default
    return now - timedelta(hours=6), now

def resolve_source_aliases(aliases: list[str]) -> list[str]:
    """
    Maps user-friendly names to actual source_id or chat_class.
    """
    mapping = {
        "self": "self_chat", "나": "self_chat", "나랑챗": "self_chat",
        "강혜림": "kang_hyerim_chat", "강혜림 대화": "kang_hyerim_chat",
        "kilo": "kilo_chat", "로컬챗": "local_chat",
        "주식큐레이터": "stock_curator_channel",
        "뉴스": "news_channel"
    }
    core_four = ['local_chat', 'kilo_chat', 'self_chat', 'kang_hyerim_chat']
    
    resolved = []
    for alias in (aliases or []):
        if alias == "핵심4개":
            resolved.extend(core_four)
        elif alias in mapping:
            resolved.append(mapping[alias])
        else:
            resolved.append(alias)
    return list(set(resolved))
