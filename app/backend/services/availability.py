"""M-USERS · when a kaki can work, and whether that covers a given visit.

Two layers, deliberately:
  1. weekly hours — the normal week, per day, e.g.
       {"Tue": {"from": "09:00", "to": "12:00"}, "Sat": {"from": "08:00", "to": "18:00"}}
     (v1.6; the v1.3 half-day form {"Tue": ["morning"]} is still read and
     converted, morning = 08:00–13:00, afternoon = 13:00–18:00.)
  2. exceptions — dated overrides. available=FALSE is a day off; available=TRUE
     is an extra slot outside the usual pattern. Kept in half-days.

Exceptions always win over the weekly pattern for that date.

This module answers "is this kaki free?" — it never blocks anything. The
coordinator can still assign an unavailable kaki (an urgent case may warrant a
phone call), the matching screen just flags it.
"""
import datetime, json, re
from .. import config, db

_WEEKDAY = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
STEP_MINUTES = 30

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

# ---- times ------------------------------------------------------------------

def parse_hhmm(value: str) -> int | None:
    """'09:30' → 570 minutes since midnight. None if not HH:MM."""
    m = re.match(r"^\s*(\d{1,2}):(\d{2})\s*$", value or "")
    if not m:
        return None
    h, mi = int(m.group(1)), int(m.group(2))
    if not (0 <= h <= 23 and 0 <= mi <= 59):
        return None
    return h * 60 + mi

def fmt_hhmm(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"

def on_the_half_hour(minutes: int | None) -> bool:
    return minutes is not None and minutes % STEP_MINUTES == 0

def _half_windows() -> dict:
    """{'morning': (480, 780), 'afternoon': (780, 1080)} from assumptions.json."""
    from .. import assumptions
    out = {}
    for half, text in assumptions.half_day_windows().items():
        rng = window_range(text)
        out[half] = rng or ((480, 780) if half == "morning" else (780, 1080))
    return out

def window_range(window: str) -> tuple[int, int] | None:
    """A visit window as (start, end) minutes. Handles '09:30–11:30',
    'Morning 9–12', 'Afternoon 2–5', 'Today, 6–9pm', 'within the hour'."""
    if not window:
        return None
    w = window.strip().lower()
    m = re.search(r"(\d{1,2}):(\d{2})\s*[–\-]\s*(\d{1,2}):(\d{2})", w)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2)), int(m.group(3)) * 60 + int(m.group(4))
    if "within the hour" in w or "within 2 hours" in w:
        now = datetime.datetime.now()
        start = now.hour * 60 + now.minute
        return start, min(start + (60 if "hour" in w and "2" not in w else 120), 24 * 60 - 1)
    m = re.search(r"(\d{1,2})\s*(am|pm)?\s*[–\-]\s*(\d{1,2})\s*(am|pm)?", w)
    if m:
        a, b, pm = int(m.group(1)), int(m.group(3)), m.group(4)
        if pm == "pm" and b < 12:
            b += 12
        elif pm is None and 1 <= b <= 8:
            b += 12
        if a < 12 and b > 12 and a <= 8:
            a += 12
        if a >= b:
            a = b - 60
        return a * 60, b * 60
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

# ---- the weekly pattern -----------------------------------------------------

def _raw_weekly(user_id: str) -> dict:
    p = db.one("SELECT weekly_slots FROM kaki_profiles WHERE user_id = ?", [user_id]) or {}
    try:
        data = json.loads(p.get("weekly_slots") or "{}")
    except Exception:
        data = {}
    return data if isinstance(data, dict) else {}

def _to_range(value) -> tuple[int, int] | None:
    """Either shape → (start, end) minutes, or None for a day off."""
    if isinstance(value, dict):
        a, b = parse_hhmm(value.get("from", "")), parse_hhmm(value.get("to", ""))
        return (a, b) if a is not None and b is not None and a < b else None
    if isinstance(value, list):                       # v1.3 half-days
        halves = [h for h in value if h in config.HALF_DAYS]
        if not halves:
            return None
        hw = _half_windows()
        return min(hw[h][0] for h in halves), max(hw[h][1] for h in halves)
    return None

def weekly_hours(user_id: str) -> dict:
    """{'Mon': {'from': '09:00', 'to': '13:00'} | None, ...} for every weekday."""
    raw = _raw_weekly(user_id)
    out = {}
    for d in _WEEKDAY:
        rng = _to_range(raw.get(d))
        out[d] = {"from": fmt_hhmm(rng[0]), "to": fmt_hhmm(rng[1])} if rng else None
    return out

def weekly(user_id: str) -> dict:
    """The v1.3 half-day view, derived from the hours, kept for older screens
    and for the coordinator's at-a-glance badge."""
    hw = _half_windows()
    out = {}
    for d, rng in weekly_hours(user_id).items():
        halves = []
        if rng:
            a, b = parse_hhmm(rng["from"]), parse_hhmm(rng["to"])
            for h in config.HALF_DAYS:
                lo, hi = hw[h]
                if a < hi and b > lo:
                    halves.append(h)
        out[d] = halves
    return out

def exceptions(user_id: str) -> list[dict]:
    return db.q("""SELECT id, date, half_day, available, note FROM availability_exceptions
                   WHERE user_id = ? ORDER BY date""", [user_id])

def summary(user_id: str) -> dict:
    w = weekly(user_id)
    p = db.one("SELECT availability_note FROM kaki_profiles WHERE user_id = ?", [user_id]) or {}
    return {"weekly": w, "weekly_hours": weekly_hours(user_id), "exceptions": exceptions(user_id),
            "note": p.get("availability_note") or "",
            "half_day_windows": _windows(),
            "step_minutes": STEP_MINUTES,
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
    hours = weekly_hours(user_id)

    if not any(hours.values()):
        return {"state": "unknown", "why": "hasn't set availability yet"}
    if d is None:
        return {"state": "unknown", "why": "visit date isn't a fixed day"}

    iso = d.isoformat()
    day_name = _WEEKDAY[d.weekday()]
    rng = window_range(window)
    half = half_day_for_window(window)
    hw = _half_windows()

    # Dated exceptions override the weekly pattern.
    for e in db.q("""SELECT half_day, available, note FROM availability_exceptions
                     WHERE user_id = ? AND date = ?""", [user_id, iso]):
        if e["half_day"] == "all":
            covers = True
        elif rng:
            lo, hi = hw.get(e["half_day"], (0, 0))
            covers = rng[0] < hi and rng[1] > lo
        else:
            covers = half is None or e["half_day"] == half
        if covers:
            if not e["available"]:
                return {"state": "unavailable", "why": e.get("note") or f"marked off on {iso}"}
            return {"state": "available", "why": f"extra slot on {iso}"}

    day = hours.get(day_name)
    if not day:
        return {"state": "unavailable", "why": f"doesn't normally work {day_name}"}
    label = f"{day_name} {day['from']}–{day['to']}"
    if rng is None:
        return {"state": "available", "why": f"works {label}"}
    a, b = parse_hhmm(day["from"]), parse_hhmm(day["to"])
    if a <= rng[0] and rng[1] <= b:
        return {"state": "available", "why": label}
    return {"state": "unavailable", "why": f"{day_name} but only {day['from']}–{day['to']}"}
