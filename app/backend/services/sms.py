"""M-AUTH · outbound SMS via AWS SNS. Same contract as emailer.send_otp_email.

Kept deliberately parallel to emailer.py: both return {"sent", "dev_code"} so
routers/auth.py can pick a channel without caring how delivery works. Swapping
SNS for Twilio later means rewriting only this file.
"""
from .. import config

# boto3 is imported lazily so the app still boots (and email sign-in still
# works) on a box where the AWS SDK was never installed.
def _publish(to: str, message: str) -> bool:
    import boto3
    client = boto3.client("sns", region_name=config.AWS_REGION)
    attrs = {
        "AWS.SNS.SMS.SMSType": {"DataType": "String", "StringValue": "Transactional"},
    }
    if config.SMS_SENDER_ID:
        attrs["AWS.SNS.SMS.SenderID"] = {"DataType": "String", "StringValue": config.SMS_SENDER_ID}
    client.publish(PhoneNumber=to, Message=message, MessageAttributes=attrs)
    return True

def send_otp_sms(to: str, code: str) -> dict:
    """Returns {"sent": bool, "dev_code": code|None}. In DEV_MODE (or with SMS
    switched off) the code comes back to the API so the app works end to end
    before SNS is live."""
    message = (f"{code} is your Kakis sign-in code. "
               f"It expires in {config.OTP_MINUTES} minutes.")
    if config.SMS_ENABLED:
        try:
            _publish(to, message)
            return {"sent": True, "dev_code": None}
        except Exception:
            # Sandbox restrictions, unregistered Sender ID, missing credentials —
            # all land here. Fall through to the dev code rather than stranding
            # the person on the code screen.
            return {"sent": False, "dev_code": code if config.DEV_MODE else None}
    print(f"[kakis DEV] SMS OTP for {to}: {code}")
    return {"sent": False, "dev_code": code if config.DEV_MODE else None}
