"""M-CORE · reach a person on whichever channel they actually signed in with.

A caregiver who joined with a mobile has no email; a kaki who joined with an
email may have no number. Rather than guess, route to the channel they proved
they control, falling back to whichever one exists.

Nothing here raises. A notification failing must never roll back the action
that triggered it — an assignment that happened is still an assignment, and the
coordinator can always phone. Every attempt is written to audit_log so a missed
message can be traced afterwards.

v1.7: each message exists in English and Simplified Chinese; the recipient's
`users.lang` decides. The English subject is what goes to the audit log
whatever the language, so the coordinator reads one language there. Service
names stay English inside Chinese messages: they are the words on the
coordinator's console and on the family's booking, and a kaki who has to phone
the coordinator needs the same word. Anything a person typed (names, reasons)
is never translated.
"""
import html as _html
from .. import assumptions, db
from . import emailer, sms

def _e(x) -> str:
    """Anything user-typed that ends up in an email body."""
    return _html.escape(str(x or ""), quote=True)

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

def lang_of(user: dict | None) -> str:
    """'zh' if the person chose Chinese in the app, else 'en'."""
    return "zh" if (user or {}).get("lang") == "zh" else "en"

def notify(user: dict, subject: str, sms_text: str, email_html: str | None = None,
           log_subject: str | None = None) -> dict:
    """→ {'channel': ..., 'sent': bool}. Safe to call from anywhere.
    `log_subject` is the English line for audit_log when `subject` is not."""
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
                 "notified" if sent else "notify_failed", f"{channel}: {log_subject or subject}")
    except Exception:
        pass
    return {"channel": channel, "sent": sent}

def _pick(user: dict, en: dict, zh: dict) -> dict:
    """Send the zh variant to a zh recipient; the audit log keeps the en subject."""
    if lang_of(user) == "zh":
        return notify(user, zh["subject"], zh["sms"], zh.get("email"), log_subject=en["subject"])
    return notify(user, en["subject"], en["sms"], en.get("email"))

def _hours_zh(hours: float) -> str:
    return f"{hours:g} 小时"

# ---- assignment ------------------------------------------------------------

def visit_assigned(visit: dict, kaki: dict, caregiver: dict, senior_name: str = "") -> dict:
    """Tell both sides a match has been made. Called on manual and auto assign."""
    when = f"{visit.get('date', '')} {visit.get('time_window') or ''}".strip()
    service = visit.get("service", "a visit")
    who = senior_name or "the senior"
    who_zh = senior_name or "长者"
    # Hours and a one-line task description, so the kaki knows what they are
    # saying yes to before they open the app (asked for by every source on 21 Aug).
    meta = assumptions.service(service) or {}
    try:
        hours = float(visit.get("hours") or meta.get("hours") or assumptions.default_hours())
    except (TypeError, ValueError):
        hours = float(assumptions.default_hours())
    hours_txt = f"{hours:g} hr{'' if hours == 1 else 's'}"
    task = (meta.get("note") or "").strip()
    kname = kaki.get("name") or "a kaki"

    kaki_res = _pick(kaki,
        en=dict(subject=f"You've been matched: {service} · {hours_txt}",
                sms=(f"Kakis: {service} for {who}, {when} ({hours_txt}). {task} "
                     f"Open the app to accept.").replace("  ", " "),
                email=(f"<p>You've been matched to a <b>{service}</b> visit for {who}.</p>"
                       f"<p><b>When:</b> {when} · <b>{hours_txt}</b></p>"
                       + (f"<p><b>The task:</b> {task}</p>" if task else "")
                       + f"<p>Open Kakis to accept or pass it back to the coordinator.</p>")),
        zh=dict(subject=f"已为您安排探访：{service} · {_hours_zh(hours)}",
                sms=(f"Kakis：已为您安排 {who_zh} 的探访（{service}），{when}，{_hours_zh(hours)}。"
                     + (f"任务：{task} " if task else "")
                     + "请打开应用接受。").replace("  ", " "),
                email=(f"<p>已为您安排 {who_zh} 的 <b>{service}</b> 探访。</p>"
                       f"<p><b>时间：</b>{when} · <b>{_hours_zh(hours)}</b></p>"
                       + (f"<p><b>任务：</b>{task}</p>" if task else "")
                       + "<p>请打开 Kakis 接受，或退回给协调员。</p>")))
    cg_res = _pick(caregiver,
        en=dict(subject=f"A kaki has been matched: {service}",
                sms=(f"Kakis: {kname} has been matched to your {service.lower()} "
                     f"for {who}, {when}. Open the app for details."),
                email=(f"<p><b>{kname}</b> has been matched to your "
                       f"<b>{service}</b> visit for {who}.</p>"
                       f"<p><b>When:</b> {when}</p>"
                       f"<p>Open Kakis to see their profile and the 4-digit start code.</p>")),
        zh=dict(subject=f"已为您配对 Kaki：{service}",
                sms=f"Kakis：已为 {who_zh} 的探访（{service}，{when}）安排 Kaki {kname}。请打开应用查看详情。",
                email=(f"<p>已为 {who_zh} 的 <b>{service}</b> 探访安排 Kaki <b>{kname}</b>。</p>"
                       f"<p><b>时间：</b>{when}</p>"
                       "<p>请打开 Kakis 查看 Kaki 的资料。Kaki 到门口时，先核对照片和 Kaki 验证码，再把开始码读给他/她。</p>")))
    return {"kaki": kaki_res, "caregiver": cg_res}

