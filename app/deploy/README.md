# Deploying Kakis (pilot)

Two supported shapes. **A** is the simplest — one VM runs everything.

## A. Single VM (backend serves the frontend)

On any Ubuntu/Debian VM (a $6 droplet is plenty for the pilot):

```bash
# 1. Get the code
git clone https://github.com/quixoticblink/eldercare.git && cd eldercare/app

# 2. Python env
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt

# 3. Configure — create app/.env.sh (chmod 600)
export JWT_SECRET="$(openssl rand -hex 32)"      # REQUIRED in prod
export ADMIN_EMAILS="abhishekkaul@gmail.com"     # the hardcoded admin(s)
export RESEND_API_KEY="re_..."                   # from resend.com (else codes print to console)
export MAIL_FROM="Kakis <hello@yourdomain.sg>"   # domain verified in Resend
export DEV_MODE="0"                              # 1 = codes returned in API (pre-Resend only!)
export ANTHROPIC_API_KEY="sk-ant-..."            # optional — enables the smart chatbot
export DB_PATH="/home/kakis/kakis.duckdb"
export CORS_ORIGINS="*"                          # tighten to your Vercel URL if using shape B

# 4. Run
source .env.sh
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Visit `http://<vm-ip>:8000` — that's the whole app. First sign-in with an
`ADMIN_EMAILS` address lands you in the coordinator console.

**Make it survive reboots:** copy `kakis.service` to `/etc/systemd/system/`,
adjust paths, then `systemctl enable --now kakis`. Note: systemd's
`EnvironmentFile` wants plain `KEY=value` lines — put the same variables in
`app/.env` without the `export` keyword.

**HTTPS (required before real users):** point a domain at the VM, install Caddy
(`apt install caddy`), drop in the `Caddyfile` — Caddy fetches TLS certs
automatically and proxies to :8000.

**Backups:** the entire database is one file (`kakis.duckdb`). A nightly
`cp kakis.duckdb backups/kakis-$(date +%F).duckdb` in cron is a real backup
strategy at pilot scale.

## B. Frontend on Vercel + backend on the VM

1. Deploy the backend as above (it still serves `/api/*`; the static mount is harmless).
2. In Vercel: New Project → set **Root Directory** to `app/frontend` (vercel.json included — plain static).
3. Edit `frontend/config.js` on the Vercel side: `window.KAKIS_API = "https://api.yourdomain.sg"`.
4. On the VM set `CORS_ORIGINS="https://your-app.vercel.app"`.

## Service checklist (what you asked to know)

| Service | Needed for | Get it at |
|---|---|---|
| **Resend** | email sign-in codes | resend.com — free tier fine; verify your sending domain |
| **Anthropic API key** | the help chatbot (optional — falls back to a built-in guide) | console.anthropic.com |
| **A VM** | backend + DuckDB | DigitalOcean/Lightsail/Hetzner, 1GB RAM is enough |
| **A domain** | HTTPS + Resend domain verification | any registrar |
| Vercel | only for shape B | vercel.com |

Mobile OTP later = one SMS provider (e.g. Twilio) added to `services/emailer.py` — M-AUTH only, per SPEC.

## Smoke test after any change

```bash
cd app && python3 backend/tests/smoke.py   # 24 assertions, full lifecycle
```
