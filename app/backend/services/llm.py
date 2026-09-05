"""M-HELP · chatbot brain. Claude or OpenAI via API if a key is set; keyword guide otherwise."""
import httpx
from .. import config

HELP_GUIDE = {
    "sign in": "Enter your email address or your mobile number, then type the 6-digit code we send you. No password needed. If you've signed in before, the six digits are all we ask for. New accounts wait for the coordinator's approval.",
    "approval": "After your first sign-in, the Kakis coordinator reviews and approves your account — usually within a day. You'll see the waiting screen until then.",
    "book": "Caregivers: Home → Book a visit → pick the service → pick when (Urgent / Soon / Planned) → add details → submit. The coordinator matches a kaki and you'll see it under Visits.",
    "urgent": "Urgent means you need someone within the hour — e.g. your helper left suddenly. The coordinator prioritises these requests first.",
    "otp": "When the kaki arrives, the caregiver's visit page shows a 4-digit start code. The kaki enters it to start the visit — that's how we confirm they're really there.",
    "start code": "Caregivers: when your kaki arrives, first enter the 4-digit kaki code from their screen under 'Check it's them' — your start code then appears on the visit page. Read it to your kaki to start the visit.",
    "kaki code": "Kakis: your visit page shows a 4-digit code for the family. Show it (with your photo) at the door; the family enters it, then reads you their start code.",
    "photo": "Kakis: add a photo on your Profile — families see it on the visit page so they know it's you at the door.",
    "certificate": "Kakis: add certificates (CPR + AED, mobility training) on your Profile, as a PDF or a photo. The coordinator checks them before approving you.",
    "report": "Kakis: after ending a visit, tick the chips and add a short note. Caregivers see the report on the visit page.",
    "care plan": "Caregivers: Home → Care plan. Keep meds, mobility and languages current — every kaki sees it before a visit.",
    "cancel": "Open the visit and tap Cancel. Please cancel at least 2 hours ahead so the kaki isn't already travelling.",
    "pay": "During the pilot there's nothing to pay in the app — billing runs through the Vanguard / ICCP account.",
    "earnings": "Kakis: your Impact tab shows hours and amounts. Payouts run weekly via Vanguard during the pilot.",
    "contact": "Stuck? Call the Pasir Ris ICCP coordinator at 6XXX XXXX.",
    "open": "You don't need to keep the app open. We send you an SMS or email message when a visit is assigned, confirmed, or changes — open the app when one arrives.",
    "notification": "You don't need to keep the app open. We send you an SMS or email message when a visit is assigned, confirmed, or changes.",
}

# v1.7: the same guide in Simplified Chinese, keyed by the words a Singapore
# senior would type. Matched only when the question itself is in Chinese.
HELP_GUIDE_ZH = {
    # specific phrases first: "Kaki 验证码" must not fall into "验证码" (the sign-in code)
    "kaki 验证码": "Kaki：您的探访页面有一个给家属的 4 位数 Kaki 验证码。到门口时连同您的照片一起出示，家属输入后会把开始码读给您。",
    "kaki验证码": "Kaki：您的探访页面有一个给家属的 4 位数 Kaki 验证码。到门口时连同您的照片一起出示，家属输入后会把开始码读给您。",
    "开始码": "照顾者：Kaki 到达时，先在“确认是本人”输入 Kaki 屏幕上的 4 位数 Kaki 验证码，您的开始码就会出现在探访页面。把开始码读给 Kaki，探访就开始。",
    "取消": "打开探访，点“取消”。请至少提前 2 小时取消，以免 Kaki 已经在路上。",
    "照护计划": "照顾者：首页 → 照护计划。请保持药物、行动能力和语言的资料更新，每位 Kaki 探访前都会看。",
    "报告": "Kaki：结束探访后，勾选适用的项目并写一段简短备注。照顾者会在探访页面看到报告。",
    "报酬": "Kaki：“成果”页面显示小时数和金额。试点期间报酬每周通过 Vanguard 发放。",
    "付款": "试点期间应用内不需要付款，费用通过 Vanguard / ICCP 账户结算。",
    "照片": "Kaki：在“我的资料”添加照片。家属会在探访页面看到，这样在门口就知道是您。",
    "证书": "Kaki：在“我的资料”添加证书（CPR + AED、行动辅助培训等），PDF 或照片都可以。协调员审批前会查看。",
    "紧急": "紧急是指一小时内就需要人，例如帮佣突然离开。协调员会优先处理这些申请。",
    "审批": "第一次登录后，Kakis 协调员会审核并批准您的账户，通常一天内完成。在那之前您会看到等待页面。",
    "预约": "照顾者：首页 → 预约探访 → 选服务 → 选时间（紧急 / 尽快 / 提前安排）→ 填详情 → 提交。协调员会配对 Kaki，您可以在“探访”里看到。",
    "开着": "不需要一直开着应用。安排了探访、确认了或有任何变动，我们都会发短信或电邮给您，收到再打开应用就可以。",
    "通知": "不需要一直开着应用。安排了探访、确认了或有任何变动，我们都会发短信或电邮给您。",
    "联系": "有困难？请致电巴西立 ICCP 协调员 6XXX XXXX。",
    "登录": "输入您的电邮地址或手机号码，然后输入我们发给您的 6 位数验证码。不需要密码。登录过的用户只需要输入验证码。新账户需要等协调员审批。",
    "验证码": "登录时的 6 位数验证码会发到您的电邮或手机。如果没收到，请再发送一次，或致电协调员 6XXX XXXX。",
}
_ZH_FALLBACK = ("我可以帮您解答：登录、审批、预约探访、开始码、报告、照护计划、取消和报酬。"
                "请试试这些词，或致电巴西立 ICCP 协调员 6XXX XXXX。")

