"""M-AUTH · stateless signed tokens (HMAC), identifier handling, auth dependency.

An "identifier" is whatever the person typed into the single sign-in box: an
email address or a mobile number. Everything downstream works with the
normalised pair (channel, value) so the rest of the app never has to guess.
"""
import base64, hashlib, hmac, json, re, time, random
from fastapi import Header, HTTPException
from . import config, db

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def normalise_email(raw: str) -> str:
    email = (raw or "").strip().lower()
    if not _EMAIL_RE.match(email):
        raise ValueError("That email address doesn't look right")
    return email

def normalise_phone(raw: str) -> str:
    """Accepts '9123 4567', '+65 9123 4567', '6591234567' → '+6591234567'."""
    s = re.sub(r"[\s\-().]", "", raw or "")
    digits = re.sub(r"\D", "", s)
    if not digits:
        raise ValueError("Enter a mobile number, e.g. 9123 4567")
    cc = config.DEFAULT_COUNTRY_CODE.lstrip("+")
    if s.startswith("+"):
        if not 8 <= len(digits) <= 15:
            raise ValueError("That mobile number doesn't look right")
        return "+" + digits
    if len(digits) == 8:                                  # bare local number
        return "+" + cc + digits
    if digits.startswith(cc) and len(digits) == len(cc) + 8:
        return "+" + digits
    raise ValueError("Enter a Singapore mobile number, e.g. 9123 4567")

def classify(raw: str) -> tuple[str, str]:
    """→ ('email'|'phone', normalised value). Raises ValueError on junk."""
    s = (raw or "").strip()
    if not s:
        raise ValueError("Enter your email or mobile number")
    return ("email", normalise_email(s)) if "@" in s else ("phone", normalise_phone(s))

def _sign(payload_b: bytes) -> str:
    return hmac.new(config.JWT_SECRET.encode(), payload_b, hashlib.sha256).hexdigest()

def make_token(user_id: str) -> str:
    payload = {"uid": user_id, "exp": int(time.time()) + config.TOKEN_DAYS * 86400}
    pb = base64.urlsafe_b64encode(json.dumps(payload).encode())
    return pb.decode() + "." + _sign(pb)

def parse_token(token: str):
    try:
        pb, sig = token.split(".")
        if not hmac.compare_digest(sig, _sign(pb.encode())):
            return None
        payload = json.loads(base64.urlsafe_b64decode(pb))
        if payload["exp"] < time.time():
            return None
        return payload["uid"]
    except Exception:
        return None

def new_otp() -> str:
    return f"{random.randint(0, 999999):06d}"

def current_user(authorization: str = Header(default="")):
    """FastAPI dependency: Bearer token → user row (any status)."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Not signed in")
    uid = parse_token(authorization[7:])
    if not uid:
        raise HTTPException(401, "Session expired — sign in again")
    user = db.one("SELECT * FROM users WHERE id = ?", [uid])
    if not user:
        raise HTTPException(401, "Account not found")
    return user

def approved_user(user=None):
    if user is None:
        raise HTTPException(401, "Not signed in")
    if user["status"] != "approved":
        raise HTTPException(403, "Account awaiting approval")
    return user

def require_role(user, *roles):
    if user["role"] not in roles:
        raise HTTPException(403, f"Requires role: {' or '.join(roles)}")
    return user