# ---- lifecycle after assignment (v1.6) --------------------------------------
# On 21 Aug caregivers refreshed the page to learn whether anything had
# happened. Each state change now tells the side that did not cause it.

def _when(visit: dict) -> str:
    return f"{visit.get('date', '')} {visit.get('time_window') or ''}".strip()

def visit_accepted(visit: dict, kaki: dict, caregiver: dict, senior_name: str = "") -> dict:
    who, name = senior_name or "the senior", (kaki or {}).get("name") or "Your kaki"
    who_zh, name_zh = senior_name or "长者", (kaki or {}).get("name") or "您的 Kaki"
    svc = visit.get("service") or "visit"
    return _pick(caregiver,
        en=dict(subject=f"{name} confirmed: {visit.get('service', 'your visit')}",
                sms=(f"Kakis: {name} has confirmed the {svc.lower()} "
                     f"for {who}, {_when(visit)}. The start code is on your visit page."),
                email=(f"<p><b>{name}</b> has confirmed the <b>{visit.get('service')}</b> visit "
                       f"for {who}.</p><p><b>When:</b> {_when(visit)}</p>"
                       f"<p>Open Kakis to see their photo and the 4-digit start code.</p>")),
        zh=dict(subject=f"{name_zh} 已确认：{svc}",
                sms=(f"Kakis：{name_zh} 已确认 {who_zh} 的探访（{svc}），{_when(visit)}。"
                     "开始码在您的探访页面。"),
                email=(f"<p><b>{name_zh}</b> 已确认 {who_zh} 的 <b>{svc}</b> 探访。</p>"
                       f"<p><b>时间：</b>{_when(visit)}</p>"
                       "<p>请打开 Kakis 查看 Kaki 的照片和 4 位数开始码。</p>")))

def visit_declined(visit: dict, kaki: dict, caregiver: dict, senior_name: str = "") -> dict:
    who, name = senior_name or "the senior", (kaki or {}).get("name") or "The kaki"
    who_zh, name_zh = senior_name or "长者", (kaki or {}).get("name") or "Kaki"
    svc = visit.get("service") or "visit"
    return _pick(caregiver,
        en=dict(subject=f"Finding another kaki: {visit.get('service', 'your visit')}",
                sms=(f"Kakis: {name} passed the {svc.lower()} for {who} "
                     f"back to the coordinator, who is finding someone else now. Nothing to do."),
                email=(f"<p>{name} passed the <b>{visit.get('service')}</b> visit for {who} back "
                       f"to the coordinator, who is finding someone else now.</p><p>Nothing to do.</p>")),
        zh=dict(subject=f"正在另找 Kaki：{svc}",
                sms=(f"Kakis：{name_zh} 把 {who_zh} 的探访（{svc}）退回给了协调员，协调员正在另找他人。"
                     "您不需要做什么。"),
                email=(f"<p>{name_zh} 把 {who_zh} 的 <b>{svc}</b> 探访退回给了协调员，协调员正在另找他人。</p>"
                       "<p>您不需要做什么。</p>")))

