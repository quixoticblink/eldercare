"""M-AUTH · outbound messages. Resend for email today; add SMS provider here later."""
import httpx
from .. import config

def send_otp_email(to: str, code: str) -> dict:
    """Returns {"sent": bool, "dev_code": code|None}. In DEV_MODE (or without a
    Resend key) the code is returned to the API so the app works pre-configuration."""
    if config.RESEND_API_KEY:
        try:
            payload = {
                    "from": config.MAIL_FROM,
                    "to": [to],
                    "subject": f"{code} is your Kakis sign-in code",
                    "html": f"""
                      <div style="font-family:sans-serif;max-width:420px;margin:auto">
                        <h2 style="color:#0C3D33">Kakis<span style="color:#F0A63C">.</span></h2>
                        <p>Your sign-in code:</p>
                        <p style="font-size:34px;letter-spacing:8px;font-weight:700;color:#14594A">{code}</p>
                        <p style="color:#5E6B65">It expires in {config.OTP_MINUTES} minutes.
                        If you didn't request this, ignore this email.</p>
                      </div>""",
            }
            if config.MAIL_REPLY_TO:
                payload["reply_to"] = config.MAIL_REPLY_TO
            r = httpx.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {config.RESEND_API_KEY}"},
                json=payload,
                timeout=15,
            )
            ok = r.status_code < 300
            return {"sent": ok, "dev_code": code if (config.DEV_MODE and not ok) else None}
        except Exception:
            return {"sent": False, "dev_code": code if config.DEV_MODE else None}
    # No key configured: dev fallback
    print(f"[kakis DEV] OTP for {to}: {code}")
    return {"sent": False, "dev_code": code if config.DEV_MODE else None}

def send_email(to: str, subject: str, body_html: str) -> bool:
    """Generic transactional email (notifications, not codes). Returns success.
    Never raises — a failed notification must not break the action that
    triggered it."""
    if not config.RESEND_API_KEY:
        print(f"[kakis DEV] email to {to}: {subject}")
        return False
    payload = {
        "from": config.MAIL_FROM,
        "to": [to],
        "subject": subject,
        "html": f"""<div style="font-family:sans-serif;max-width:460px;margin:auto">
            <h2 style="color:#0C3D33">Kakis<span style="color:#F0A63C">.</span></h2>
            {body_html}
            <p style="color:#5E6B65;font-size:.8rem;margin-top:18px">
              Questions? Call the Pasir Ris ICCP coordinator on 6XXX XXXX.</p>
          </div>""",
    }
    if config.MAIL_REPLY_TO:
        payload["reply_to"] = config.MAIL_REPLY_TO
    try:
        r = httpx.post("https://api.resend.com/emails",
                       headers={"Authorization": f"Bearer {config.RESEND_API_KEY}"},
                       json=payload, timeout=15)
        return r.status_code < 300
    except Exception as e:
        print(f"[kakis] email to {to} failed: {e}")
        return False
