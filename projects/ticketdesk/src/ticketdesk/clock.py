from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
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


def age_minutes(created_at: str, now: str) -> int:
    delta = parse_dt(now) - parse_dt(created_at)
    return max(0, int(delta.total_seconds() // 60))


def sla_remaining_minutes(created_at: str, now: str, sla_minutes: int) -> int:
    return sla_minutes - age_minutes(created_at, now)


def is_night_or_weekend(now: str) -> bool:
    dt = parse_dt(now)
    if dt.weekday() >= 5:
        return True
    return dt.hour < 9 or dt.hour >= 18


def l2_on_duty(now: str, roster: dict[str, Any] | None) -> dict[str, Any] | None:
    """名册里有人且当前落在班次才返回；否则空。夜间不得虚构值班人。"""
    if not roster or is_night_or_weekend(now):
        return None
    dt = parse_dt(now)
    weekday = dt.weekday() + 1  # 1=周一
    for shift in roster.get("l2") or []:
        days = shift.get("weekdays") or [1, 2, 3, 4, 5]
        if weekday not in days:
            continue
        start = _hm(shift.get("from") or "09:00")
        end = _hm(shift.get("to") or "18:00")
        cur = dt.hour * 60 + dt.minute
        if start <= cur < end:
            return {"name": shift.get("name") or "二线", "shift": shift}
    return None


def _hm(text: str) -> int:
    hour, _, minute = text.partition(":")
    return int(hour) * 60 + int(minute or 0)


def within_minutes(a: str, b: str, window: int) -> bool:
    return abs((parse_dt(a) - parse_dt(b)).total_seconds()) <= window * 60


def days_between(start: str, end: str) -> int:
    return (parse_dt(end).date() - parse_dt(start).date()).days


def plus_minutes(stamp: str, minutes: int) -> str:
    return (parse_dt(stamp) + timedelta(minutes=minutes)).isoformat()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).astimezone(SHANGHAI).isoformat()
