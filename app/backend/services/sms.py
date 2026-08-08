"""M-AUTH · outbound SMS. Same contract as emailer.send_otp_email.

Two providers behind one function, chosen by SMS_PROVIDER:

  sns    — AWS SNS. Sandboxed per REGION until production access is granted:
           it accepts a publish to any number and returns a MessageId, but
           delivers only to verified destination numbers. The failure is
           completely silent, which is why send() reporting True is never
           proof of delivery.
  twilio — no per-region sandbox. A TRIAL account is still limited to verified
           numbers; a paid account reaches anyone.

Both return {"sent": bool, "dev_code": code|None} so routers/auth.py never has
to know which one is live. Switching is an .env change and a restart.
"""
import httpx
from .. import config

def _sns(to: str, message: str) -> bool:
    import boto3
    client = boto3.client("sns", region_name=config.AWS_REGION)
    attrs = {"AWS.SNS.SMS.SMSType": {"DataType": "String", "StringValue": "Transactional"}}
    if config.SMS_SENDER_ID:
        attrs["AWS.SNS.SMS.SenderID"] = {"DataType": "String", "StringValue": config.SMS_SENDER_ID}
    client.publish(PhoneNumber=to, Message=message, MessageAttributes=attrs)
    return True

def _twilio(to: str, message: str) -> bool:
    sid, token = config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN
    if not (sid and token):
        raise RuntimeError("TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN not set")
    data = {"To": to, "Body": message}
    if config.TWILIO_MESSAGING_SERVICE_SID:
        data["MessagingServiceSid"] = config.TWILIO_MESSAGING_SERVICE_SID
    elif config.TWILIO_FROM:
        data["From"] = config.TWILIO_FROM
    else:
        raise RuntimeError("Set TWILIO_FROM or TWILIO_MESSAGING_SERVICE_SID")

    r = httpx.post(
        f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
        auth=(sid, token), data=data, timeout=20,
    )
    if r.status_code >= 300:
        # Twilio returns a numeric code that says exactly what is wrong —
        # 21608 = trial account, unverified number; 21606 = bad From.
        try:
            body = r.json()
            raise RuntimeError(f"twilio {body.get('code')}: {body.get('message')}")
        except ValueError:
            raise RuntimeError(f"twilio HTTP {r.status_code}: {r.text[:200]}")
    return True

_PROVIDERS = {"sns": _sns, "twilio": _twilio}

def send_otp_sms(to: str, code: str) -> dict:
    """Returns {"sent": bool, "dev_code": code|None}. With SMS switched off (or
    on a failure in DEV_MODE) the code comes back to the API so the app still
    works end to end."""
    message = (f"{code} is your Kakis sign-in code. "
               f"It expires in {config.OTP_MINUTES} minutes.")
    if config.SMS_ENABLED:
        send = _PROVIDERS.get(config.SMS_PROVIDER)
        if send is None:
            print(f"[kakis] unknown SMS_PROVIDER {config.SMS_PROVIDER!r} — not sending")
            return {"sent": False, "dev_code": code if config.DEV_MODE else None}
        try:
            send(to, message)
            return {"sent": True, "dev_code": None}
        except Exception as e:
            # Missing credentials, trial restrictions, unregistered sender IDs —
            # all land here. Fall through to the dev code rather than stranding
            # the person on the code screen.
            print(f"[kakis] {config.SMS_PROVIDER} send to {to} failed: {e}")
            return {"sent": False, "dev_code": code if config.DEV_MODE else None}
    print(f"[kakis DEV] SMS OTP for {to}: {code}")
    return {"sent": False, "dev_code": code if config.DEV_MODE else None}

def send_sms(to: str, text: str) -> bool:
    """Generic SMS (notifications, not codes). Returns success, never raises."""
    if not config.SMS_ENABLED:
        print(f"[kakis DEV] SMS to {to}: {text}")
        return False
    send = _PROVIDERS.get(config.SMS_PROVIDER)
    if send is None:
        print(f"[kakis] unknown SMS_PROVIDER {config.SMS_PROVIDER!r} — not sending")
        return False
    try:
        send(to, text)
        return True
    except Exception as e:
        print(f"[kakis] {config.SMS_PROVIDER} notification to {to} failed: {e}")
        return False
