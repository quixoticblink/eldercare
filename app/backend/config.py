"""M-CORE · configuration. Env vars only — no logic."""
import os

def env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()

JWT_SECRET     = env("JWT_SECRET", "dev-secret-change-me")
ADMIN_EMAILS   = [e.strip().lower() for e in env("ADMIN_EMAILS", "abhishekkaul@gmail.com").split(",") if e.strip()]
# Admins may also be recognised by mobile number, so a coordinator can sign in
# without an email. Store in full E.164, e.g. ADMIN_PHONES="+6591234567".
ADMIN_PHONES   = [p.strip() for p in env("ADMIN_PHONES").split(",") if p.strip()]
RESEND_API_KEY = env("RESEND_API_KEY")
MAIL_FROM      = env("MAIL_FROM", "Kakis <onboarding@resend.dev>")
# Sending through Resend needs DNS records, not a mailbox — so MAIL_FROM can be
# an address that cannot receive. Point replies somewhere real, or they bounce.
MAIL_REPLY_TO  = env("MAIL_REPLY_TO")
DEV_MODE       = env("DEV_MODE", "1") == "1"

# M-AUTH · SMS channel. Sign-in codes go out over AWS SNS when SMS_ENABLED=1;
# until then codes fall back to the DEV_MODE path exactly like email does.
# SNS notes for go-live: the account starts in the SMS sandbox (only verified
# numbers receive messages), and Singapore requires a registered Sender ID.
SMS_ENABLED    = env("SMS_ENABLED", "0") == "1"

# DEMO BACKDOOR — read this before adding anything here.
# Identifiers on this list get their sign-in code returned in the API response
# and shown on screen, even when DEV_MODE=0. It exists so the app can be
# demonstrated without a working SMS provider.
#
# Anyone who knows a listed identifier can sign in as that account from the
# public site. Treat every entry as a shared password. Never list an identifier
# belonging to a real user, and empty this list once SMS delivery works.
# Phone numbers must be full E.164, e.g. "+6598553704".
DEMO_IDENTIFIERS = [d.strip().lower() for d in env("DEMO_IDENTIFIERS").split(",") if d.strip()]

def is_demo_identifier(value: str) -> bool:
    return bool(value) and value.strip().lower() in DEMO_IDENTIFIERS
AWS_REGION     = env("AWS_REGION", "ap-southeast-1")
SMS_SENDER_ID  = env("SMS_SENDER_ID", "Kakis")
DEFAULT_COUNTRY_CODE = env("DEFAULT_COUNTRY_CODE", "+65")   # bare 8-digit numbers are Singapore
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY")
OPENAI_API_KEY = env("OPENAI_API_KEY")
LLM_MODEL      = env("LLM_MODEL", "claude-sonnet-4-5")
OPENAI_MODEL   = env("OPENAI_MODEL", "gpt-4o-mini")
DB_PATH        = env("DB_PATH", "./kakis.duckdb")
CORS_ORIGINS   = [o.strip() for o in env("CORS_ORIGINS", "*").split(",")]
PORT           = int(env("PORT", "8000"))
TOKEN_DAYS     = 30
OTP_MINUTES    = 10

# The bookable services and their rates come from assumptions.json — one file,
# one source of truth, editable without a deploy. The literal list below is only
# a fallback for when that file is missing.
from . import assumptions as _assumptions          # noqa: E402  (stdlib-only import)

SERVICES = list(_assumptions.services().keys()) or [
    "Chaperone", "Companionship", "Wellness check", "Household help"]

# Availability is captured in half-days rather than exact hours — realistic for
# kakis who are also employed elsewhere.
HALF_DAYS = ["morning", "afternoon"]
WEEKDAYS  = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
TRIGGERS = ["Helper left suddenly", "Spouse hospitalised", "My own emergency",
            "Discharge, no plan", "Sudden decline", "Loss of a spouse"]
LOCKED_SERVICES = ["Medicine administration"]  # Tier 2 — visible, not bookable in v1
TIERS = ["urgent", "soon", "planned"]
LANGUAGES = ["English", "Mandarin", "Malay", "Tamil", "Hokkien"]
