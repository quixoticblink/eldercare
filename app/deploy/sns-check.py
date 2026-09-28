"""M-AUTH · is AWS SNS ready to carry Kakis SMS from this box?

Run on the EC2 box as the app user, from the app directory so .env is picked up:

    cd /home/kakis/eldercare/app
    sudo -u kakis .venv/bin/python deploy/sns-check.py            # read-only checks
    sudo -u kakis .venv/bin/python deploy/sns-check.py +6591234567 # ...then one real SMS

Read-only part (no message is sent):
  1. which AWS identity the box is using (instance role or keys in .env), never the key itself
  2. whether the account is still in the SMS sandbox for AWS_REGION; in the sandbox a publish
     returns a MessageId but only verified numbers receive anything
  3. the account's monthly SMS spend limit and default sender settings

With a phone number in E.164 it also sends one transactional SMS through the same
code path the app uses (backend/services/sms.py::_sns), so what you receive is exactly
what a caregiver would. Prints nothing secret.
"""
import os, sys, pathlib

APP = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP))
os.chdir(APP)

from backend import config                      # loads .env
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def ok(msg):  print(f"  ok   {msg}")
def bad(msg): print(f"  FAIL {msg}")

print(f"region {config.AWS_REGION}   SMS_PROVIDER={config.SMS_PROVIDER}   "
      f"SMS_ENABLED={'1' if config.SMS_ENABLED else '0'}   SENDER_ID={config.SMS_SENDER_ID or '(none)'}")

# 1. identity
try:
    who = boto3.client("sts", region_name=config.AWS_REGION).get_caller_identity()
    arn = who["Arn"]
    ok(f"credentials found: {arn.split(':')[-1]} in account ...{who['Account'][-4:]}")
except NoCredentialsError:
    bad("no AWS credentials. Attach an IAM role to the instance (sns:Publish, sns:GetSMSAttributes, "
        "sns:GetSMSSandboxAccountStatus) or put AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY in .env")
    sys.exit(1)

sns = boto3.client("sns", region_name=config.AWS_REGION)

# 2. sandbox
try:
    sandbox = sns.get_sms_sandbox_account_status()["IsInSandbox"]
    if sandbox:
        bad(f"account is IN the SMS sandbox for {config.AWS_REGION}: only verified numbers receive. "
            "Request production access in the SNS console (Text messaging > Sandbox).")
        try:
            nums = sns.list_sms_sandbox_phone_numbers().get("PhoneNumbers", [])
            for n in nums:
                print(f"       verified: {n['PhoneNumber']}  {n['Status']}")
        except ClientError as e:
            print(f"       (cannot list verified numbers: {e.response['Error']['Code']})")
    else:
        ok(f"account is OUT of the sandbox in {config.AWS_REGION}")
except ClientError as e:
    bad(f"get_sms_sandbox_account_status: {e.response['Error']['Code']} {e.response['Error']['Message']}")

# 3. account attributes
try:
    a = sns.get_sms_attributes()["attributes"]
    ok(f"MonthlySpendLimit={a.get('MonthlySpendLimit', '?')} USD  "
       f"DefaultSMSType={a.get('DefaultSMSType', '?')}  DefaultSenderID={a.get('DefaultSenderID', '(none)')}")
except ClientError as e:
    bad(f"get_sms_attributes: {e.response['Error']['Code']} {e.response['Error']['Message']}")

# 4. optional real send
if len(sys.argv) > 1:
    to = sys.argv[1]
    if not to.startswith("+"):
        bad("phone must be E.164, e.g. +6591234567"); sys.exit(2)
    from backend.services import sms
    text = "123456 is your Kakis sign-in code. (SNS test, ignore)"
    try:
        sms._sns(to, text)
        ok(f"published to {to[:4]}…{to[-3:]} via SNS. Check the phone; sender should read "
           f"'{config.SMS_SENDER_ID or 'a shared number'}'. If nothing arrives in 2 min and the account "
           "is out of the sandbox, the Sender ID is being dropped by the carrier: clear SMS_SENDER_ID.")
    except ClientError as e:
        bad(f"publish: {e.response['Error']['Code']} {e.response['Error']['Message']}")
        sys.exit(3)
