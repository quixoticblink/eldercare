#!/usr/bin/env python3
"""Go-live preflight — proves each provider actually works before DEV_MODE=0.

Turning off DEV_MODE stops sign-in codes being returned in the API response.
If email or SMS delivery is misconfigured at that moment, nobody can sign in
and there is no fallback. So: run this, get three green ticks, then flip.

    cd /home/kakis/eldercare/app && .venv/bin/python deploy/preflight.py
    .venv/bin/python deploy/preflight.py --send-email you@example.com
    .venv/bin/python deploy/preflight.py --send-sms +6591234567

Read-only by default: it validates credentials and reports configuration
without sending anything. The --send flags do a real end-to-end delivery.
"""
import argparse, os, sys, pathlib

# Load /home/kakis/eldercare/app/.env the same way systemd does (KEY=value).
ENV_PATH = pathlib.Path(__file__).resolve().parent.parent / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from backend import config                      # noqa: E402
import httpx                                    # noqa: E402

OK, WARN, BAD = "\033[32m✓\033[0m", "\033[33m!\033[0m", "\033[31m✗\033[0m"
results = {}

def head(t):
    print(f"\n\033[1m{t}\033[0m")

def line(sym, msg):
    print(f"  {sym} {msg}")

# ---------------------------------------------------------------- email
def check_resend(send_to=None):
    head("Resend · email sign-in codes")
    if not config.RESEND_API_KEY:
        line(BAD, "RESEND_API_KEY is not set — codes fall back to DEV_MODE")
        return False
    try:
        r = httpx.get("https://api.resend.com/domains",
                      headers={"Authorization": f"Bearer {config.RESEND_API_KEY}"}, timeout=20)
    except Exception as e:
        line(BAD, f"could not reach Resend: {e}")
        return False
    if r.status_code == 401:
        line(BAD, "API key rejected (401) — wrong or revoked key")
        return False
    if r.status_code >= 300:
        line(BAD, f"unexpected response {r.status_code}: {r.text[:200]}")
        return False
    line(OK, "API key accepted")

    domains = r.json().get("data", []) or []
    verified = [d for d in domains if d.get("status") == "verified"]
    for d in domains:
        sym = OK if d.get("status") == "verified" else WARN
        line(sym, f"domain {d.get('name')} — {d.get('status')}")
    if not domains:
        line(WARN, "no sending domain added yet (only resend.dev test sends will work)")

    sender = config.MAIL_FROM
    line(OK if "@" in sender else BAD, f"MAIL_FROM = {sender}")
    domain_part = sender.split("@")[-1].rstrip(">").strip() if "@" in sender else ""
    if domain_part and domain_part != "resend.dev":
        if any(d.get("name") == domain_part for d in verified):
            line(OK, f"{domain_part} is verified — real users will receive mail")
        else:
            line(BAD, f"{domain_part} is NOT verified in Resend — sends will be rejected")
            return False
    elif domain_part == "resend.dev":
        line(WARN, "using resend.dev — only reaches your own Resend signup address")

    if send_to:
        from backend.services import emailer
        out = emailer.send_otp_email(send_to, "123456")
        line(OK if out["sent"] else BAD, f"test email to {send_to}: sent={out['sent']}")
        return bool(out["sent"])
    return True

# ------------------------------------------------------------------ sms
def check_sns(send_to=None):
    head("AWS SNS · SMS sign-in codes")
    if not config.SMS_ENABLED:
        line(WARN, "SMS_ENABLED=0 — SMS codes fall back to DEV_MODE (email still fine)")
        return None                      # not a blocker, just off
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
    except ImportError:
        line(BAD, "boto3 not installed")
        return False
    try:
        sns = boto3.client("sns", region_name=config.AWS_REGION)
        sandbox = sns.get_sms_sandbox_account_status().get("IsInSandbox", True)
    except NoCredentialsError:
        line(BAD, "no AWS credentials — attach an IAM role with sns:Publish to the instance")
        return False
    except ClientError as e:
        line(BAD, f"AWS rejected the call: {e.response['Error'].get('Code')}")
        return False
    except Exception as e:
        line(BAD, f"could not reach SNS: {e}")
        return False

    line(OK, f"credentials work, region {config.AWS_REGION}")
    if sandbox:
        line(BAD, "account is in the SMS SANDBOX — only verified numbers receive messages")
        try:
            nums = sns.list_sms_sandbox_phone_numbers().get("PhoneNumbers", [])
            for n in nums:
                line(WARN, f"  sandbox-verified: {n.get('PhoneNumber')} ({n.get('Status')})")
        except Exception:
            pass
    else:
        line(OK, "out of the sandbox — any number can receive codes")
    line(OK if config.SMS_SENDER_ID else WARN, f"SMS_SENDER_ID = {config.SMS_SENDER_ID or '(none)'}")
    line(WARN, "Singapore requires a REGISTERED Sender ID; unregistered senders are dropped by carriers")

    if send_to:
        from backend.services import sms as smsmod
        out = smsmod.send_otp_sms(send_to, "123456")
        line(OK if out["sent"] else BAD, f"test SMS to {send_to}: sent={out['sent']}")
        return bool(out["sent"])
    return not sandbox

# --------------------------------------------------------------- chatbot
def check_llm():
    head("Chatbot · OpenAI / Anthropic")
    if not (config.OPENAI_API_KEY or config.ANTHROPIC_API_KEY):
        line(WARN, "no key set — chatbot serves the built-in keyword guide (app still works)")
        return None
    if config.ANTHROPIC_API_KEY:
        line(OK, "ANTHROPIC_API_KEY set (takes precedence over OpenAI)")
    if config.OPENAI_API_KEY:
        try:
            r = httpx.get("https://api.openai.com/v1/models",
                          headers={"Authorization": f"Bearer {config.OPENAI_API_KEY}"}, timeout=20)
        except Exception as e:
            line(BAD, f"could not reach OpenAI: {e}")
            return False
        if r.status_code == 401:
            line(BAD, "OpenAI key rejected (401)")
            return False
        if r.status_code >= 300:
            line(BAD, f"OpenAI returned {r.status_code}: {r.text[:160]}")
            return False
        names = {m["id"] for m in r.json().get("data", [])}
        line(OK, "OpenAI key accepted")
        line(OK if config.OPENAI_MODEL in names else WARN,
             f"OPENAI_MODEL = {config.OPENAI_MODEL}" +
             ("" if config.OPENAI_MODEL in names else "  (not in your account's model list)"))
    return True

# --------------------------------------------------------------- verdict
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--send-email", metavar="ADDRESS")
    ap.add_argument("--send-sms", metavar="+65XXXXXXXX")
    a = ap.parse_args()

    head("Current mode")
    line(WARN if config.DEV_MODE else OK,
         f"DEV_MODE = {'1 — sign-in codes are returned in the API response' if config.DEV_MODE else '0 — live'}")

    email_ok = check_resend(a.send_email)
    sms_ok = check_sns(a.send_sms)
    check_llm()

    head("Verdict")
    if email_ok or sms_ok:
        channels = [n for n, ok in (("email", email_ok), ("SMS", sms_ok)) if ok]
        line(OK, f"at least one delivery channel works ({', '.join(channels)})")
        if config.DEV_MODE:
            line(WARN, "safe to set DEV_MODE=0 and restart — but test a real sign-in first")
        else:
            line(OK, "already live")
    else:
        line(BAD, "NO delivery channel works — do not set DEV_MODE=0 or nobody can sign in")
        sys.exit(1)

if __name__ == "__main__":
    main()
