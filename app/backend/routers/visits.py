"""M-VISITS · request → assigned → accepted → in_progress → completed, reports, care notes."""
import datetime, random, re
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from .. import assumptions, config, db, security, settings
from ..services import matching, notify

router = APIRouter(prefix="/visits", tags=["visits"])

class VisitIn(BaseModel):
    service: str
    tier: str
    date: str          # "2026-07-22" or "today"
    window: str        # "14:00–17:00" / "within the hour"
    language: str | None = None        # legacy single value
    languages: list[str] | None = None # v1.6: several; first one becomes `language`
    notes: str | None = ""
    trigger: str | None = ""   # urgent/soon path: what happened

class StartIn(BaseModel):
    otp: str

class ReportIn(BaseModel):
    chips: list[str] = []
    text: str = ""
    meds_confirmed: bool = False

class NoteIn(BaseModel):
    chips: list[str] = []
    text: str = ""

def _now() -> datetime.datetime:
    """Wall clock, as a function so tests can pin it."""
    return datetime.datetime.now()

def window_end_hour(window: str) -> int | None:
    """End hour (0-23) of a preset window like 'Afternoon 2–5', 'Today, 6–9pm',
    'Morning 9–12'. None for relative windows ('Within the hour') or free text.
    Bare numbers 1–8 read as pm; 9–12 as am; 'pm' forces pm."""
    if not window:
        return None
    m = re.search(r"(\d{1,2})\s*[–\-]\s*(\d{1,2})\s*(am|pm)?", window.lower())
    if not m:
        return None
    end, ampm = int(m.group(2)), m.group(3)
    if ampm == "pm" and end < 12:
        end += 12
    elif ampm is None and 1 <= end <= 8:
        end += 12
    return end if 0 <= end <= 23 else None

def _window_has_passed(date: str, window: str) -> bool:
    """True when the visit is for today and its window already ended.
    Seniors were offered 'Today, 2–5pm' for an urgent visit at 6pm (21 Aug)."""
    now = _now()
    if (date or "").strip().lower() not in ("today", now.date().isoformat()):
        return False
    end = window_end_hour(window)
    return end is not None and now.hour >= end

def _estimate(service: str) -> dict | None:
    """Pilot price stack. Every number comes from assumptions.json — see that
    file for the source behind each figure. Presentational only; billing runs
    through the Vanguard / ICCP account during the pilot."""
    m = assumptions.service(service)
    if not m:
        return None
    hours = m.get("hours", assumptions.default_hours())
    rate = m.get("family_rate_per_hour", 0)
    base = hours * rate
    subsidy = round(base * assumptions.subsidy_pct("community_care_fund_pct"))
    foundation = round(base * assumptions.subsidy_pct("foundation_topup_pct"))
    return {"hours": hours, "rate": rate, "base": base,
            "subsidy": subsidy, "foundation": foundation,
            "family_pays": base - subsidy - foundation,
            "kaki_fee": hours * m.get("kaki_rate_per_hour", 0),
            "transport": assumptions.transport_allowance(),
            "illustrative": True,
            "disclaimer": assumptions.disclaimer()["short"]}

def _parties(v: dict) -> tuple[dict | None, dict | None, str]:
    """(kaki, caregiver, senior_name) for notifications."""
    kaki = db.one("SELECT * FROM users WHERE id = ?", [v["kaki_id"]]) if v.get("kaki_id") else None
    cg = db.one("SELECT * FROM users WHERE id = ?", [v["caregiver_id"]])
    h = db.one("SELECT senior_name FROM households WHERE id = ?", [v["household_id"]]) or {}
    return kaki, cg, h.get("senior_name") or ""

def _enrich(v: dict) -> dict:
    h = db.one("SELECT * FROM households WHERE id = ?", [v["household_id"]]) or {}
    kaki = db.one("SELECT id, name, email, phone FROM users WHERE id = ?", [v["kaki_id"]]) if v.get("kaki_id") else None
    times_together = 0
    if kaki:
        kp = db.one("SELECT tier FROM kaki_profiles WHERE user_id = ?", [kaki["id"]]) or {}
        kaki["tier"] = kp.get("tier", 1)
        prof = db.one("SELECT languages FROM kaki_profiles WHERE user_id = ?", [kaki["id"]]) or {}
        kaki["languages"] = db.uj(prof.get("languages"))
        times_together = db.q("""SELECT count(*) c FROM visits
                                 WHERE kaki_id = ? AND household_id = ? AND status = 'completed'""",
                              [kaki["id"], v["household_id"]])[0]["c"]
    cg = db.one("SELECT id, name, email FROM users WHERE id = ?", [v["caregiver_id"]]) or {}
    report = db.one("SELECT * FROM visit_reports WHERE visit_id = ?", [v["id"]])
    if report:
        report["chips"] = db.uj(report.get("chips"))
    plan = db.one("SELECT * FROM care_plans WHERE household_id = ?", [v["household_id"]])
    if plan:
        plan["languages"] = db.uj(plan.get("languages"))
    langs = db.uj(v.get("languages")) or ([v["language"]] if v.get("language") else [])
    return {**v, "window": v.get("time_window"), "trigger": v.get("crisis_trigger") or "",
            "languages": langs,
            "senior_name": h.get("senior_name"), "senior_age": h.get("senior_age"),
            "address": h.get("address"), "kaki": kaki, "caregiver": cg,
            "times_together": times_together, "estimate": _estimate(v.get("service")),
            "report": report, "care_plan": plan}

