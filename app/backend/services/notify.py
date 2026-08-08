"""M-CORE · reach a person on whichever channel they actually signed in with.

A caregiver who joined with a mobile has no email; a kaki who joined with an
email may have no number. Rather than guess, route to the channel they proved
they control, falling back to whichever one exists.

Nothing here raises. A notification failing must never roll back the action
that triggered it — an assignment that happened is still an assignment, and the
coordinator can always phone. Every attempt is written to audit_log so a missed
message can be traced afterwards.
"""
from .. import db
from . import emailer, sms

def channel_for(user: dict) -> str | None:
    """'sms' | 'email' | None — prefer a verified channel over an unverified one."""
    phone, email = (user.get("phone") or "").strip(), (user.get("email") or "").strip()
    if user.get("phone_verified") and phone:
        return "sms"
    if user.get("email_verified") and email:
        return "email"
    if phone:
        return "sms"
    if email:
        return "email"
    return None

def notify(user: dict, subject: str, sms_text: str, email_html: str | None = None) -> dict:
    """→ {'channel': ..., 'sent': bool}. Safe to call from anywhere."""
    if not user:
        return {"channel": None, "sent": False}
    channel = channel_for(user)
    sent = False
    try:
        if channel == "sms":
            sent = sms.send_sms(user["phone"].strip(), sms_text)
        elif channel == "email":
            sent = emailer.send_email(user["email"].strip(), subject,
                                      email_html or f"<p>{sms_text}</p>")
    except Exception as e:                      # belt and braces
        print(f"[kakis] notify failed for {user.get('id')}: {e}")
        sent = False
    try:
        db.audit(user.get("email") or user.get("phone") or user.get("id", "?"),
                 "notified" if sent else "notify_failed", f"{channel}: {subject}")
    except Exception:
        pass
    return {"channel": channel, "sent": sent}

# ---- assignment ------------------------------------------------------------

def visit_assigned(visit: dict, kaki: dict, caregiver: dict, senior_name: str = "") -> dict:
    """Tell both sides a match has been made. Called on manual and auto assign."""
    when = f"{visit.get('date', '')} {visit.get('time_window') or ''}".strip()
    service = visit.get("service", "a visit")
    who = senior_name or "the senior"

    kaki_res = notify(
        kaki,
        subject=f"You've been matched: {service}",
        sms_text=(f"Kakis: you've been matched to a {service.lower()} for {who}, {when}. "
                  f"Open the app to accept."),
        email_html=(f"<p>You've been matched to a <b>{service}</b> visit for {who}.</p>"
                    f"<p><b>When:</b> {when}</p>"
                    f"<p>Open Kakis to accept or pass it back to the coordinator.</p>"),
    )
    cg_res = notify(
        caregiver,
        subject=f"A kaki has been matched: {service}",
        sms_text=(f"Kakis: {kaki.get('name') or 'a kaki'} has been matched to your {service.lower()} "
                  f"for {who}, {when}. Open the app for details."),
        email_html=(f"<p><b>{kaki.get('name') or 'A kaki'}</b> has been matched to your "
                    f"<b>{service}</b> visit for {who}.</p>"
                    f"<p><b>When:</b> {when}</p>"
                    f"<p>Open Kakis to see their profile and the 4-digit start code.</p>"),
    )
    return {"kaki": kaki_res, "caregiver": cg_res}
