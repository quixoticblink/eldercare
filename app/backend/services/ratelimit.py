"""M-AUTH · sliding-window rate limiting for the sign-in endpoints.

Without this the OTP flow has two open doors (ISO 5055 security measures,
CWE-307 improper restriction of excessive authentication attempts and CWE-770
allocation without limits):

  1. /auth/request-code could be called without limit. Every call sends a real
     SMS or email, so an attacker can bill the pilot arbitrarily through Twilio
     and harass a caregiver's phone at the same time.
  2. /auth/verify accepted unlimited guesses at a 6-digit code inside a
     10-minute window. A million codes is not a lot against an unthrottled
     endpoint — that is a practical account-takeover path, not a theoretical
     one.

DB-backed rather than in-memory on purpose: the counters must survive the
restarts that deployment involves, or the limit is trivially reset.
"""
import datetime
from .. import db

# (limit, window minutes) — tuned for elderly users who genuinely do mistype
# and re-request, while still closing off automated abuse.
LIMITS = {
    "request_code_identifier": (5, 15),    # per email/number
    "request_code_ip":        (20, 15),    # per source address, shared networks exist
    "verify_failure":          (5, 15),    # wrong codes before lockout
}

def _cutoff(minutes: int):
    return db.now() - datetime.timedelta(minutes=minutes)

def record(kind: str, key: str) -> None:
    if not key:
        return
    db.run("INSERT INTO auth_attempts(kind, key, ts) VALUES (?,?,current_timestamp)", [kind, key])

def count(kind: str, key: str, minutes: int) -> int:
    if not key:
        return 0
    return db.q("SELECT count(*) c FROM auth_attempts WHERE kind = ? AND key = ? AND ts > ?",
                [kind, key, _cutoff(minutes)])[0]["c"]

def exceeded(kind: str, key: str) -> bool:
    limit, minutes = LIMITS[kind]
    return count(kind, key, minutes) >= limit

def retry_after(kind: str, key: str) -> int:
    """Minutes until the oldest attempt in the window ages out."""
    _, minutes = LIMITS[kind]
    row = db.one("""SELECT min(ts) AS oldest FROM auth_attempts
                    WHERE kind = ? AND key = ? AND ts > ?""", [kind, key, _cutoff(minutes)])
    if not row or not row.get("oldest"):
        return minutes
    elapsed = (db.now() - row["oldest"]).total_seconds() / 60
    return max(1, int(minutes - elapsed) + 1)

def clear(kind: str, key: str) -> None:
    """Called after a success, so one good sign-in resets the counter."""
    db.run("DELETE FROM auth_attempts WHERE kind = ? AND key = ?", [kind, key])

def prune(days: int = 2) -> None:
    """Keep the table small. Called opportunistically, not on a schedule."""
    db.run("DELETE FROM auth_attempts WHERE ts < ?",
           [db.now() - datetime.timedelta(days=days)])

def client_ip(request) -> str:
    """Real caller address. Caddy terminates TLS and proxies, so the socket peer
    is always 127.0.0.1 — the forwarded header is the only useful signal.

    Trusted only because nothing reaches uvicorn except through Caddy on
    localhost; if the app is ever exposed directly this becomes spoofable and
    the IP limit stops being meaningful (the per-identifier limit still holds)."""
    if request is None:
        return ""
    fwd = request.headers.get("x-forwarded-for", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return getattr(getattr(request, "client", None), "host", "") or ""
