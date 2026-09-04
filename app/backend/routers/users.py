"""M-USERS · profiles, kaki preferences and availability."""
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from .. import config, db, security
from ..services import availability

router = APIRouter(prefix="/users", tags=["users"])

class ProfileIn(BaseModel):
    name: str | None = None
    phone: str | None = None
    services: list[str] | None = None
    languages: list[str] | None = None
    area: str | None = None

class WeeklyIn(BaseModel):
    # {"Mon": ["morning"], "Sat": ["morning", "afternoon"]}
    weekly: dict[str, list[str]]
    note: str | None = None

class ExceptionIn(BaseModel):
    date: str                      # YYYY-MM-DD
    half_day: str = "all"          # morning | afternoon | all
    available: bool = False        # False = day off, True = extra slot
    note: str | None = ""

@router.put("/me")
def update_me(body: ProfileIn, user=Depends(security.current_user)):
    if body.name is not None:
        db.run("UPDATE users SET name = ? WHERE id = ?", [body.name.strip(), user["id"]])
    if body.phone is not None:
        phone = body.phone.strip()
        if phone:
            try:
                phone = security.normalise_phone(phone)
            except ValueError as e:
                raise HTTPException(400, str(e))
            owner = db.one("SELECT id FROM users WHERE phone = ? AND id <> ?", [phone, user["id"]])
            if owner:
                raise HTTPException(400, "That mobile number is already linked to another account")
        db.run("UPDATE users SET phone = ? WHERE id = ?", [phone, user["id"]])
    if user["role"] == "kaki":
        if not db.one("SELECT 1 FROM kaki_profiles WHERE user_id = ?", [user["id"]]):
            db.run("INSERT INTO kaki_profiles(user_id) VALUES (?)", [user["id"]])
        if body.services is not None:
            db.run("UPDATE kaki_profiles SET services = ? WHERE user_id = ?", [db.j(body.services), user["id"]])
        if body.languages is not None:
            db.run("UPDATE kaki_profiles SET languages = ? WHERE user_id = ?", [db.j(body.languages), user["id"]])
        if body.area is not None:
            db.run("UPDATE kaki_profiles SET area = ? WHERE user_id = ?", [body.area, user["id"]])
    return get_me_profile(db.one("SELECT * FROM users WHERE id = ?", [user["id"]]))

@router.get("/me/profile")
def get_me_profile(user=Depends(security.current_user)):
    out = {k: user.get(k) for k in ("id", "email", "name", "phone", "role", "status")}
    if user["role"] == "kaki":
        p = db.one("SELECT * FROM kaki_profiles WHERE user_id = ?", [user["id"]]) or {}
        out["kaki"] = {"services": db.uj(p.get("services")), "languages": db.uj(p.get("languages")),
                       "area": p.get("area", "Pasir Ris"), "tier": p.get("tier", 1),
                       "availability": availability.summary(user["id"])}
    return out

# ---- availability (kaki only) ------------------------------------------------

def _kaki(user):
    security.require_role(user, "kaki")
    if not db.one("SELECT 1 FROM kaki_profiles WHERE user_id = ?", [user["id"]]):
        db.run("INSERT INTO kaki_profiles(user_id) VALUES (?)", [user["id"]])
    return user

@router.get("/me/availability")
def get_availability(user=Depends(security.current_user)):
    _kaki(user)
    return availability.summary(user["id"])

@router.put("/me/availability")
def put_availability(body: WeeklyIn, user=Depends(security.current_user)):
    """Replaces the recurring week. Unknown day names or half-days are dropped
    rather than stored, so a typo can never make someone silently unbookable."""
    _kaki(user)
    clean = {}
    for day, slots in (body.weekly or {}).items():
        if day not in config.WEEKDAYS:
            continue
        picked = [s for s in (slots or []) if s in config.HALF_DAYS]
        if picked:
            clean[day] = picked
    db.run("UPDATE kaki_profiles SET weekly_slots = ? WHERE user_id = ?",
           [json.dumps(clean), user["id"]])
    if body.note is not None:
        db.run("UPDATE kaki_profiles SET availability_note = ? WHERE user_id = ?",
               [body.note, user["id"]])
    db.audit(user["email"] or user["phone"], "availability_set", json.dumps(clean))
    return availability.summary(user["id"])

@router.post("/me/availability/exceptions")
def add_exception(body: ExceptionIn, user=Depends(security.current_user)):
    _kaki(user)
    if availability.parse_date(body.date) is None:
        raise HTTPException(400, "Use a real date, e.g. 2026-08-04")
    if body.half_day not in config.HALF_DAYS + ["all"]:
        raise HTTPException(400, "half_day must be morning, afternoon or all")
    # One entry per date+half-day; re-adding replaces rather than stacking.
    db.run("DELETE FROM availability_exceptions WHERE user_id = ? AND date = ? AND half_day = ?",
           [user["id"], body.date, body.half_day])
    db.run("""INSERT INTO availability_exceptions(id, user_id, date, half_day, available, note)
              VALUES (?,?,?,?,?,?)""",
           [db.new_id(), user["id"], body.date, body.half_day, body.available, body.note or ""])
    return availability.summary(user["id"])

@router.delete("/me/availability/exceptions/{eid}")
def remove_exception(eid: str, user=Depends(security.current_user)):
    _kaki(user)
    db.run("DELETE FROM availability_exceptions WHERE id = ? AND user_id = ?", [eid, user["id"]])
    return availability.summary(user["id"])
