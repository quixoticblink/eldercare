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
    gender: str | None = None        # kaki only: female | male | "" (not stated)

class PhotoIn(BaseModel):
    data_url: str = ""     # "data:image/jpeg;base64,..." or "" to remove

PHOTO_MAX_BYTES = 200 * 1024
PHOTO_TYPES = ("image/jpeg", "image/png")

class WeeklyIn(BaseModel):
    # v1.6: {"Mon": {"from": "09:00", "to": "13:00"}, "Sat": {"from": "08:00", "to": "18:00"}}
    # v1.3 (still accepted): {"Mon": ["morning"], "Sat": ["morning", "afternoon"]}
    weekly: dict[str, dict[str, str] | list[str] | None]
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
        if phone != (user.get("phone") or ""):
            # A phone-only account signs in BY this number. Letting them retype
            # it is letting them lock themselves out; that change goes through
            # the coordinator.
            if not (user.get("email") or "").strip():
                raise HTTPException(400, "This number is how you sign in — call the coordinator to change it")
            if phone and db.one("SELECT id FROM users WHERE phone = ? AND id <> ?", [phone, user["id"]]):
                raise HTTPException(400, "That mobile number is already linked to another account")
            # A new number has not been proved yet; it is proved the first time
            # a sign-in code is used on it (M-AUTH).
            db.run("UPDATE users SET phone = ?, phone_verified = FALSE WHERE id = ?", [phone, user["id"]])
    if user["role"] == "kaki":
        if not db.one("SELECT 1 FROM kaki_profiles WHERE user_id = ?", [user["id"]]):
            db.run("INSERT INTO kaki_profiles(user_id) VALUES (?)", [user["id"]])
        if body.services is not None:
            db.run("UPDATE kaki_profiles SET services = ? WHERE user_id = ?", [db.j(body.services), user["id"]])
        if body.languages is not None:
            db.run("UPDATE kaki_profiles SET languages = ? WHERE user_id = ?", [db.j(body.languages), user["id"]])
        if body.area is not None:
            db.run("UPDATE kaki_profiles SET area = ? WHERE user_id = ?", [body.area, user["id"]])
        if body.gender is not None:
            g = body.gender.strip().lower()
            if g not in config.GENDERS + [""]:
                raise HTTPException(400, "Gender must be female or male, or left blank")
            db.run("UPDATE kaki_profiles SET gender = ? WHERE user_id = ?", [g, user["id"]])
    return get_me_profile(db.one("SELECT * FROM users WHERE id = ?", [user["id"]]))

@router.put("/me/photo")
def put_photo(body: PhotoIn, user=Depends(security.current_user)):
    """Kaki profile photo, shown to the family on the visit page. Stored as a
    data URL in the users table — one file, one backup, no object storage —
    and capped, because the frontend resizes to 320px before sending."""
    import base64, re
    security.require_role(user, "kaki")
    if user.get("status") == "suspended":
        raise HTTPException(403, "Account suspended — call the coordinator")
    data = (body.data_url or "").strip()
    if data:
        if len(data) > PHOTO_MAX_BYTES * 4 // 3 + 64:      # refuse before decoding
            raise HTTPException(413, "Photo too large — the app should resize it first")
        m = re.match(r"^data:(image/(?:jpeg|png));base64,([A-Za-z0-9+/=]+)$", data)
        if not m or m.group(1) not in PHOTO_TYPES:
            raise HTTPException(400, "Photos must be JPEG or PNG")
        try:
            raw = base64.b64decode(m.group(2), validate=True)
        except Exception:
            raise HTTPException(400, "That image could not be read")
        if len(raw) > PHOTO_MAX_BYTES:
            raise HTTPException(413, "Photo too large — the app should resize it first")
    db.run("UPDATE users SET photo = ? WHERE id = ?", [data, user["id"]])
    db.audit(user["email"] or user["phone"], "photo_set" if data else "photo_removed", "")
    return get_me_profile(db.one("SELECT * FROM users WHERE id = ?", [user["id"]]))

@router.get("/me/profile")
def get_me_profile(user=Depends(security.current_user)):
    out = {k: user.get(k) for k in ("id", "email", "name", "phone", "role", "status")}
    out["photo"] = user.get("photo") or ""
    if user["role"] == "kaki":
        p = db.one("SELECT * FROM kaki_profiles WHERE user_id = ?", [user["id"]]) or {}
        out["kaki"] = {"services": db.uj(p.get("services")), "languages": db.uj(p.get("languages")),
                       "area": p.get("area", "Pasir Ris"), "tier": p.get("tier", 1),
                       "gender": p.get("gender") or "",
                       "availability": availability.summary(user["id"])}
    return out

