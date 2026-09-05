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
from .. import config, db

# (limit, window minutes) — tuned for elderly users who genuinely do mistype
# and re-request, while still closing off automated abuse. Overridable by env so
# a session can be widened without a code change.
#
# The per-IP cap is the one that bites in the real world. Everyone in a room
# shares one public address: a team test, or the tabletop exercise with five
# sets of senior + micro-jobber + coordinator, is fifteen-plus people signing in
# within minutes from a single IP. A cap of 20 would lock the room out halfway
# through and look exactly like the app being broken, during the session where
# it is being judged. So the per-IP number is deliberately loose; the real
# protection against targeted abuse is the per-identifier cap, which is not
# affected by how many other people share the network.
def _int(name: str, default: int) -> int:
    try:
        return max(1, int(config.env(name, str(default))))
    except (TypeError, ValueError):
        return default

WINDOW_MIN = _int("RATE_LIMIT_WINDOW_MIN", 15)

LIMITS = {
    "request_code_identifier": (_int("RATE_LIMIT_CODE_PER_IDENTIFIER", 5), WINDOW_MIN),
    "request_code_ip":         (_int("RATE_LIMIT_CODE_PER_IP", 200), WINDOW_MIN),
    "verify_failure":          (_int("RATE_LIMIT_VERIFY_FAILURES", 5), WINDOW_MIN),
    # v1.6: the two 4-digit door codes (kaki code, start code) — 10,000 guesses
    # is an afternoon for a script. Keyed per visit.
    "visit_code":              (_int("RATE_LIMIT_VISIT_CODE", 5), WINDOW_MIN),
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
