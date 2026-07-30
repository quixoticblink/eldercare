"""M-AUTH · stateless signed tokens (HMAC) + auth dependency. No external JWT lib."""
import base64, hashlib, hmac, json, time, random
from fastapi import Header, HTTPException
from . import config, db

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
