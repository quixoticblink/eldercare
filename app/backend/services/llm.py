"""M-HELP · chatbot brain. Claude or OpenAI via API if a key is set; keyword guide otherwise."""
import httpx
from .. import config

HELP_GUIDE = {
    "sign in": "Enter your email, then type the 6-digit code we send you. No password needed. New accounts wait for the coordinator's approval.",
    "approval": "After your first sign-in, the Kakis coordinator reviews and approves your account — usually within a day. You'll see the waiting screen until then.",
    "book": "Caregivers: Home → Book a visit → pick the service → pick when (Urgent / Soon / Planned) → add details → submit. The coordinator matches a kaki and you'll see it under Visits.",
    "urgent": "Urgent means you need someone within the hour — e.g. your helper left suddenly. The coordinator prioritises these requests first.",
    "otp": "When the kaki arrives, the caregiver's visit page shows a 4-digit start code. The kaki enters it to start the visit — that's how we confirm they're really there.",
    "start code": "Open the visit in your Visits tab — the start code is on the visit page. Read it to your kaki when they arrive.",
    "report": "Kakis: after ending a visit, tick the chips and add a short note. Caregivers see the report on the visit page.",
    "care plan": "Caregivers: Home → Care plan. Keep meds, mobility and languages current — every kaki sees it before a visit.",
    "cancel": "Open the visit and tap Cancel. Please cancel at least 2 hours ahead so the kaki isn't already travelling.",
    "pay": "During the pilot there's nothing to pay in the app — billing runs through the Vanguard / ICCP account.",
    "earnings": "Kakis: your Impact tab shows hours and amounts. Payouts run weekly via Vanguard during the pilot.",
    "contact": "Stuck? Call the Pasir Ris ICCP coordinator at 6XXX XXXX.",
}

SYSTEM_PROMPT = """You are the in-app helper for Kakis, a Singapore pilot app where family
caregivers book trusted respite visits for elderly parents, trained "kakis" (respite givers)
serve those visits, and a coordinator approves users and matches visits manually.
Answer briefly (2-4 sentences), warmly, in plain language. App facts:
- Sign-in: email + 6-digit code. New users need coordinator approval.
- Caregivers: set up household + care plan; book visits (service -> urgency Urgent/Soon/Planned -> details); see assigned kaki; visit page shows a 4-digit start code to read to the kaki; get a report after.
- Kakis: see assigned visits, accept, start with the code, end with a short report. Impact tab shows hours/earnings; weekly payout via Vanguard.
- No payments in-app during the pilot (billed via ICCP account). No public ratings of kakis (MOH rule) - concerns go privately to the care team.
- Coordinator phone: 6XXX XXXX. If you don't know, say so and point to the coordinator."""

def _recent(history: list) -> list:
    return [{"role": m.get("role", "user"), "content": m.get("content", "")}
            for m in (history or [])[-6:]]

def _anthropic(message: str, history: list) -> str | None:
    msgs = _recent(history) + [{"role": "user", "content": message}]
    r = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": config.ANTHROPIC_API_KEY,
                 "anthropic-version": "2023-06-01"},
        json={"model": config.LLM_MODEL, "max_tokens": 400,
              "system": SYSTEM_PROMPT, "messages": msgs},
        timeout=30,
    )
    if r.status_code < 300:
        return r.json()["content"][0]["text"]
    return None

def _openai(message: str, history: list) -> str | None:
    msgs = ([{"role": "system", "content": SYSTEM_PROMPT}]
            + _recent(history)
            + [{"role": "user", "content": message}])
    r = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {config.OPENAI_API_KEY}"},
        json={"model": config.OPENAI_MODEL, "max_tokens": 400, "messages": msgs},
        timeout=30,
    )
    if r.status_code < 300:
        return r.json()["choices"][0]["message"]["content"]
    return None

def reply(message: str, history: list) -> str:
    # Anthropic first if configured, then OpenAI, then the keyword guide.
    for key, fn in ((config.ANTHROPIC_API_KEY, _anthropic),
                    (config.OPENAI_API_KEY, _openai)):
        if not key:
            continue
        try:
            out = fn(message, history)
            if out:
                return out
        except Exception:
            pass
    # keyword fallback
    m = message.lower()
    for key, answer in HELP_GUIDE.items():
        if key in m:
            return answer
    return ("Here's what I can help with: signing in, approval, booking a visit, "
            "the start code, reports, care plans, cancelling, and earnings. "
            "Try one of those words — or call the coordinator at 6XXX XXXX.")
