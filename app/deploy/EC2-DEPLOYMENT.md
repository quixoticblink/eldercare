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

## Before real users

- **`DEV_MODE=1` must become `0`.** Sign-in codes are currently returned in the
  API response, so anyone can sign in as anyone. Needs a Resend key and a
  verified sending domain first.
- **`OPENAI_API_KEY` is empty**, so the chatbot serves the built-in keyword
  guide rather than live answers.

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

- `backend/tests/smoke.py` — 30/30 assertions pass on the server
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
