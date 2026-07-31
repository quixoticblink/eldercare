"""M-USERS · when a kaki can work, and whether that covers a given visit.

Two layers, deliberately:
  1. weekly_slots  — the normal week, e.g. {"Tue": ["morning"], "Sat": ["morning","afternoon"]}
  2. exceptions    — dated overrides. available=FALSE is a day off; available=TRUE
                     is an extra slot outside the usual pattern.

Exceptions always win over the weekly pattern for that date.

This module answers "is this kaki free?" — it never blocks anything. The
coordinator can still assign an unavailable kaki (an urgent case may warrant a
phone call), the matching screen just flags it.
"""
import datetime, re
from .. import config, db

_WEEKDAY = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def parse_date(value: str) -> datetime.date | None:
    """Visits store dates loosely ('today', 'tomorrow', '2026-08-04')."""
    if not value:
        return None
    v = value.strip().lower()
    today = datetime.date.today()
    if v == "today":
        return today
    if v == "tomorrow":
        return today + datetime.timedelta(days=1)
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", v)
    if m:
        try:
            return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    return None

def half_day_for_window(window: str) -> str | None:
    """Map a visit's time window to a half-day. Returns None when unknowable."""
    if not window:
        return None
    w = window.strip().lower()
    if "within the hour" in w:                      # urgent — right now
        return "morning" if datetime.datetime.now().hour < 13 else "afternoon"
    for word, half in (("morning", "morning"), ("am", "morning"),
                       ("afternoon", "afternoon"), ("pm", "afternoon"),
                       ("evening", "afternoon")):
        if word in w:
            return half
    m = re.match(r"^\s*(\d{1,2})", w)                # "14:00–17:00"
    if m:
        hour = int(m.group(1))
        if 0 <= hour <= 23:
            return "morning" if hour < 13 else "afternoon"
    return None

def weekly(user_id: str) -> dict:
    p = db.one("SELECT weekly_slots FROM kaki_profiles WHERE user_id = ?", [user_id]) or {}
    raw = p.get("weekly_slots") or "{}"
    try:
        import json
        data = json.loads(raw)
    except Exception:
        data = {}
    return {d: [h for h in (data.get(d) or []) if h in config.HALF_DAYS] for d in _WEEKDAY}

def exceptions(user_id: str) -> list[dict]:
    return db.q("""SELECT id, date, half_day, available, note FROM availability_exceptions
                   WHERE user_id = ? ORDER BY date""", [user_id])

def summary(user_id: str) -> dict:
    w = weekly(user_id)
    p = db.one("SELECT availability_note FROM kaki_profiles WHERE user_id = ?", [user_id]) or {}
    return {"weekly": w, "exceptions": exceptions(user_id),
            "note": p.get("availability_note") or "",
            "half_day_windows": _windows(),
            "any_set": any(w.values())}

def _windows() -> dict:
    from .. import assumptions
    return assumptions.half_day_windows()

def check(user_id: str, date_str: str, window: str) -> dict:
    """→ {'state': 'available'|'unavailable'|'unknown', 'why': str}

    'unknown' matters: a kaki who has never filled in availability must not be
    shown as unavailable, or the coordinator would stop offering them work.
    """
    d = parse_date(date_str)
    half = half_day_for_window(window)
    w = weekly(user_id)

    if not any(w.values()):
        return {"state": "unknown", "why": "hasn't set availability yet"}
    if d is None:
        return {"state": "unknown", "why": "visit date isn't a fixed day"}

    iso = d.isoformat()
    day_name = _WEEKDAY[d.weekday()]

    # Dated exceptions override the weekly pattern.
    for e in db.q("""SELECT half_day, available, note FROM availability_exceptions
                     WHERE user_id = ? AND date = ?""", [user_id, iso]):
        covers = e["half_day"] == "all" or half is None or e["half_day"] == half
        if covers:
            if not e["available"]:
                return {"state": "unavailable", "why": e.get("note") or f"marked off on {iso}"}
            return {"state": "available", "why": f"extra slot on {iso}"}

    slots = w.get(day_name) or []
    if not slots:
        return {"state": "unavailable", "why": f"doesn't normally work {day_name}"}
    if half is None:
        return {"state": "available", "why": f"works {day_name} ({', '.join(slots)})"}
    if half in slots:
        return {"state": "available", "why": f"{day_name} {half}"}
    return {"state": "unavailable", "why": f"{day_name} but only {', '.join(slots)}"}
