# Kakis — live EC2 deployment

**Live at https://singaporekakis.com** since 30 Jul 2026.
Shape **A** from `README.md` (single VM, backend serves the frontend).

## The box

| | |
|---|---|
| URL | `https://singaporekakis.com` (`www` 301s to the apex) |
| Instance | `i-0942e81ef83d2beec` — t3.micro, Amazon Linux 2023, ap-southeast-1 |
| Elastic IP | `3.1.33.212` |
| Security group | `sg-03d595ab57b72d786` (`launch-wizard-4`) — 22, 80, 443 inbound |
| SSH | `ssh -i ~/Documents/Claude/Keypairs/eldercare.pem ec2-user@3.1.33.212` |
| App user | `kakis` |
| App root | `/home/kakis/eldercare/app` |
| Database | `/home/kakis/kakis.duckdb` |
| Backups | `/home/kakis/backups/` — nightly 02:30 SGT, 14-day retention |
| DNS | GoDaddy (`ns05`/`ns06.domaincontrol.com`) — apex `A` → `3.1.33.212`, `www` CNAME → apex |
| TLS | Let's Encrypt via Caddy, auto-renewing. Current cert expires 28 Oct 2026 |

Note the README assumes Ubuntu/Debian (`apt`); this box is Amazon Linux, so
packages went in via `dnf` and Python is `python3.11` (the system `python3` is
3.9, too old for the current FastAPI/DuckDB wheels).

## Services

| Unit | State | Purpose |
|---|---|---|
| `kakis.service` | active, enabled | uvicorn on `0.0.0.0:8000` |
| `caddy.service` | active, enabled | HTTPS reverse proxy on 80/443 |
| `kakis-backup.timer` | active, enabled | nightly DuckDB snapshot |

Caddy 2.11.4 was installed from the official release binary (no `dnf` package
exists for Amazon Linux). Config lives at `/etc/caddy/Caddyfile` and serves
`singaporekakis.com`, redirecting `www` to the apex.

## How the domain is wired up

Elastic IP `3.1.33.212` is associated with `i-0942e81ef83d2beec`, so the address
survives stop/start. The old auto-assigned `47.129.187.33` was released in the
process — that hostname is dead, SSH to the Elastic IP.

DNS lives at **GoDaddy**, not Route 53. To change it:
**godaddy.com → My Products → Domains → singaporekakis.com → DNS → Records**,
edit the `A` record on `@`. `www` is a CNAME to `@` and follows automatically.

One gotcha worth remembering: after associating the Elastic IP the box went
completely unreachable, including port 22. The Elastic IP was attached
correctly — the cause was the security group, whose SSH rule was scoped to a
stale "My IP" value. Re-saving the inbound rules with 22, 80 and 443 fixed it.
If the box ever goes dark on *every* port at once while the console says
Running, check the security group before anything else.

Port 8000 is deliberately closed to the internet; Caddy proxies to it over
localhost.

## Live status (30 Jul 2026)

| Channel | State |
|---|---|
| Email sign-in | **Live** — Resend, `singaporekakis.com` verified, from `hello@singaporekakis.com`, replies to abhishekkaul@gmail.com |
| Chatbot | **Live** — OpenAI `gpt-4o-mini` |
| SMS sign-in | **Live via Twilio** — paid account `singaporekakis`, Messaging Service `MG94c7a1…`, US number `+18023067424`. Delivery confirmed to Singapore handsets that AWS SNS could not reach |
| `DEV_MODE` | **0** — codes are delivered, never returned in the API |

Confirmed after the switch: `/api/auth/request-code` returns no `dev_code` for
either a known or an unknown address, and delivery to a real inbox was
verified (not spam).

Before touching any of this, run the preflight — it refuses to bless a
`DEV_MODE` change unless a delivery channel actually works:

```bash
sudo -u kakis /home/kakis/eldercare/app/.venv/bin/python \
  /home/kakis/eldercare/app/deploy/preflight.py
# add --send-email you@example.com for a real end-to-end send
```

