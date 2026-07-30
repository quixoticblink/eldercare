"""M-CORE · configuration. Env vars only — no logic."""
import os

def env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()

JWT_SECRET     = env("JWT_SECRET", "dev-secret-change-me")
ADMIN_EMAILS   = [e.strip().lower() for e in env("ADMIN_EMAILS", "abhishekkaul@gmail.com").split(",") if e.strip()]
RESEND_API_KEY = env("RESEND_API_KEY")
MAIL_FROM      = env("MAIL_FROM", "Kakis <onboarding@resend.dev>")
DEV_MODE       = env("DEV_MODE", "1") == "1"
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY")
LLM_MODEL      = env("LLM_MODEL", "claude-sonnet-4-5")
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
