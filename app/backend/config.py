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
DEV_MODE       = env("DEV_MODE", "1") == "1"

# M-AUTH · SMS channel. Sign-in codes go out over AWS SNS when SMS_ENABLED=1;
# until then codes fall back to the DEV_MODE path exactly like email does.
# SNS notes for go-live: the account starts in the SMS sandbox (only verified
# numbers receive messages), and Singapore requires a registered Sender ID.
SMS_ENABLED    = env("SMS_ENABLED", "0") == "1"
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

SERVICES = ["Chaperone", "Companionship", "Wellness check", "Household help"]
# est hours, family rate $/hr, kaki rate $/hr — pilot estimates for the price stack
SERVICE_META = {
    "Chaperone":       {"hours": 3, "rate": 28, "kaki_rate": 12},
    "Companionship":   {"hours": 2, "rate": 24, "kaki_rate": 11},
    "Wellness check":  {"hours": 1, "rate": 24, "kaki_rate": 12},
    "Household help":  {"hours": 2, "rate": 22, "kaki_rate": 10},
}
TRIGGERS = ["Helper left suddenly", "Spouse hospitalised", "My own emergency",
            "Discharge, no plan", "Sudden decline", "Loss of a spouse"]
LOCKED_SERVICES = ["Medicine administration"]  # Tier 2 — visible, not bookable in v1
TIERS = ["urgent", "soon", "planned"]
LANGUAGES = ["English", "Mandarin", "Malay", "Tamil", "Hokkien"]
