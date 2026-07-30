"""M-AUTH · email OTP login, sessions, roles, approval status."""
import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from .. import config, db, security
from ..services import emailer

router = APIRouter(prefix="/auth", tags=["auth"])

class EmailIn(BaseModel):
    email: EmailStr

class VerifyIn(BaseModel):
    email: EmailStr
    code: str
    role: str | None = None   # caregiver | kaki — chosen at first login
    name: str | None = None

def _public(user: dict) -> dict:
    return {k: user.get(k) for k in ("id", "email", "name", "phone", "role", "status")}

@router.post("/request-code")
def request_code(body: EmailIn):
    email = body.email.lower()
    code = security.new_otp()
    expires = db.now() + datetime.timedelta(minutes=config.OTP_MINUTES)
    db.run("DELETE FROM otp_codes WHERE email = ?", [email])
    db.run("INSERT INTO otp_codes VALUES (?,?,?)", [email, code, expires])
    result = emailer.send_otp_email(email, code)
    out = {"ok": True, "sent": result["sent"]}
    if result["dev_code"]:
        out["dev_code"] = result["dev_code"]   # DEV_MODE only — lets the app work before Resend is set up
    return out

@router.post("/verify")
def verify(body: VerifyIn):
    email = body.email.lower()
    row = db.one("SELECT * FROM otp_codes WHERE email = ? AND code = ?", [email, body.code.strip()])
    if not row:
        raise HTTPException(400, "Wrong code — check and try again")
    if row["expires"] < db.now():
        raise HTTPException(400, "Code expired — request a new one")
    db.run("DELETE FROM otp_codes WHERE email = ?", [email])

    user = db.one("SELECT * FROM users WHERE email = ?", [email])
    if not user:
        is_admin = email in config.ADMIN_EMAILS
        role = "admin" if is_admin else (body.role if body.role in ("caregiver", "kaki") else "")
        status = "approved" if is_admin else "pending"
        uid = db.new_id()
        db.run("INSERT INTO users(id, email, name, role, status) VALUES (?,?,?,?,?)",
               [uid, email, body.name or "", role, status])
        if role == "kaki":
            db.run("INSERT INTO kaki_profiles(user_id) VALUES (?)", [uid])
        user = db.one("SELECT * FROM users WHERE id = ?", [uid])
        db.audit(email, "signup", f"role={role} status={status}")
    else:
        # allow a pending user with no role yet to set one
        if not user["role"] and body.role in ("caregiver", "kaki"):
            db.run("UPDATE users SET role = ? WHERE id = ?", [body.role, user["id"]])
            if body.role == "kaki" and not db.one("SELECT 1 FROM kaki_profiles WHERE user_id=?", [user["id"]]):
                db.run("INSERT INTO kaki_profiles(user_id) VALUES (?)", [user["id"]])
            user = db.one("SELECT * FROM users WHERE id = ?", [user["id"]])
    db.audit(email, "login")
    return {"token": security.make_token(user["id"]), "user": _public(user)}

@router.get("/me")
def me(user=Depends(security.current_user)):
    return {"user": _public(user), "config": {
        "services": config.SERVICES, "locked_services": config.LOCKED_SERVICES,
        "tiers": config.TIERS, "languages": config.LANGUAGES}}