# ---- certificates (kaki only) -------------------------------------------------
# Certification gates supply (Aug 3). A kaki uploads the evidence; the
# coordinator sees it when approving and when matching. Metadata in lists,
# the file only on an explicit fetch.

CERT_MAX_BYTES = 1024 * 1024
CERT_MAX_PER_KAKI = 10
CERT_TYPES = ("application/pdf", "image/jpeg", "image/png")

class CertificateIn(BaseModel):
    name: str
    issuer: str | None = ""
    expires: str | None = ""       # YYYY-MM-DD, free text tolerated
    file_name: str | None = ""
    data_url: str                  # data:<mime>;base64,...

def _cert_public(row: dict) -> dict:
    return {k: row.get(k) for k in ("id", "name", "issuer", "expires", "file_name", "mime", "uploaded_at")}

def list_certificates(user_id: str) -> list[dict]:
    rows = db.q("""SELECT id, name, issuer, expires, file_name, mime, uploaded_at
                   FROM kaki_certificates WHERE user_id = ? ORDER BY uploaded_at""", [user_id])
    return [_cert_public(r) for r in rows]

@router.get("/me/certificates")
def my_certificates(user=Depends(security.current_user)):
    security.require_role(user, "kaki")
    return list_certificates(user["id"])

@router.post("/me/certificates")
def add_certificate(body: CertificateIn, user=Depends(security.current_user)):
    import base64, re
    security.require_role(user, "kaki")
    if user.get("status") == "suspended":
        raise HTTPException(403, "Account suspended — call the coordinator")
    name = (body.name or "").strip()
    if not name:
        raise HTTPException(400, "Name the certificate, e.g. CPR + AED")
    if db.q("SELECT count(*) c FROM kaki_certificates WHERE user_id = ?", [user["id"]])[0]["c"] >= CERT_MAX_PER_KAKI:
        raise HTTPException(400, f"Up to {CERT_MAX_PER_KAKI} certificates — remove one first")
    data = (body.data_url or "").strip()
    if len(data) > CERT_MAX_BYTES * 4 // 3 + 64:           # refuse before decoding
        raise HTTPException(413, "File too large — 1 MB at most; a photo of the certificate is fine")
    m = re.match(r"^data:([a-z]+/[a-z0-9.+-]+);base64,([A-Za-z0-9+/=]+)$", data)
    if not m or m.group(1) not in CERT_TYPES:
        raise HTTPException(400, "Certificates must be a PDF, JPEG or PNG")
    try:
        raw = base64.b64decode(m.group(2), validate=True)
    except Exception:
        raise HTTPException(400, "That file could not be read")
    if len(raw) > CERT_MAX_BYTES:
        raise HTTPException(413, "File too large — 1 MB at most; a photo of the certificate is fine")
    db.run("""INSERT INTO kaki_certificates(id, user_id, name, issuer, expires, file_name, mime, data)
              VALUES (?,?,?,?,?,?,?,?)""",
           [db.new_id(), user["id"], name, (body.issuer or "").strip(), (body.expires or "").strip(),
            (body.file_name or "").strip()[:120], m.group(1), body.data_url.strip()])
    db.audit(user["email"] or user["phone"], "certificate_added", name)
    return list_certificates(user["id"])

@router.delete("/me/certificates/{cid}")
def remove_certificate(cid: str, user=Depends(security.current_user)):
    security.require_role(user, "kaki")
    if not db.one("SELECT 1 FROM kaki_certificates WHERE id = ? AND user_id = ?", [cid, user["id"]]):
        raise HTTPException(404, "No such certificate")
    db.run("DELETE FROM kaki_certificates WHERE id = ? AND user_id = ?", [cid, user["id"]])
    db.audit(user["email"] or user["phone"], "certificate_removed", cid)
    return list_certificates(user["id"])

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
    for day, value in (body.weekly or {}).items():
        if day not in config.WEEKDAYS or value is None:
            continue
        if isinstance(value, dict):
            a, b = availability.parse_hhmm(value.get("from", "")), availability.parse_hhmm(value.get("to", ""))
            if a is None or b is None:
                raise HTTPException(400, f"{day}: times look like 09:00")
            if not (availability.on_the_half_hour(a) and availability.on_the_half_hour(b)):
                raise HTTPException(400, f"{day}: times go in 30-minute steps")
            if b <= a:
                raise HTTPException(400, f"{day}: the end must be after the start")
            clean[day] = {"from": availability.fmt_hhmm(a), "to": availability.fmt_hhmm(b)}
        else:
            picked = [s for s in (value or []) if s in config.HALF_DAYS]
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