@router.post("")
def create(body: VisitIn, user=Depends(security.current_user)):
    security.approved_user(user)
    security.require_role(user, "caregiver")
    if body.service not in config.SERVICES:
        raise HTTPException(400, "That service isn't bookable yet")
    if body.tier not in config.TIERS:
        raise HTTPException(400, "Pick an urgency")
    if _window_has_passed(body.date, body.window):
        raise HTTPException(400, "That window has passed — pick a later one")
    horizon = int(settings.get("max_advance_days") or 30)
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", (body.date or "").strip())
    if m:
        try:
            d = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            raise HTTPException(400, "Use a real date")
        if d < _now().date():
            raise HTTPException(400, "That date has passed")
        if (d - _now().date()).days > horizon:
            raise HTTPException(400, f"Bookings open up to {horizon} days ahead — pick an earlier date")
    langs = [l for l in (body.languages or []) if l in config.LANGUAGES]
    if not langs and body.language:
        langs = [body.language]
    if not langs:
        raise HTTPException(400, "Pick at least one language")
    language = langs[0]
    h = db.one("SELECT * FROM households WHERE caregiver_id = ?", [user["id"]])
    if not h:
        raise HTTPException(400, "Set up your household and care plan first")
    vid = db.new_id()
    otp = f"{random.randint(0, 9999):04d}"
    db.run("""INSERT INTO visits(id, household_id, caregiver_id, service, tier, date, time_window, language, languages, notes, otp_code, crisis_trigger)
              VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
           [vid, h["id"], user["id"], body.service, body.tier, body.date, body.window,
            language, db.j(langs), body.notes or "", otp, body.trigger or ""])
    db.audit(user["email"] or user["phone"], "visit_requested", f"{vid} {body.service} {body.tier}")

    # Auto-matching, when the coordinator has switched it on. It only ever picks
    # a kaki whose availability positively covers the visit; anything it cannot
    # fill stays 'requested' for a human rather than being forced onto someone.
    if settings.get("auto_match"):
        try:
            matching.try_auto_assign(vid, "auto-match")
        except Exception as e:
            print(f"[kakis] auto-match failed for {vid}: {e}")   # booking still stands

    return _enrich(db.one("SELECT * FROM visits WHERE id = ?", [vid]))

@router.get("")
def list_visits(user=Depends(security.current_user)):
    security.approved_user(user)
    if user["role"] == "caregiver":
        rows = db.q("SELECT * FROM visits WHERE caregiver_id = ? ORDER BY created_at DESC", [user["id"]])
    elif user["role"] == "kaki":
        rows = db.q("SELECT * FROM visits WHERE kaki_id = ? ORDER BY created_at DESC", [user["id"]])
    else:  # admin
        rows = db.q("SELECT * FROM visits ORDER BY created_at DESC")
    return [_enrich(v) for v in rows]

@router.get("/{vid}")
def get_visit(vid: str, user=Depends(security.current_user)):
    security.approved_user(user)
    v = db.one("SELECT * FROM visits WHERE id = ?", [vid])
    if not v:
        raise HTTPException(404, "Visit not found")
    if user["role"] != "admin" and user["id"] not in (v["caregiver_id"], v.get("kaki_id")):
        raise HTTPException(403, "Not your visit")
    out = _enrich(v)
    if user["role"] == "kaki":
        out.pop("otp_code", None)   # kaki gets the code from the senior/caregiver in person
    return out

def _transition(vid, user, allowed_roles, from_states, to_state, stamp_col=None):
    v = db.one("SELECT * FROM visits WHERE id = ?", [vid])
    if not v:
        raise HTTPException(404, "Visit not found")
    if user["role"] not in allowed_roles and user["role"] != "admin":
        raise HTTPException(403, "Not allowed")
    if user["role"] == "kaki" and v.get("kaki_id") != user["id"]:
        raise HTTPException(403, "Not your visit")
    if user["role"] == "caregiver" and v["caregiver_id"] != user["id"]:
        raise HTTPException(403, "Not your visit")
    if v["status"] not in from_states:
        raise HTTPException(400, f"Can't do that — visit is {v['status']}")
    stamp = f", {stamp_col} = current_timestamp" if stamp_col else ""
    db.run(f"UPDATE visits SET status = ?{stamp} WHERE id = ?", [to_state, vid])
    db.audit(user["email"], f"visit_{to_state}", vid)
    return db.one("SELECT * FROM visits WHERE id = ?", [vid])

@router.post("/{vid}/accept")
def accept(vid: str, user=Depends(security.current_user)):
    security.approved_user(user)
    v = _transition(vid, user, ["kaki"], ["assigned"], "accepted", "accepted_at")
    notify.visit_accepted(v, *_parties(v))
    return _enrich(v)

@router.post("/{vid}/decline")
def decline(vid: str, user=Depends(security.current_user)):
    security.approved_user(user)
    v = _transition(vid, user, ["kaki"], ["assigned"], "requested")
    kaki, cg, senior = _parties(v)          # before the kaki is cleared
    db.run("UPDATE visits SET kaki_id = NULL, assigned_at = NULL WHERE id = ?", [vid])
    notify.visit_declined(v, kaki, cg, senior)
    return _enrich(db.one("SELECT * FROM visits WHERE id = ?", [vid]))

@router.post("/{vid}/on-the-way")
def on_the_way(vid: str, user=Depends(security.current_user)):
    """Kaki only, once accepted. Stamps on_way_at and tells the caregiver.
    Re-pressing is harmless: the first stamp stays."""
    security.approved_user(user)
    security.require_role(user, "kaki")
    v = db.one("SELECT * FROM visits WHERE id = ?", [vid])
    if not v:
        raise HTTPException(404, "Visit not found")
    if v.get("kaki_id") != user["id"]:
        raise HTTPException(403, "Not your visit")
    if v["status"] != "accepted":
        raise HTTPException(400, "Accept the visit first")
    if not v.get("on_way_at"):
        db.run("UPDATE visits SET on_way_at = current_timestamp WHERE id = ?", [vid])
        db.audit(user["email"] or user["phone"], "visit_on_the_way", vid)
        v = db.one("SELECT * FROM visits WHERE id = ?", [vid])
        notify.visit_on_the_way(v, *_parties(v))
    return _enrich(v)

@router.post("/{vid}/start")
def start(vid: str, body: StartIn, user=Depends(security.current_user)):
    security.approved_user(user)
    v = db.one("SELECT * FROM visits WHERE id = ?", [vid])
    if not v:
        raise HTTPException(404, "Visit not found")
    if body.otp.strip() != v["otp_code"]:
        raise HTTPException(400, "Wrong start code — ask the family to read it from their visit page")
    v = _transition(vid, user, ["kaki"], ["accepted", "assigned"], "in_progress", "started_at")
    kaki, _cg, senior = _parties(v)
    notify.visit_started_contact(v, kaki, senior, db.one("SELECT * FROM care_plans WHERE household_id = ?", [v["household_id"]]))
    return _enrich(v)

@router.post("/{vid}/complete")
def complete(vid: str, body: ReportIn, user=Depends(security.current_user)):
    security.approved_user(user)
    v = _transition(vid, user, ["kaki"], ["in_progress"], "completed", "completed_at")
    db.run("DELETE FROM visit_reports WHERE visit_id = ?", [vid])
    db.run("INSERT INTO visit_reports(visit_id, chips, text, meds_confirmed) VALUES (?,?,?,?)",
           [vid, db.j(body.chips), body.text, body.meds_confirmed])
    kaki, _cg, senior = _parties(v)
    notify.visit_finished_contact(v, kaki, senior, db.one("SELECT * FROM care_plans WHERE household_id = ?", [v["household_id"]]))
    return _enrich(db.one("SELECT * FROM visits WHERE id = ?", [vid]))

@router.post("/{vid}/cancel")
def cancel(vid: str, user=Depends(security.current_user)):
    security.approved_user(user)
    v = _transition(vid, user, ["caregiver"], ["requested", "assigned", "accepted"], "cancelled")
    if v.get("kaki_id"):
        notify.visit_cancelled(v, "caregiver", *_parties(v))
    return _enrich(v)

@router.post("/{vid}/care-note")
def care_note(vid: str, body: NoteIn, user=Depends(security.current_user)):
    security.approved_user(user)
    v = db.one("SELECT * FROM visits WHERE id = ?", [vid])
    if not v:
        raise HTTPException(404, "Visit not found")
    if user["id"] not in (v["caregiver_id"], v.get("kaki_id")) and user["role"] != "admin":
        raise HTTPException(403, "Not your visit")
    db.run("INSERT INTO care_notes(id, household_id, visit_id, author_id, chips, text) VALUES (?,?,?,?,?,?)",
           [db.new_id(), v["household_id"], vid, user["id"], db.j(body.chips), body.text])
    db.audit(user["email"], "care_note", vid)
    return {"ok": True}
