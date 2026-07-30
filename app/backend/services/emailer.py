"""M-AUTH · outbound messages. Resend for email today; add SMS provider here later."""
import httpx
from .. import config

def send_otp_email(to: str, code: str) -> dict:
    """Returns {"sent": bool, "dev_code": code|None}. In DEV_MODE (or without a
    Resend key) the code is returned to the API so the app works pre-configuration."""
    if config.RESEND_API_KEY:
        try:
            r = httpx.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {config.RESEND_API_KEY}"},
                json={
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
                },
                timeout=15,
            )
            ok = r.status_code < 300
            return {"sent": ok, "dev_code": code if (config.DEV_MODE and not ok) else None}
        except Exception:
            return {"sent": False, "dev_code": code if config.DEV_MODE else None}
    # No key configured: dev fallback
    print(f"[kakis DEV] OTP for {to}: {code}")
    return {"sent": False, "dev_code": code if config.DEV_MODE else None}