To change any secret without it entering shell history:

```bash
sudo /home/kakis/eldercare/app/deploy/set-secret.sh RESEND_API_KEY
```

A copy of the pre-go-live `.env` sits at `/home/kakis/.env.bak-predevmode`.

**Worth knowing:** `emailer.py` only returns a dev code when sending *fails*.
So once Resend was working, on-screen codes stopped appearing even with
`DEV_MODE=1`. Setting it to `0` removes the fallback for the case where Resend
is *down* — at which point sign-in stops entirely rather than degrading into
an open door. That is the intended trade.

## Demo admin account

`ADMIN_PHONES=+6598553704` → **Demo Coordinator**, a phone-only admin account
separate from `abhishekkaul@gmail.com`. Signing in with that number now
receives a real SMS code like any other user; confirmed working end to end
through the UI.

**`DEMO_IDENTIFIERS` is empty, and should stay that way.** Any identifier on
that list has its sign-in code returned in the API response and shown on
screen, bypassing delivery entirely — on a public URL that makes the identifier
a shared password, and this one is a full admin. It existed only to cover the
gap before SMS worked. Each use writes `demo_code_issued` to `audit_log`.

If a demo ever needs it back (no handset in the room, say), re-add it and
remove it immediately afterwards:

```bash
sudo /home/kakis/eldercare/app/deploy/set-secret.sh DEMO_IDENTIFIERS   # +6598553704
# afterwards
sudo sed -i 's/^DEMO_IDENTIFIERS=.*/DEMO_IDENTIFIERS=/' /home/kakis/eldercare/app/.env
sudo systemctl restart kakis
```

## SMS — currently Twilio

`SMS_PROVIDER=twilio`, paid account, sending through a Messaging Service. This
replaced SNS because `ap-southeast-1` is still in the SMS sandbox, where only
verified destination numbers receive anything — one handset worked and every
other Singapore number silently got nothing.

**A2P 10DLC Brand and Campaign registration is not required here.** That is a
US carrier rule for messages sent *to* US numbers; traffic to Singapore never
touches it. Twilio's console labels the number "Registration required" anyway,
which is misleading in this context. The steps that did matter were the
compliance profile and the Messaging Service.

Two trade-offs accepted: messages go out as international SMS from a US number,
so they cost more per message than a local sender and arrive from a `+1`
number, which some recipients treat as suspicious. In exchange it completely
sidesteps Singapore SSIR Sender ID registration, which takes weeks.

Delivery problems: **Twilio Console → Monitor → Logs → Messaging** gives
per-message status and an error code — far better visibility than SNS offered.

## SMS via AWS SNS (standby)

Instance role **`KakisAppRole`** on `i-0942e81ef83d2beec`, policy in
`deploy/aws-sns-policy.json`. `SMS_ENABLED=1`, region `ap-southeast-1`.

The policy JSON contains **only** `Version` and `Statement` — IAM rejects any
other top-level key (a `_comment` field will fail validation), so keep the
explanation here rather than in the file:

- `sns:Publish` uses `NotResource` on topic ARNs, so the instance can text
  phone numbers but cannot publish to any SNS topic in the account.
- **Sandbox management is `sms-voice:*`, not `sns:*`.** AWS moved it to End User
  Messaging (PinpointSmsVoiceV2). `sns:CreateSMSSandboxPhoneNumber` and friends
  authorise nothing — the call is evaluated against
  `sms-voice:CreateVerifiedDestinationNumber`. Granting only the `sns:` names
  produces an `AuthorizationError` that reads as if the policy were attached
  correctly.

### Sandbox: only verified numbers receive anything

While the account is in the SMS sandbox for a given **region**, SNS accepts a
publish to any number and returns a MessageId, but silently delivers only to
**verified destination numbers**. The symptom is one handset receiving codes
while every other number gets nothing, with no error anywhere.

Production access is granted **per account per region** — a support case
approved in one region leaves `ap-southeast-1` sandboxed.