def visit_cancelled(visit: dict, by_role: str, kaki: dict, caregiver: dict,
                    senior_name: str = "", reason: str = "") -> dict:
    """Tell the side that did not cancel."""
    who = _e(senior_name or "the senior")
    who_zh = _e(senior_name or "长者")
    why = f" Reason: {_e(reason)}" if reason else ""
    why_zh = f"原因：{_e(reason)}。" if reason else ""
    svc = visit.get("service") or "visit"
    if by_role == "caregiver":
        return _pick(kaki,
            en=dict(subject=f"Cancelled: {visit.get('service', 'visit')} for {who}",
                    sms=(f"Kakis: the family cancelled the {svc.lower()} "
                         f"for {who}, {_when(visit)}.{why} No need to travel."),
                    email=(f"<p>The family cancelled the <b>{visit.get('service')}</b> visit for {who}, "
                           f"{_when(visit)}.{why}</p><p>No need to travel.</p>")),
            zh=dict(subject=f"已取消：{who_zh} 的探访（{svc}）",
                    sms=f"Kakis：家属取消了 {who_zh} 的探访（{svc}），{_when(visit)}。{why_zh}不用前往。",
                    email=(f"<p>家属取消了 {who_zh} 的 <b>{svc}</b> 探访，{_when(visit)}。{why_zh}</p>"
                           "<p>不用前往。</p>")))
    if by_role == "admin":
        cg_res = _pick(caregiver,
            en=dict(subject=f"Cancelled by the coordinator: {visit.get('service', 'your visit')}",
                    sms=f"Kakis: the coordinator cancelled the {svc.lower()} for {who}, {_when(visit)}.{why} Call 6XXX XXXX with any questions."),
            zh=dict(subject=f"协调员已取消：{svc}",
                    sms=f"Kakis：协调员取消了 {who_zh} 的探访（{svc}），{_when(visit)}。{why_zh}有疑问请致电 6XXX XXXX。"))
        _pick(kaki,
            en=dict(subject=f"Cancelled by the coordinator: {visit.get('service', 'visit')} for {who}",
                    sms=f"Kakis: the coordinator cancelled the {svc.lower()} for {who}, {_when(visit)}.{why} No need to travel."),
            zh=dict(subject=f"协调员已取消：{who_zh} 的探访（{svc}）",
                    sms=f"Kakis：协调员取消了 {who_zh} 的探访（{svc}），{_when(visit)}。{why_zh}不用前往。"))
        return cg_res
    name = _e((kaki or {}).get("name") or "Your kaki")
    name_zh = _e((kaki or {}).get("name") or "您的 Kaki")
    return _pick(caregiver,
        en=dict(subject=f"{name} had to cancel: {visit.get('service', 'your visit')}",
                sms=(f"Kakis: {name} had to cancel the {svc.lower()} for {who}, "
                     f"{_when(visit)}.{why} The coordinator has been told."),
                email=(f"<p><b>{name}</b> had to cancel the <b>{visit.get('service')}</b> visit for {who}, "
                       f"{_when(visit)}.{why}</p><p>The coordinator has been told.</p>")),
        zh=dict(subject=f"{name_zh} 不得不取消：{svc}",
                sms=f"Kakis：{name_zh} 不得不取消 {who_zh} 的探访（{svc}），{_when(visit)}。{why_zh}协调员已收到通知。",
                email=(f"<p><b>{name_zh}</b> 不得不取消 {who_zh} 的 <b>{svc}</b> 探访，{_when(visit)}。{why_zh}</p>"
                       "<p>协调员已收到通知。</p>")))

def visit_on_the_way(visit: dict, kaki: dict, caregiver: dict, senior_name: str = "") -> dict:
    who, name = senior_name or "the senior", (kaki or {}).get("name") or "Your kaki"
    who_zh, name_zh = senior_name or "长者", (kaki or {}).get("name") or "您的 Kaki"
    return _pick(caregiver,
        en=dict(subject=f"{name} is on the way",
                sms=f"Kakis: {name} is on the way to {who} now. Have the 4-digit start code ready.",
                email=(f"<p><b>{name}</b> is on the way to {who} now.</p>"
                       f"<p>Have the 4-digit start code ready on your visit page.</p>")),
        zh=dict(subject=f"{name_zh} 正在路上",
                sms=f"Kakis：{name_zh} 正在前往 {who_zh} 那里。请准备好 4 位数开始码。",
                email=(f"<p><b>{name_zh}</b> 正在前往 {who_zh} 那里。</p>"
                       "<p>请在探访页面准备好 4 位数开始码。</p>")))

# ---- the emergency contact (v1.6) -------------------------------------------
# Not a user: a name and a number on the care plan. SMS only; never raises.
# v1.7: the contact has no account, so the caregiver's language is used —
# they are the same household.

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

def visit_started_contact(visit: dict, kaki: dict, senior_name: str, plan: dict, caregiver: dict | None = None) -> bool:
    if not plan or not plan.get("contact_phone"):
        return False
    svc = (visit.get("service") or "visit")
    if lang_of(caregiver) == "zh":
        name = (kaki or {}).get("name") or "Kakis 的帮手"
        who = senior_name or "您的家人"
        return contact_sms(plan["contact_phone"],
                           f"Kakis：{name} 已开始 {who} 的探访（{svc}）。探访结束时您会再收到一条信息。")
    name = (kaki or {}).get("name") or "A Kakis helper"
    who = senior_name or "your family member"
    return contact_sms(plan["contact_phone"],
                       f"Kakis: {name} has started a {svc.lower()} with {who}. "
                       f"You'll get another message when it finishes.")

def visit_finished_contact(visit: dict, kaki: dict, senior_name: str, plan: dict, caregiver: dict | None = None) -> bool:
    if not plan or not plan.get("contact_phone"):
        return False
    if lang_of(caregiver) == "zh":
        name = (kaki or {}).get("name") or "Kakis 的帮手"
        who = senior_name or "您的家人"
        return contact_sms(plan["contact_phone"],
                           f"Kakis：{name} 已完成 {who} 的探访。家属可以在应用里查看报告。")
    name = (kaki or {}).get("name") or "The Kakis helper"
    who = senior_name or "your family member"
    return contact_sms(plan["contact_phone"],
                       f"Kakis: {name} has finished the visit with {who}. The family can read the report in the app.")
