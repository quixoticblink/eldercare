"""M-VISITS · request → assigned → accepted → in_progress → completed, reports, care notes."""
import datetime, random, re, zoneinfo
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from .. import assumptions, config, db, security, settings
from ..services import availability, matching, notify

router = APIRouter(prefix="/visits", tags=["visits"])

class VisitIn(BaseModel):
    service: str
    tier: str
    date: str          # "2026-07-22" or "today"
    window: str | None = ""   # "Afternoon 2–5" / "within the hour"; derived from the times when given
    start_time: str | None = None   # "09:30" — v1.6 exact times, 30-minute steps
    end_time: str | None = None
    language: str | None = None        # legacy single value
    languages: list[str] | None = None # v1.6: several; first one becomes `language`
    notes: str | None = ""
    trigger: str | None = Field(default="", max_length=120)   # urgent/soon path: what happened
    kaki_gender_pref: str | None = "any"   # any | female | male
    preferred_kaki_id: str | None = ""     # a kaki this household has had before

class StartIn(BaseModel):
    otp: str

class KakiCodeIn(BaseModel):
    code: str

class CancelIn(BaseModel):
    reason: str = Field(default="", max_length=300)

class ReportIn(BaseModel):
    chips: list[str] = []
    text: str = ""
    meds_confirmed: bool = False

class NoteIn(BaseModel):
    chips: list[str] = []
    text: str = ""

def _now() -> datetime.datetime:
    """Singapore wall clock (config.TZ), naive, as a function so tests can pin it."""
    try:
        return datetime.datetime.now(zoneinfo.ZoneInfo(config.TZ)).replace(tzinfo=None)
    except Exception:
        return datetime.datetime.now()

def window_end_hour(window: str) -> int | None:
    """End hour (0-23) of a preset window like 'Afternoon 2–5', 'Today, 6–9pm',
    'Morning 9–12'. None for relative windows ('Within the hour') or free text.
    Bare numbers 1–8 read as pm; 9–12 as am; 'pm' forces pm."""
    if not window:
        return None
    m = re.search(r"(\d{1,2})\s*(?:am|pm)?\s*[–\-]\s*(\d{1,2})\s*(am|pm)?", window.lower())
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
    w = (window or "").lower()
    if "within" in w:
        return False                       # relative to now, by definition
    rng = availability.window_range(window)
    if rng is None:
        end = window_end_hour(window)
        return end is not None and now.hour >= end
    return now.hour * 60 + now.minute >= rng[1]

def _hours_for(start_time: str | None, end_time: str | None, service: str) -> tuple[float, str, str, str]:
    """→ (hours, window, start, end). Exact times are validated on the half
    hour; duration rounds UP to assumptions.rounding_hours with a floor of
    assumptions.min_visit_hours. Without times, the service default applies."""
    meta = assumptions.service(service) or {}
    default = float(meta.get("hours", assumptions.default_hours()))
    if not start_time and not end_time:
        return default, "", "", ""
    a, b = availability.parse_hhmm(start_time or ""), availability.parse_hhmm(end_time or "")
    if a is None or b is None:
        raise HTTPException(400, "Times look like 09:30 — pick both a start and an end")
    if not (availability.on_the_half_hour(a) and availability.on_the_half_hour(b)):
        raise HTTPException(400, "Times go in 30-minute steps, e.g. 09:30 or 10:00")
    if b <= a:
        raise HTTPException(400, "The end time must be after the start")
    step = assumptions.rounding_hours() or 0.5
    raw = (b - a) / 60
    hours = max(assumptions.min_visit_hours(), (int(raw / step) + (1 if raw % step else 0)) * step)
    start, end = availability.fmt_hhmm(a), availability.fmt_hhmm(b)
    return float(hours), f"{start}–{end}", start, end

def _estimate(service: str, hours: float | None = None) -> dict | None:
    """Pilot price stack. Every number comes from assumptions.json — see that
    file for the source behind each figure. Presentational only; billing runs
    through the Vanguard / ICCP account during the pilot. `hours` is the
    visit's own (prorated) duration when it has exact times."""
    m = assumptions.service(service)
    if not m:
        return None
    hours = float(hours) if hours else float(m.get("hours", assumptions.default_hours()))
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

# Services where the kaki does not need the medical side of the care plan.
# Household help is chores: the kaki needs the address, mobility (so they know
# whether the senior can move out of the way), and who to call — not age,
# medications, or the family's private notes about the senior (v1.6, B2·5).
MINIMISED_SERVICES = {"Household help"}