Check and add numbers in the console: **AWS End User Messaging SMS →
Configurations → Sandbox destination phone numbers** (or SNS → Mobile → Text
messaging). Each number receives a verification code you must enter back.

### Switching provider: Twilio ↔ SNS

`SMS_PROVIDER` selects the carrier; no code changes either way.

```bash
# temporary move to Twilio while ap-southeast-1 is sandboxed
sudo /home/kakis/eldercare/app/deploy/set-secret.sh SMS_PROVIDER        # twilio
sudo /home/kakis/eldercare/app/deploy/set-secret.sh TWILIO_ACCOUNT_SID  # AC...
sudo /home/kakis/eldercare/app/deploy/set-secret.sh TWILIO_AUTH_TOKEN
sudo /home/kakis/eldercare/app/deploy/set-secret.sh TWILIO_FROM         # +1... or a Messaging Service SID

# back to AWS the moment production access is granted
sudo /home/kakis/eldercare/app/deploy/set-secret.sh SMS_PROVIDER        # sns
```

Always confirm with the preflight afterwards — it detects a Twilio **trial**
account, which is limited to verified numbers in exactly the same way as the
SNS sandbox and will otherwise reproduce this whole problem under a new name:

```bash
sudo -u kakis /home/kakis/eldercare/app/.venv/bin/python \
  /home/kakis/eldercare/app/deploy/preflight.py --send-sms +6591055701
```

Twilio setup, in order: sign up → **upgrade to pay-as-you-go** (the trial is
the trap) → buy a number, or create a Messaging Service → copy the Account SID
and Auth Token from the console dashboard. A Twilio number sending into
Singapore arrives as international SMS, which sidesteps SSIR Sender ID
registration; an alphanumeric sender does not.

### Sender ID is the thing most likely to break delivery

`SMS_SENDER_ID` defaults to `Kakis`. **Singapore carriers drop unregistered
alphanumeric Sender IDs**, and SNS still reports `sent: true` because AWS
accepted the message — the failure is downstream and silent.

If codes are not arriving, unset the Sender ID so AWS falls back to a shared
number, and compare:

```bash
sudo /home/kakis/eldercare/app/deploy/set-secret.sh SMS_SENDER_ID   # enter a single space to clear
sudo systemctl restart kakis
```

Registering `Kakis` with the Singapore SMS Sender ID Registry (SSIR) is the
permanent fix; it takes weeks and carries a fee.

## Still to do

- **SNS production access for `ap-southeast-1`**, if you want to move back off
  Twilio. Everything is still configured; it is a one-line
  `SMS_PROVIDER=sns` switch. Reattach the corrected IAM policy at the same time
  so `preflight.py` can read sandbox status instead of guessing.
- **DMARC** is `p=quarantine` with `rua` pointing at GoDaddy's address.
  Repoint `rua` to a mailbox you actually read, or authentication failures go
  unnoticed.
- **Sender ID registration (SSIR).** Delivery works today, but an unregistered
  alphanumeric Sender ID is not guaranteed long-term in Singapore.
- **Restore-from-backup has never been tested.** Snapshots are written nightly;
  a backup you have not restored is a hope, not a backup.

The app is then live at **https://singaporekakis.com**. First sign-in with
`abhishekkaul@gmail.com` lands in the coordinator console.

## Configuration

`/home/kakis/eldercare/app/.env` (mode 600, owned by `kakis`):

```
JWT_SECRET=<generated with openssl rand -hex 32>
ADMIN_EMAILS=abhishekkaul@gmail.com
MAIL_FROM="Kakis <onboarding@resend.dev>"
DEV_MODE=1
RESEND_API_KEY=
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
DB_PATH=/home/kakis/kakis.duckdb
CORS_ORIGINS=https://singaporekakis.com,https://www.singaporekakis.com
PORT=8000
```

### Turning on SMS sign-in (AWS SNS)

The code path is written and deployed; it is switched off until SNS is ready.
To enable, add to `.env` and restart:

