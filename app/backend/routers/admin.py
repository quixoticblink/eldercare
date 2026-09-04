"""M-ADMIN · approvals, manual matching, quality. Automated matching lands here later."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from .. import assumptions, db, security, settings
from ..services import availability, matching

router = APIRouter(prefix="/admin", tags=["admin"])

class AssignIn(BaseModel):
    kaki_id: str

class ApproveIn(BaseModel):
    role: str | None = None   # optionally set/override role on approval

class SettingsIn(BaseModel):
    auto_approve_kaki: bool | None = None
    auto_approve_caregiver: bool | None = None
    auto_match: bool | None = None
    paynow_type: str | None = None
    paynow_value: str | None = None
    paynow_name: str | None = None

class ServiceRatesIn(BaseModel):
    # {"Chaperone": {"hours": 3, "family_rate_per_hour": 28, "kaki_rate_per_hour": 12}}
    services: dict[str, dict[str, float | int | None]]

def _admin(user):
    security.approved_user(user)
    security.require_role(user, "admin")
    return user

@router.get("/overview")
def overview(user=Depends(security.current_user)):
    _admin(user)
    def count(sql, params=None):
        return db.q(sql, params)[0]["c"]
    return {
        "pending_users":  count("SELECT count(*) c FROM users  WHERE status = 'pending'"),
        "open_requests":  count("SELECT count(*) c FROM visits WHERE status = 'requested'"),
        "active_visits":  count("SELECT count(*) c FROM visits WHERE status IN ('assigned','accepted','in_progress')"),
        "completed":      count("SELECT count(*) c FROM visits WHERE status = 'completed'"),
        "care_notes":     count("SELECT count(*) c FROM care_notes"),
    }

@router.get("/pending-users")
def pending_users(user=Depends(security.current_user)):
    _admin(user)
    return db.q("SELECT id, email, name, phone, role, status, created_at FROM users WHERE status = 'pending' ORDER BY created_at")

@router.get("/users")
def all_users(user=Depends(security.current_user)):
    _admin(user)
    rows = db.q("SELECT id, email, name, phone, role, status, created_at FROM users ORDER BY created_at")
    for r in rows:
        if r["role"] == "kaki":
            p = db.one("SELECT * FROM kaki_profiles WHERE user_id = ?", [r["id"]]) or {}
            r["kaki"] = {"services": db.uj(p.get("services")), "languages": db.uj(p.get("languages")),
                         "area": p.get("area"), "tier": p.get("tier", 1)}
    return rows

@router.post("/users/{uid}/approve")
def approve(uid: str, body: ApproveIn, user=Depends(security.current_user)):
    _admin(user)
    target = db.one("SELECT * FROM users WHERE id = ?", [uid])
    if not target:
        raise HTTPException(404, "User not found")
    role = body.role or target["role"] or "caregiver"
    db.run("UPDATE users SET status = 'approved', role = ? WHERE id = ?", [role, uid])
    if role == "kaki" and not db.one("SELECT 1 FROM kaki_profiles WHERE user_id = ?", [uid]):
        db.run("INSERT INTO kaki_profiles(user_id) VALUES (?)", [uid])
    db.audit(user["email"], "user_approved", f"{target['email']} as {role}")
    return {"ok": True}

@router.post("/users/{uid}/suspend")
def suspend(uid: str, user=Depends(security.current_user)):
    _admin(user)
    if uid == user["id"]:
        raise HTTPException(400, "You can't suspend yourself")
    db.run("UPDATE users SET status = 'suspended' WHERE id = ?", [uid])
    db.audit(user["email"], "user_suspended", uid)
    return {"ok": True}

@router.get("/kakis")
def kakis(visit_id: str | None = None, user=Depends(security.current_user)):
    """Approved kakis for the matching picker.

    Pass ?visit_id= to get each kaki's availability for that visit's date and
    window. Availability never filters the list — the coordinator may still need
    to assign someone who is nominally off, especially for urgent cases — it
    only sorts and flags."""
    _admin(user)
    visit = db.one("SELECT * FROM visits WHERE id = ?", [visit_id]) if visit_id else None

    rows = db.q("""SELECT u.id, u.name, u.email, u.phone FROM users u
                   WHERE u.role = 'kaki' AND u.status = 'approved' ORDER BY u.name""")
    for r in rows:
        p = db.one("SELECT * FROM kaki_profiles WHERE user_id = ?", [r["id"]]) or {}
        r["services"] = db.uj(p.get("services"))
        r["languages"] = db.uj(p.get("languages"))
        r["active"] = db.q("SELECT count(*) c FROM visits WHERE kaki_id = ? AND status IN ('assigned','accepted','in_progress')", [r["id"]])[0]["c"]
        r["done_with"] = {}  # visits completed per household — consistency signal
        for row in db.q("""SELECT household_id, count(*) c FROM visits
                           WHERE kaki_id = ? AND status = 'completed' GROUP BY household_id""", [r["id"]]):
            r["done_with"][row["household_id"]] = row["c"]
        r["availability"] = availability.summary(r["id"])
        if visit:
            _wanted = db.uj(visit.get("languages")) or ([visit["language"]] if visit.get("language") else [])
            r["language_ok"] = any(l in r["languages"] for l in _wanted)
        r["fit"] = (availability.check(r["id"], visit.get("date"), visit.get("time_window"))
                    if visit else {"state": "unknown", "why": "no visit selected"})

    if visit:
        order = {"available": 0, "unknown": 1, "unavailable": 2}
        rows.sort(key=lambda r: (order.get(r["fit"]["state"], 3),
                                 -r["done_with"].get(visit["household_id"], 0),
                                 r["active"], (r["name"] or "").lower()))
    return rows

@router.post("/visits/{vid}/assign")
def assign(vid: str, body: AssignIn, user=Depends(security.current_user)):
    """Manual matching, v1. Automated scoring will replace ONLY this endpoint's logic."""
    _admin(user)
    v = db.one("SELECT * FROM visits WHERE id = ?", [vid])
    if not v:
        raise HTTPException(404, "Visit not found")
    if v["status"] not in ("requested", "assigned"):
        raise HTTPException(400, f"Visit is {v['status']}")
    # Shared with the automatic matcher so both paths validate and notify
    # identically. Returns who actually received it — assigning to the wrong
    # kaki is silent otherwise, and looks exactly like the feature being broken.
    try:
        return matching.assign(vid, body.kaki_id, user["email"] or user["phone"])
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/auto-match")
def auto_match_all(user=Depends(security.current_user)):
    """Fill every outstanding request that has an available kaki, urgent first.
    Works regardless of the auto_match toggle — the toggle governs automatic
    assignment at booking time; this is the coordinator asking explicitly."""
    _admin(user)
    return matching.sweep(user["email"] or user["phone"])

