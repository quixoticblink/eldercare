"""M-AUTH · OTP login by email OR mobile, sessions, roles, approval status.

One sign-in box takes either channel. The code goes out over Resend (email) or
AWS SNS (SMS); in DEV_MODE it comes back in the response instead. Returning
users are recognised before the code screen is drawn, so they are only ever
asked for the 6 digits — never their name or role again.
"""
import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from .. import config, db, security
from ..services import emailer, ratelimit, sms

router = APIRouter(prefix="/auth", tags=["auth"])

class IdentifierIn(BaseModel):
    identifier: str | None = None
    email: str | None = None          # legacy callers: treated as the identifier

class VerifyIn(BaseModel):
    identifier: str | None = None
    email: str | None = None          # legacy callers: treated as the identifier
    code: str
    role: str | None = None           # caregiver | kaki — first sign-in only
    name: str | None = None           # first sign-in only
    contact_phone: str | None = None  # optional 2nd channel when joining by email
    contact_email: str | None = None  # optional 2nd channel when joining by phone

def _public(user: dict) -> dict:
    out = {k: user.get(k) for k in ("id", "email", "name", "phone", "role", "status")}
    out["email_verified"] = bool(user.get("email_verified"))
    out["phone_verified"] = bool(user.get("phone_verified"))
    return out

def _identifier(body) -> tuple[str, str]:
    try:
        return security.classify(body.identifier or body.email or "")
    except ValueError as e:
        raise HTTPException(400, str(e))

def _find_user(channel: str, value: str):
    if channel == "email":
        return db.one("SELECT * FROM users WHERE lower(email) = ?", [value])
    return db.one("SELECT * FROM users WHERE phone = ?", [value])

def _send(channel: str, value: str, code: str) -> dict:
    return emailer.send_otp_email(value, code) if channel == "email" else sms.send_otp_sms(value, code)

def _is_admin(channel: str, value: str) -> bool:
    return value in (config.ADMIN_EMAILS if channel == "email" else config.ADMIN_PHONES)

def _claim_free(channel: str, value: str, exclude_id: str | None = None):
    """Refuse to attach an email/phone that already belongs to someone else."""
    owner = _find_user(channel, value)
    if owner and owner["id"] != exclude_id:
        label = "email address" if channel == "email" else "mobile number"
        raise HTTPException(400, f"That {label} is already linked to another account")

@router.post("/request-code")
def request_code(body: IdentifierIn, request: Request = None):
    channel, value = _identifier(body)

    # Each call sends a real SMS or email. Unlimited calls means an attacker can
    # run up the Twilio bill and hammer someone's phone at the same time.
    ip = ratelimit.client_ip(request)
    if ratelimit.exceeded("request_code_identifier", value):
        raise HTTPException(429, f"Too many codes requested. Try again in "
                                 f"{ratelimit.retry_after('request_code_identifier', value)} minutes, "
                                 f"or call the coordinator on 6XXX XXXX.")
    if ip and ratelimit.exceeded("request_code_ip", ip):
        raise HTTPException(429, "Too many sign-in attempts from this connection. "
                                 "Please wait a few minutes and try again.")
    ratelimit.record("request_code_identifier", value)
    if ip:
        ratelimit.record("request_code_ip", ip)

    user = _find_user(channel, value)

    code = security.new_otp()
    expires = db.now() + datetime.timedelta(minutes=config.OTP_MINUTES)
    db.run("DELETE FROM otp_codes WHERE identifier = ?", [value])
    db.run("INSERT INTO otp_codes VALUES (?,?,?,?)", [value, channel, code, expires])

    result = _send(channel, value, code)
    out = {
        "ok": True,
        "sent": result["sent"],
        "channel": channel,
        "identifier": value,
        # Drives the code screen: a known account with a role set is asked for
        # nothing but the 6 digits.
        "known": bool(user),
        "needs_profile": not user or not user["role"],
    }
    if result["dev_code"]:
        out["dev_code"] = result["dev_code"]   # DEV_MODE only
    if config.is_demo_identifier(value):
        # Demo backdoor: show the code on screen even in production, so the app
        # can be walked through without a working SMS provider. Flagged and
        # audited, because it is a real bypass — see config.DEMO_IDENTIFIERS.
        out["dev_code"] = code
        out["demo"] = True
        db.audit(value, "demo_code_issued", f"via {channel}")
    return out