def _minimise_for_kaki(out: dict) -> dict:
    if out.get("service") not in MINIMISED_SERVICES:
        out["minimised"] = False
        return out
    out["minimised"] = True
    out["senior_age"] = None
    plan = out.get("care_plan")
    if plan:
        out["care_plan"] = {**plan, "meds": None, "notes": None, "contacts": None}
    return out

def _out(v: dict, user: dict) -> dict:
    """Every visit response goes through here. The kaki never receives the
    start code — not on the visit page, not in the list, not in the response
    to their own accept/start/complete. SPEC §9.5. For household help the
    kaki also gets only what the task needs."""
    out = _enrich(v)
    role = user.get("role")
    if role == "kaki":
        out.pop("otp_code", None)            # never; they get it from the family in person
        out = _minimise_for_kaki(out)
    elif role == "caregiver":
        out.pop("kaki_code", None)           # they have to ask the kaki for it
        if not v.get("kaki_verified_at"):
            out.pop("otp_code", None)        # revealed only once the kaki is verified
    return out

def _enrich(v: dict) -> dict:
    h = db.one("SELECT * FROM households WHERE id = ?", [v["household_id"]]) or {}
    kaki = db.one("SELECT id, name, email, phone, photo FROM users WHERE id = ?", [v["kaki_id"]]) if v.get("kaki_id") else None
    times_together = 0
    if kaki:
        kp = db.one("SELECT tier, gender FROM kaki_profiles WHERE user_id = ?", [kaki["id"]]) or {}
        kaki["tier"] = kp.get("tier", 1)
        kaki["gender"] = kp.get("gender") or ""
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
    preferred = (db.one("SELECT id, name FROM users WHERE id = ?", [v["preferred_kaki_id"]])
                 if v.get("preferred_kaki_id") else None)
    last_cancellation = ({"by": v["cancelled_by"], "by_name": v.get("cancelled_by_name") or "",
                          "reason": v.get("cancel_reason") or "", "at": v.get("cancelled_at")}
                         if v.get("cancelled_by") else None)
    return {**v, "window": v.get("time_window"), "trigger": v.get("crisis_trigger") or "",
            "languages": langs, "preferred_kaki": preferred, "last_cancellation": last_cancellation,
            "senior_name": h.get("senior_name"), "senior_age": h.get("senior_age"),
            "address": h.get("address"), "kaki": kaki, "caregiver": cg,
            "times_together": times_together, "estimate": _estimate(v.get("service"), v.get("hours")),
            "hours": v.get("hours") or (assumptions.service(v.get("service")) or {}).get("hours"),
            "report": report, "care_plan": plan}

