"""M-CORE · reach a person on whichever channel they actually signed in with.

A caregiver who joined with a mobile has no email; a kaki who joined with an
email may have no number. Rather than guess, route to the channel they proved
they control, falling back to whichever one exists.

Nothing here raises. A notification failing must never roll back the action
that triggered it — an assignment that happened is still an assignment, and the
coordinator can always phone. Every attempt is written to audit_log so a missed
message can be traced afterwards.
"""
from .. import assumptions, db
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
    # Hours and a one-line task description, so the kaki knows what they are
    # saying yes to before they open the app (asked for by every source on 21 Aug).
    meta = assumptions.service(service) or {}
    try:
        hours = float(visit.get("hours") or meta.get("hours") or assumptions.default_hours())
    except (TypeError, ValueError):
        hours = float(assumptions.default_hours())
    hours_txt = f"{hours:g} hr{'' if hours == 1 else 's'}"
    task = (meta.get("note") or "").strip()

    kaki_res = notify(
        kaki,
        subject=f"You've been matched: {service} · {hours_txt}",
        sms_text=(f"Kakis: {service} for {who}, {when} ({hours_txt}). {task} "
                  f"Open the app to accept.").replace("  ", " "),
        email_html=(f"<p>You've been matched to a <b>{service}</b> visit for {who}.</p>"
                    f"<p><b>When:</b> {when} · <b>{hours_txt}</b></p>"
                    + (f"<p><b>The task:</b> {task}</p>" if task else "")
                    + f"<p>Open Kakis to accept or pass it back to the coordinator.</p>"),
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
    if by_role == "admin":
        cg_res = notify(caregiver, subject=f"Cancelled by the coordinator: {visit.get('service', 'your visit')}",
                        sms_text=f"Kakis: the coordinator cancelled the {(visit.get('service') or 'visit').lower()} for {who}, {_when(visit)}.{why} Call 6XXX XXXX with any questions.")
        notify(kaki, subject=f"Cancelled by the coordinator: {visit.get('service', 'visit')} for {who}",
               sms_text=f"Kakis: the coordinator cancelled the {(visit.get('service') or 'visit').lower()} for {who}, {_when(visit)}.{why} No need to travel.")
        return cg_res
    name = (kaki or {}).get("name") or "Your kaki"
    return notify(
        caregiver,
        subject=f"{name} had to cancel: {visit.get('service', 'your visit')}",
        sms_text=(f"Kakis: {name} had to cancel the {(visit.get('service') or 'visit').lower()} for {who}, "
                  f"{_when(visit)}.{why} The coordinator has been told."),
        email_html=(f"<p><b>{name}</b> had to cancel the <b>{visit.get('service')}</b> visit for {who}, "
                    f"{_when(visit)}.{why}</p><p>The coordinator has been told.</p>"),
    )

def visit_on_the_way(visit: dict, kaki: dict, caregiver: dict, senior_name: str = "") -> dict:
    who, name = senior_name or "the senior", (kaki or {}).get("name") or "Your kaki"
    return notify(
        caregiver,
        subject=f"{name} is on the way",
        sms_text=f"Kakis: {name} is on the way to {who} now. Have the 4-digit start code ready.",
        email_html=(f"<p><b>{name}</b> is on the way to {who} now.</p>"
                    f"<p>Have the 4-digit start code ready on your visit page.</p>"),
    )

# ---- the emergency contact (v1.6) -------------------------------------------
# Not a user: a name and a number on the care plan. SMS only; never raises.

def contact_sms(phone: str, text: str, actor: str = "care-plan-contact") -> bool:
    phone = (phone or "").strip()
    if not phone:
        return False
    try:
        sent = bool(sms.send_sms(phone, text))
    except Exception as e:
        print(f"[kakis] contact sms to {phone} failed: {e}")
        sent = False
    try:
        db.audit(actor, "contact_notified" if sent else "contact_notify_failed", phone)
    except Exception:
        pass
    return sent

def visit_started_contact(visit: dict, kaki: dict, senior_name: str, plan: dict) -> bool:
    if not plan or not plan.get("contact_phone"):
        return False
    name = (kaki or {}).get("name") or "A Kakis helper"
    who = senior_name or "your family member"
    return contact_sms(plan["contact_phone"],
                       f"Kakis: {name} has started a {(visit.get('service') or 'visit').lower()} with {who}. "
                       f"You'll get another message when it finishes.")

def visit_finished_contact(visit: dict, kaki: dict, senior_name: str, plan: dict) -> bool:
    if not plan or not plan.get("contact_phone"):
        return False
    name = (kaki or {}).get("name") or "The Kakis helper"
    who = senior_name or "your family member"
    return contact_sms(plan["contact_phone"],
                       f"Kakis: {name} has finished the visit with {who}. The family can read the report in the app.")
