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

# ---- lifecycle after assignment (v1.6) --------------------------------------
# On 21 Aug caregivers refreshed the page to learn whether anything had
# happened. Each state change now tells the side that did not cause it.

def _when(visit: dict) -> str:
    return f"{visit.get('date', '')} {visit.get('time_window') or ''}".strip()

def visit_accepted(visit: dict, kaki: dict, caregiver: dict, senior_name: str = "") -> dict:
    who, name = senior_name or "the senior", (kaki or {}).get("name") or "Your kaki"
    return notify(
        caregiver,
        subject=f"{name} confirmed: {visit.get('service', 'your visit')}",
        sms_text=(f"Kakis: {name} has confirmed the {(visit.get('service') or 'visit').lower()} "
                  f"for {who}, {_when(visit)}. The start code is on your visit page."),
        email_html=(f"<p><b>{name}</b> has confirmed the <b>{visit.get('service')}</b> visit "
                    f"for {who}.</p><p><b>When:</b> {_when(visit)}</p>"
                    f"<p>Open Kakis to see their photo and the 4-digit start code.</p>"),
    )

def visit_declined(visit: dict, kaki: dict, caregiver: dict, senior_name: str = "") -> dict:
    who, name = senior_name or "the senior", (kaki or {}).get("name") or "The kaki"
    return notify(
        caregiver,
        subject=f"Finding another kaki: {visit.get('service', 'your visit')}",
        sms_text=(f"Kakis: {name} passed the {(visit.get('service') or 'visit').lower()} for {who} "
                  f"back to the coordinator, who is finding someone else now. Nothing to do."),
        email_html=(f"<p>{name} passed the <b>{visit.get('service')}</b> visit for {who} back "
                    f"to the coordinator, who is finding someone else now.</p><p>Nothing to do.</p>"),
    )

def visit_cancelled(visit: dict, by_role: str, kaki: dict, caregiver: dict,
                    senior_name: str = "", reason: str = "") -> dict:
    """Tell the side that did not cancel."""
    who = senior_name or "the senior"
    why = f" Reason: {reason}" if reason else ""
    if by_role == "caregiver":
        return notify(
            kaki,
            subject=f"Cancelled: {visit.get('service', 'visit')} for {who}",
            sms_text=(f"Kakis: the family cancelled the {(visit.get('service') or 'visit').lower()} "
                      f"for {who}, {_when(visit)}.{why} No need to travel."),
            email_html=(f"<p>The family cancelled the <b>{visit.get('service')}</b> visit for {who}, "
                        f"{_when(visit)}.{why}</p><p>No need to travel.</p>"),
        )
    name = (kaki or {}).get("name") or "Your kaki"
    return notify(
        caregiver,
        subject=f"{name} had to cancel: {visit.get('service', 'your visit')}",
        sms_text=(f"Kakis: {name} had to cancel the {(visit.get('service') or 'visit').lower()} for {who}, "
                  f"{_when(visit)}.{why} The coordinator has been told."),
        email_html=(f"<p><b>{name}</b> had to cancel the <b>{visit.get('service')}</b> visit for {who}, "
                    f"{_when(visit)}.{why}</p><p>The coordinator has been told.</p>"),
    )