@router.post("/verify")
def verify(body: VerifyIn):
    channel, value = _identifier(body)

    # A 6-digit code is only strong if guesses are limited. Without this an
    # attacker can walk the whole keyspace inside the 10-minute window.
    if ratelimit.exceeded("verify_failure", value):
        raise HTTPException(429, f"Too many incorrect codes. Locked for "
                                 f"{ratelimit.retry_after('verify_failure', value)} minutes — "
                                 f"request a new code after that, or call the coordinator.")

    row = db.one("SELECT * FROM otp_codes WHERE identifier = ? AND code = ?", [value, body.code.strip()])
    if not row:
        ratelimit.record("verify_failure", value)
        db.audit(value, "login_failed", "wrong code")
        raise HTTPException(400, "Wrong code — check and try again")
    if row["expires"] < db.now():
        raise HTTPException(400, "Code expired — request a new one")
    db.run("DELETE FROM otp_codes WHERE identifier = ?", [value])
    # A genuine sign-in clears the counters, so an honest user who fumbled a few
    # digits is not left locked out.
    ratelimit.clear("verify_failure", value)
    ratelimit.clear("request_code_identifier", value)
    ratelimit.prune()

    user = _find_user(channel, value)
    if not user:
        user = _create_user(channel, value, body)
    else:
        _update_existing(user, channel, body)
        user = db.one("SELECT * FROM users WHERE id = ?", [user["id"]])

    db.audit(value, "login", f"via {channel}")
    return {"token": security.make_token(user["id"]), "user": _public(user)}

def _auto_approved(role: str) -> bool:
    from .. import settings
    return bool(settings.get(f"auto_approve_{role}")) if role in ("kaki", "caregiver") else False

def _create_user(channel: str, value: str, body: VerifyIn):
    is_admin = _is_admin(channel, value)
    role = "admin" if is_admin else (body.role if body.role in ("caregiver", "kaki") else "")
    # Admins are always approved. Everyone else waits for the coordinator unless
    # auto-approval has been deliberately switched on for their role.
    status = "approved" if (is_admin or _auto_approved(role)) else "pending"

    email = value if channel == "email" else None
    phone = value if channel == "phone" else ""

    # Optional second channel offered at signup. Captured now, verified the
    # first time it is actually used to sign in.
    if channel == "email" and body.contact_phone:
        try:
            phone = security.normalise_phone(body.contact_phone)
        except ValueError as e:
            raise HTTPException(400, str(e))
        _claim_free("phone", phone)
    if channel == "phone" and body.contact_email:
        try:
            email = security.normalise_email(body.contact_email)
        except ValueError as e:
            raise HTTPException(400, str(e))
        _claim_free("email", email)

    uid = db.new_id()
    db.run("""INSERT INTO users(id, email, name, phone, role, status, email_verified, phone_verified)
              VALUES (?,?,?,?,?,?,?,?)""",
           [uid, email, body.name or "", phone, role, status,
            channel == "email", channel == "phone"])
    if role == "kaki":
        db.run("INSERT INTO kaki_profiles(user_id) VALUES (?)", [uid])
    db.audit(value, "signup", f"role={role} status={status} via {channel}")
    return db.one("SELECT * FROM users WHERE id = ?", [uid])

def _update_existing(user: dict, channel: str, body: VerifyIn):
    uid = user["id"]
    # Mark the channel they just proved they control.
    column = "email_verified" if channel == "email" else "phone_verified"
    db.run(f"UPDATE users SET {column} = TRUE WHERE id = ?", [uid])

    # A pending user who never picked a role may still set one.
    if not user["role"] and body.role in ("caregiver", "kaki"):
        db.run("UPDATE users SET role = ? WHERE id = ?", [body.role, uid])
        if body.role == "kaki" and not db.one("SELECT 1 FROM kaki_profiles WHERE user_id = ?", [uid]):
            db.run("INSERT INTO kaki_profiles(user_id) VALUES (?)", [uid])

    # Fill in a missing second channel, but never silently overwrite one.
    if body.contact_phone and not (user.get("phone") or "").strip():
        try:
            phone = security.normalise_phone(body.contact_phone)
        except ValueError as e:
            raise HTTPException(400, str(e))
        _claim_free("phone", phone, exclude_id=uid)
        db.run("UPDATE users SET phone = ? WHERE id = ?", [phone, uid])
    if body.contact_email and not (user.get("email") or "").strip():
        try:
            email = security.normalise_email(body.contact_email)
        except ValueError as e:
            raise HTTPException(400, str(e))
        _claim_free("email", email, exclude_id=uid)
        db.run("UPDATE users SET email = ? WHERE id = ?", [email, uid])

@router.get("/me")
def me(user=Depends(security.current_user)):
    from .. import assumptions, settings
    return {"user": _public(user), "config": {
        "services": config.SERVICES, "locked_services": config.LOCKED_SERVICES,
        "tiers": config.TIERS, "languages": config.LANGUAGES,
        "weekdays": config.WEEKDAYS, "half_days": config.HALF_DAYS,
        "half_day_windows": assumptions.half_day_windows(),
        "money_disclaimer": assumptions.disclaimer(),
        "max_advance_days": settings.get("max_advance_days"),
        "paynow": settings.paynow()}}