@router.get("/settings")
def get_settings(user=Depends(security.current_user)):
    _admin(user)
    return settings.all()

@router.put("/settings")
def put_settings(body: SettingsIn, user=Depends(security.current_user)):
    _admin(user)
    payload = {k: v for k, v in body.model_dump().items() if v is not None}
    if "paynow_type" in payload and payload["paynow_type"] not in ("uen", "mobile"):
        raise HTTPException(400, "paynow_type must be 'uen' or 'mobile'")
    return settings.set_many(payload, user["email"] or user["phone"])

@router.put("/assumptions/services")
def put_service_rates(body: ServiceRatesIn, user=Depends(security.current_user)):
    """Edit the price stack from the admin panel. Writes assumptions.json so it
    stays the single source of truth — hours and rates never live in two places."""
    _admin(user)
    data = assumptions.public()
    services = data.setdefault("services", {})
    for name, vals in (body.services or {}).items():
        if name not in services:
            raise HTTPException(400, f"Unknown service: {name}")
        for field in ("hours", "family_rate_per_hour", "kaki_rate_per_hour"):
            if field in vals and vals[field] is not None:
                try:
                    number = float(vals[field])
                except (TypeError, ValueError):
                    raise HTTPException(400, f"{name}.{field} must be a number")
                if number < 0:
                    raise HTTPException(400, f"{name}.{field} cannot be negative")
                services[name][field] = int(number) if field == "hours" else number
        services[name]["source"] = f"Set by coordinator via admin panel ({db.now():%Y-%m-%d})"
    try:
        assumptions.save(data)
    except Exception as e:
        raise HTTPException(500, f"Could not write assumptions.json: {e}")
    db.audit(user["email"] or user["phone"], "rates_changed", ", ".join(body.services or {}))
    return assumptions.public()

@router.get("/assumptions")
def get_assumptions(user=Depends(security.current_user)):
    """The money/time assumptions the engine runs on, so the coordinator can
    see exactly what drives every figure — and challenge it."""
    _admin(user)
    return assumptions.public()

@router.get("/quality")
def quality(user=Depends(security.current_user)):
    _admin(user)
    reports = db.q("""SELECT r.*, v.service, v.date, v.caregiver_id, v.kaki_id, v.household_id
                      FROM visit_reports r JOIN visits v ON v.id = r.visit_id
                      ORDER BY r.created_at DESC LIMIT 50""")
    notes = db.q("SELECT * FROM care_notes ORDER BY created_at DESC LIMIT 50")
    for x in reports:
        x["chips"] = db.uj(x.get("chips"))
    for n in notes:
        n["chips"] = db.uj(n.get("chips"))
    return {"reports": reports, "notes": notes}