@router.post("")
def create(body: VisitIn, user=Depends(security.current_user)):
    security.approved_user(user)
    security.require_role(user, "caregiver")
    if body.service not in config.SERVICES:
        raise HTTPException(400, "That service isn't bookable yet")
    if body.tier not in config.TIERS:
        raise HTTPException(400, "Pick an urgency")
    hours, exact_window, start_time, end_time = _hours_for(body.start_time, body.end_time, body.service)
    window = exact_window or (body.window or "")
    if not window:
        raise HTTPException(400, "Pick a time")
    if _window_has_passed(body.date, window):
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
    gender_pref = (body.kaki_gender_pref or "any").strip().lower()
    if gender_pref not in config.GENDER_PREFS:
        raise HTTPException(400, "Kaki preference must be any, female or male")
    h = db.one("SELECT * FROM households WHERE caregiver_id = ?", [user["id"]])
    if not h:
        raise HTTPException(400, "Set up your household and care plan first")
    preferred = (body.preferred_kaki_id or "").strip()
    if preferred and preferred not in {k["id"] for k in _past_kakis(h["id"])}:
        raise HTTPException(400, "You can only ask again for a kaki who has visited before")
    vid = db.new_id()
    otp = f"{random.randint(0, 9999):04d}"
    db.run("""INSERT INTO visits(id, household_id, caregiver_id, service, tier, date, time_window, language, languages, notes, otp_code, crisis_trigger,
                                 start_time, end_time, hours, kaki_gender_pref, preferred_kaki_id)
              VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
           [vid, h["id"], user["id"], body.service, body.tier, body.date, window,
            language, db.j(langs), body.notes or "", otp, body.trigger or "",
            start_time, end_time, hours, gender_pref, preferred])
    db.audit(user["email"] or user["phone"], "visit_requested", f"{vid} {body.service} {body.tier}")

    # Auto-matching, when the coordinator has switched it on. It only ever picks
    # a kaki whose availability positively covers the visit; anything it cannot
    # fill stays 'requested' for a human rather than being forced onto someone.
    if settings.get("auto_match"):
        try:
            matching.try_auto_assign(vid, "auto-match")
        except Exception as e:
            print(f"[kakis] auto-match failed for {vid}: {e}")   # booking still stands

    return _out(db.one("SELECT * FROM visits WHERE id = ?", [vid]), user)

@router.get("")
def list_visits(user=Depends(security.current_user)):
    security.approved_user(user)
    if user["role"] == "caregiver":
        rows = db.q("SELECT * FROM visits WHERE caregiver_id = ? ORDER BY created_at DESC", [user["id"]])
    elif user["role"] == "kaki":
        rows = db.q("SELECT * FROM visits WHERE kaki_id = ? ORDER BY created_at DESC", [user["id"]])
    else:  # admin
        rows = db.q("SELECT * FROM visits ORDER BY created_at DESC")
    return [_out(v, user) for v in rows]

def _past_kakis(household_id: str) -> list[dict]:
    """Kakis who have completed a visit for this household, most visits first."""
    rows = db.q("""SELECT u.id, u.name, u.photo, count(*) AS times
                   FROM visits v JOIN users u ON u.id = v.kaki_id
                   WHERE v.household_id = ? AND v.status = 'completed'
                     AND u.role = 'kaki' AND u.status = 'approved'
                   GROUP BY u.id, u.name, u.photo ORDER BY times DESC, u.name""", [household_id])
    return [{"id": r["id"], "name": r["name"], "photo": r.get("photo") or "", "times": r["times"]} for r in rows]

@router.get("/past-kakis")
def past_kakis(user=Depends(security.current_user)):
    """For the booking form: 'someone they know'. Caregiver only."""
    security.approved_user(user)
    security.require_role(user, "caregiver")
    h = db.one("SELECT id FROM households WHERE caregiver_id = ?", [user["id"]])
    return _past_kakis(h["id"]) if h else []

@router.get("/{vid}")
def get_visit(vid: str, user=Depends(security.current_user)):
    security.approved_user(user)
    v = db.one("SELECT * FROM visits WHERE id = ?", [vid])
    if not v:
        raise HTTPException(404, "Visit not found")
    if user["role"] != "admin" and user["id"] not in (v["caregiver_id"], v.get("kaki_id")):
        raise HTTPException(403, "Not your visit")
    return _out(v, user)   # the kaki gets the code from the family in person, never from the API

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
    return _out(v, user)

@router.post("/{vid}/decline")
def decline(vid: str, user=Depends(security.current_user)):
    security.approved_user(user)
    v = _transition(vid, user, ["kaki"], ["assigned"], "requested")
    kaki, cg, senior = _parties(v)          # before the kaki is cleared
    db.run("UPDATE visits SET kaki_id = NULL, assigned_at = NULL, kaki_code = '', kaki_verified_at = NULL WHERE id = ?", [vid])
    notify.visit_declined(v, kaki, cg, senior)
    return _out(db.one("SELECT * FROM visits WHERE id = ?", [vid]), user)

@router.post("/{vid}/verify-kaki")
def verify_kaki(vid: str, body: KakiCodeIn, user=Depends(security.current_user)):
    """Caregiver enters the 4-digit code the kaki shows on arrival (with their
    photo). Success reveals the caregiver's own start code. NCSS wanted the
    code to run kaki → family as proof of identity; the family's code still
    runs family → kaki as proof of admission. Both halves, v1.6."""
    security.approved_user(user)
    security.require_role(user, "caregiver")
    v = db.one("SELECT * FROM visits WHERE id = ?", [vid])
    if not v:
        raise HTTPException(404, "Visit not found")
    if v["caregiver_id"] != user["id"]:
        raise HTTPException(403, "Not your visit")
    if v["status"] not in ("assigned", "accepted") or not v.get("kaki_id"):
        raise HTTPException(400, "No kaki to check yet")
    if body.code.strip() != (v.get("kaki_code") or ""):
        db.audit(user["email"] or user["phone"], "kaki_code_wrong", vid)
        raise HTTPException(400, "That code doesn't match — ask your kaki to show it again, or call the coordinator")
    if not v.get("kaki_verified_at"):
        db.run("UPDATE visits SET kaki_verified_at = current_timestamp WHERE id = ?", [vid])
        db.audit(user["email"] or user["phone"], "kaki_verified", vid)
    return _out(db.one("SELECT * FROM visits WHERE id = ?", [vid]), user)

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
    return _out(v, user)

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
    return _out(v, user)

@router.post("/{vid}/complete")
def complete(vid: str, body: ReportIn, user=Depends(security.current_user)):
    security.approved_user(user)
    v = _transition(vid, user, ["kaki"], ["in_progress"], "completed", "completed_at")
    db.run("DELETE FROM visit_reports WHERE visit_id = ?", [vid])
    db.run("INSERT INTO visit_reports(visit_id, chips, text, meds_confirmed) VALUES (?,?,?,?)",
           [vid, db.j(body.chips), body.text, body.meds_confirmed])
    kaki, _cg, senior = _parties(v)
    notify.visit_finished_contact(v, kaki, senior, db.one("SELECT * FROM care_plans WHERE household_id = ?", [v["household_id"]]))
    return _out(db.one("SELECT * FROM visits WHERE id = ?", [vid]), user)

@router.post("/{vid}/cancel")
def cancel(vid: str, body: CancelIn | None = None, user=Depends(security.current_user)):
    """Cancellation as a lifecycle, not a pre-arrival button (v1.6).

    caregiver: any non-final state → cancelled; the kaki is told.
    kaki:      assigned/accepted → back to requested with the kaki cleared, a
               reason required, the caregiver told; in_progress → cancelled
               with a reason. Passing an assigned visit back without a reason
               is still `decline`.
    admin:     any non-final state → cancelled; both sides told.
    Who and why are recorded on the visit; compensation is a policy question."""
    security.approved_user(user)
    body = body or CancelIn()
    reason = (body.reason or "").strip()
    v = db.one("SELECT * FROM visits WHERE id = ?", [vid])
    if not v:
        raise HTTPException(404, "Visit not found")
    role = user["role"]
    if role == "caregiver" and v["caregiver_id"] != user["id"]:
        raise HTTPException(403, "Not your visit")
    if role == "kaki" and v.get("kaki_id") != user["id"]:
        raise HTTPException(403, "Not your visit")
    if v["status"] in ("completed", "cancelled"):
        raise HTTPException(400, f"Can't cancel — visit is {v['status']}")
    kaki, cg, senior = _parties(v)
    stamp = "cancelled_by = ?, cancelled_by_name = ?, cancel_reason = ?, cancelled_at = current_timestamp"
    if role == "kaki":
        if not reason:
            raise HTTPException(400, "Tell the family why, in a few words — they'll be looking for you")
        if v["status"] in ("assigned", "accepted"):
            # Back to the queue for a new match; the family is told who and why.
            db.run(f"""UPDATE visits SET status = 'requested', kaki_id = NULL, assigned_at = NULL,
                       accepted_at = NULL, on_way_at = NULL, kaki_code = '', kaki_verified_at = NULL, {stamp}
                       WHERE id = ?""", ["kaki", user.get("name") or "", reason, vid])
            db.audit(user["email"] or user["phone"], "visit_kaki_cancelled", f"{vid}: {reason}")
            v2 = db.one("SELECT * FROM visits WHERE id = ?", [vid])
            notify.visit_cancelled(v2, "kaki", kaki, cg, senior, reason)
            return _out(v2, user)
        db.run(f"UPDATE visits SET status = 'cancelled', {stamp} WHERE id = ?",
               ["kaki", user.get("name") or "", reason, vid])
        db.audit(user["email"] or user["phone"], "visit_cancelled_mid", f"{vid}: {reason}")
        v2 = db.one("SELECT * FROM visits WHERE id = ?", [vid])
        notify.visit_cancelled(v2, "kaki", kaki, cg, senior, reason)
        return _out(v2, user)
    # caregiver or admin
    db.run(f"UPDATE visits SET status = 'cancelled', {stamp} WHERE id = ?",
           [role, user.get("name") or "", reason, vid])
    db.audit(user["email"] or user["phone"], "visit_cancelled", f"{vid}: {reason}")
    v2 = db.one("SELECT * FROM visits WHERE id = ?", [vid])
    if v2.get("kaki_id"):
        notify.visit_cancelled(v2, role, kaki, cg, senior, reason)
    return _out(v2, user)

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