```
SMS_ENABLED=1
AWS_REGION=ap-southeast-1
SMS_SENDER_ID=Kakis
ADMIN_PHONES=+65XXXXXXXX        # optional — lets a coordinator sign in by mobile
```

Two AWS-side prerequisites that are easy to miss:

- **The account starts in the SNS SMS sandbox**, where messages only reach
  phone numbers you have explicitly verified. Real caregivers will silently get
  nothing until you request production access.
- **Singapore requires a registered Sender ID.** Unregistered senders are
  dropped by the local carriers.

Credentials come from the instance's IAM role (cleanest — attach a role with
`sns:Publish`) or standard AWS env vars. Until `SMS_ENABLED=1`, SMS codes
follow the same DEV_MODE path as email and appear on screen.

**`DEV_MODE=1` means sign-in codes are returned in the API response.** That is
fine for testing but must not stay on once real caregivers are using the app —
anyone could sign in as anyone. Before the pilot goes live: add a Resend key,
verify the sending domain, then set `DEV_MODE=0`.

To add a secret:

```bash
sudo -u kakis nano /home/kakis/eldercare/app/.env
sudo systemctl restart kakis
```

## Code changes made during deployment

Both are in your local repo and on the server.

**`backend/services/llm.py` + `backend/config.py` — OpenAI support.**
The chatbot only spoke to Anthropic's API. Added an `_openai()` branch calling
`/v1/chat/completions`, driven by `OPENAI_API_KEY` and `OPENAI_MODEL`
(default `gpt-4o-mini`). Precedence is Anthropic → OpenAI → the built-in
keyword guide, so setting either key works and setting neither still serves
help text.

**`backend/db.py` — DuckDB crash-loop fix.** This one bit during deployment:
the service came up cleanly, then died on every subsequent restart. The v1.1
migration `ALTER TABLE visits ADD COLUMN IF NOT EXISTS crisis_trigger TEXT
DEFAULT ''` leaves a write-ahead-log entry that DuckDB 1.5.5 throws an
`InternalException` replaying after an unclean shutdown — so any `systemctl
restart` or reboot would have taken the app down permanently, with a C++ stack
trace and no usable Python error. Added a `CHECKPOINT` after `_init()` to fold
the WAL into the database file so there is never such an entry to replay.
Verified with four consecutive restarts and a `SIGKILL`; the service came back
healthy every time.

## Verification performed

- `backend/tests/smoke.py` — all assertions pass on the server (the run prints its own count)
- `GET /` and `GET /api/health` → 200, `{"ok":true,"dev_mode":true}`
- 4× `systemctl restart` and 1× `SIGKILL` → recovers healthy each time
- Backup timer fired manually; snapshot written to `/home/kakis/backups/`
- `https://singaporekakis.com/` → 200, valid Let's Encrypt cert, TLS verify clean
- `https://singaporekakis.com/api/health` → `{"ok":true,"dev_mode":true}`
- `https://www.singaporekakis.com/` → 301 to the apex
- `http://singaporekakis.com/` → 308 to HTTPS

## Redeploying after code changes

```bash
cd ~/Documents/Claude/Projects/eldercare/app
rsync -az --exclude '.venv/' --exclude '__pycache__/' --exclude '*.duckdb' \
  --exclude '.DS_Store' \
  -e 'ssh -i ~/Documents/Claude/Keypairs/eldercare.pem' \
  --rsync-path='sudo rsync' \
  ./ ec2-user@3.1.33.212:/home/kakis/eldercare/app/

ssh -i ~/Documents/Claude/Keypairs/eldercare.pem ec2-user@3.1.33.212 \
  'sudo chown -R kakis:kakis /home/kakis/eldercare && sudo systemctl restart kakis'
```

Handy one-liners:

```bash
sudo journalctl -u kakis -f            # app logs
sudo journalctl -u caddy -f            # TLS / proxy logs
systemctl status kakis caddy           # health
```
