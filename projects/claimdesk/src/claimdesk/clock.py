from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

SHANGHAI = ZoneInfo("Asia/Shanghai")


def parse_dt(value: str) -> datetime:
    text = (value or "").strip()
    if not text:
        return datetime.now(tz=SHANGHAI)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=SHANGHAI)
    return dt.astimezone(SHANGHAI)


def parse_day(value: str) -> date:
    return parse_dt(value).date()


def days_between(start: str, end: str) -> int:
    return (parse_day(end) - parse_day(start)).days