def is_zh(text: str) -> bool:
    """True when the question is (mostly) written in Chinese characters."""
    import re as _re
    han = sum(1 for ch in (text or "") if "\u4e00" <= ch <= "\u9fff")
    latin_words = len(_re.findall(r"[A-Za-z]+", text or ""))
    return han >= 2 and han > latin_words

def _guide_zh(message: str) -> str:
    m = (message or "").lower()
    for key, answer in HELP_GUIDE_ZH.items():
        if key in m:
            return answer
    return _ZH_FALLBACK

SYSTEM_PROMPT = """You are the in-app helper for Kakis, a Singapore pilot app where family
caregivers book trusted respite visits for elderly parents, trained "kakis" (respite givers)
serve those visits, and a coordinator approves users and matches visits manually.
Answer briefly (2-4 sentences), warmly, in plain language. App facts:
- Sign-in: email address OR Singapore mobile number, then a 6-digit code sent to whichever they gave. Returning users are asked only for the code. New users need coordinator approval.
- Caregivers: set up household + care plan; book visits (service -> urgency Urgent/Soon/Planned -> details with exact start/end times for planned visits, charged by the half hour, minimum 1 hour); can ask for a female or male kaki, or for a kaki who has visited before; get messages when a kaki is matched, confirms, is on the way, or cancels.
- At the door (v1.6): the kaki shows their photo and a 4-digit KAKI CODE on their screen; the caregiver enters it on the visit page ("Check it's them"); only then does the caregiver's 4-digit START CODE appear, which the caregiver reads to the kaki to start the visit. The kaki never sees the start code in their app; the caregiver never sees the kaki code in theirs.
- Cancelling: either side can cancel after accepting or even mid-visit, with a short reason; the other side and the coordinator are told. Whether anything is paid for a cancelled visit is the coordinator's decision, not the app's.
- Kakis: profile photo, gender, certificates (PDF or photo) that the coordinator checks before approving; working hours per day; see assigned visits, accept, tap "I'm on my way", start with the family's start code, end with a short report. Household-help visits show the kaki only what the task needs (no medications or age). Impact tab shows hours/earnings; weekly payout via Vanguard.
- You don't need to keep the app open: SMS or email arrives when anything changes.
- No payments in-app during the pilot (billed via ICCP account). No public ratings of kakis (MOH rule) - concerns go privately to the care team.
- Coordinator phone: 6XXX XXXX. If you don't know, say so and point to the coordinator.
- Answer in the language the question was asked in: English for English, Simplified Chinese (as spoken in Singapore, plain and short) for Chinese. Keep "Kaki" as Kaki; start code = 开始码; kaki code = Kaki 验证码; caregiver = 照顾者; coordinator = 协调员; visit = 探访."""

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

def guide_reply(message: str) -> str:
    """Keyword guide only — no provider call. Used for signed-out visitors, who
    are most often asking how to sign in."""
    if is_zh(message):
        return _guide_zh(message)
    m = (message or "").lower()
    if any(w in m for w in ("sign in", "signin", "log in", "login", "code", "otp")):
        return HELP_GUIDE["sign in"]
    for key, answer in HELP_GUIDE.items():
        if key in m:
            return answer
    return ("I can help with signing in, approval, booking a visit, the start code, "
            "reports, care plans, cancelling, and earnings. Sign in for fuller answers — "
            "or call the Pasir Ris ICCP coordinator on 6XXX XXXX.")

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
    # keyword fallback, in the language of the question
    if is_zh(message):
        return _guide_zh(message)
    m = message.lower()
    for key, answer in HELP_GUIDE.items():
        if key in m:
            return answer
    return ("Here's what I can help with: signing in, approval, booking a visit, "
            "the start code, reports, care plans, cancelling, and earnings. "
            "Try one of those words — or call the coordinator at 6XXX XXXX.")
