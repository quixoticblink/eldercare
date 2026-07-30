# Kakis app — SPEC v1 (pilot build)

The deployable pilot app. FastAPI + DuckDB backend on a VM; static phone-first frontend (Vercel or served by the same VM). This SPEC is the contract: **every future change names the module it touches, and only that module's files change.** If a change can't be expressed that way, the SPEC gets amended first (add a module or split one), then the code follows.

Working name *Kakis* remains provisional (Kampung Kakis collision — see wiki).

---

## 1. Architecture

```
app/
├── SPEC.md                ← this file (the contract)
├── backend/               ← FastAPI + DuckDB, runs on the VM
│   ├── main.py            ← app factory, CORS, static mount, router registration ONLY
│   ├── config.py          ← env vars, constants ONLY
│   ├── db.py              ← DuckDB connection, schema DDL, seed ONLY
│   ├── security.py        ← token signing/verify, password-free auth helpers ONLY
│   ├── services/
│   │   ├── emailer.py     ← Resend integration (and future SMS) ONLY
│   │   └── llm.py         ← Anthropic API proxy for the help chatbot ONLY
│   └── routers/
│       ├── auth.py        ← M-AUTH   endpoints
│       ├── users.py       ← M-USERS  endpoints
│       ├── care.py        ← M-CARE   endpoints (households, care plans)
│       ├── visits.py      ← M-VISITS endpoints (requests → lifecycle → reports)
│       ├── admin.py       ← M-ADMIN  endpoints (approvals, manual matching, quality)
│       └── chat.py        ← M-HELP   endpoints
├── frontend/              ← static SPA, no build step
│   ├── index.html         ← shell + screen containers
│   ├── css/kakis.css      ← the design system (ported from prototype v2)
│   └── js/
│       ├── api.js         ← fetch wrapper, token storage, error toasts ONLY
│       ├── ui.js          ← DOM helpers, components (chips, cards, toasts) ONLY
│       ├── app.js         ← router, session, role dispatch ONLY
│       ├── views/auth.js      ← M-AUTH screens
│       ├── views/caregiver.js ← M-CARE + caregiver side of M-VISITS screens
│       ├── views/kaki.js      ← kaki side of M-VISITS screens
│       ├── views/admin.js     ← M-ADMIN screens
│       └── views/help.js      ← M-HELP guide + chatbot widget
└── deploy/
    ├── README.md          ← VM + Vercel instructions
    ├── kakis.service      ← systemd unit
    ├── Caddyfile          ← reverse proxy + TLS sample
    └── vercel.json        ← frontend-on-Vercel config
```

**Data flow:** frontend (fetch + Bearer token) → FastAPI `/api/*` → DuckDB single file (`kakis.duckdb`). One backend process; DuckDB is embedded, so no separate DB server. Backend also serves `frontend/` at `/` so a single VM is a complete deployment; pointing Vercel at `frontend/` with `API_BASE` set is the split deployment.

---

## 2. Modules and change boundaries

| Module | Owns | Backend files | Frontend files | "If you want to change…" |
|---|---|---|---|---|
| **M-AUTH** | email OTP login, sessions, roles, approval status | `routers/auth.py`, `security.py`, `services/emailer.py` | `views/auth.js` | login method (add mobile OTP → extend `emailer.py`→`sms`, add endpoint in `auth.py`; nothing else moves), session length, admin allowlist |
| **M-USERS** | profiles, preferences, kaki services/languages | `routers/users.py` | profile sections in `views/kaki.js` / `caregiver.js` | profile fields (add column in `db.py` + endpoint + form) |
| **M-CARE** | households, seniors, care plans | `routers/care.py` | `views/caregiver.js` | care-plan fields, multi-senior households |
| **M-VISITS** | visit requests, lifecycle, OTP start/end, reports, care notes | `routers/visits.py` | `views/caregiver.js`, `views/kaki.js` | services list, urgency tiers, status flow, report chips |
| **M-ADMIN** | user approvals, **manual matching**, quality view, counts | `routers/admin.py` | `views/admin.js` | matching (→ automated scoring lands HERE and only here), approval rules |
| **M-HELP** | help guide content, chatbot | `routers/chat.py`, `services/llm.py` | `views/help.js` | LLM provider/key, guide content |
| **M-CORE** | app wiring, DB schema, design system | `main.py`, `config.py`, `db.py` | `app.js`, `api.js`, `ui.js`, `kakis.css` | env vars, schema migrations, theme |

Cross-module rule: routers never import each other; shared logic lives in `db.py`/`security.py`/`services/`. Frontend views never call `fetch` directly — always through `api.js`.

---

## 3. Roles, auth, approval

- **Login:** email → 6-digit code (Resend) → verify → signed token (HMAC, 30-day). No passwords. `DEV_MODE=1` returns the code in the API response so the app works before Resend is configured.
- **Roles:** `admin` · `caregiver` · `kaki`. Chosen at first login (except admin); stored on the user.
- **Admin is hardcoded** via `ADMIN_EMAILS` env (comma-separated). Admin logins are auto-approved with role `admin`.
- **Everyone else lands `pending`** and sees a waiting screen until the admin approves them (M-ADMIN). Approval assigns/confirms the role.
- Mobile OTP: planned, M-AUTH only (`sms` provider in `emailer.py` + one endpoint).

## 4. Data model (DuckDB)

`users` (id, email, name, phone, role, status[pending|approved|suspended], created_at) · `kaki_profiles` (user_id, services[], languages[], area, tier) · `households` (id, caregiver_id, senior_name, senior_age, address) · `care_plans` (household_id, meds, mobility, languages[], contacts, notes) · `visits` (id, household_id, caregiver_id, kaki_id?, service, tier[urgent|soon|planned], date, window, language, notes, status, otp_code, timestamps…) · `visit_reports` (visit_id, chips[], text, meds_confirmed) · `care_notes` (id, household_id, visit_id?, author_id, chips[], text) · `otp_codes` (email, code, expires) · `audit_log` (ts, actor, action, detail).

**Visit lifecycle (M-VISITS):** `requested → assigned → accepted → in_progress → completed` (+ `cancelled`, `declined→requested`). Assignment is **manual by admin** in v1. Start requires the visit OTP (shown to the caregiver, entered by the kaki). Completion requires a report.

## 5. API contract (all under `/api`)

- `POST /auth/request-code` {email} · `POST /auth/verify` {email, code, role?} → {token, user} · `GET /auth/me`
- `PUT /users/me` profile+prefs · `GET /users/kakis` (admin)
- `GET|PUT /care/household` · `GET|PUT /care/plan`
- `POST /visits` create request · `GET /visits` (role-scoped list) · `GET /visits/{id}` · `POST /visits/{id}/accept|decline|start{otp}|complete{report}|cancel` · `POST /visits/{id}/care-note`
- `GET /admin/overview` counts · `GET /admin/pending-users` · `POST /admin/users/{id}/approve|suspend` · `POST /admin/visits/{id}/assign` {kaki_id} · `GET /admin/quality` reports+notes
- `POST /chat` {message, history[]} → {reply} (LLM if `ANTHROPIC_API_KEY` set, else keyword help)

Errors: `{detail}` with proper status codes; frontend surfaces via toast.

## 6. Environment

`JWT_SECRET` (required in prod) · `ADMIN_EMAILS` (default `abhishekkaul@gmail.com`) · `RESEND_API_KEY` + `MAIL_FROM` (else DEV_MODE prints codes) · `DEV_MODE` (default 1) · `ANTHROPIC_API_KEY` + `LLM_MODEL` (default claude-sonnet; chatbot falls back to static guide without it) · `DB_PATH` (default `./kakis.duckdb`) · `CORS_ORIGINS` (Vercel URL) · `PORT` (default 8000).

## 7. Frontend rules

Phone-first: single column, max-width 430px centred, ≥48px targets, Kakis tokens (pandan/marigold/porcelain, Fraunces/Instrument Sans/Spline Sans Mono). Hash router (`#/login`, `#/care/home`, `#/kaki/home`, `#/admin`…). Role decides the shell + bottom nav. Help icon (?) floats on every screen → guide + chatbot. No framework, no build step — a deliberate v1 choice; migration to Next.js is a marked upgrade path that replaces `frontend/` wholesale without touching `backend/`.

## 8. Out of scope in v1 (and where they'd land)

Payments (new `routers/payments.py`, M-PAY) · automated matching (M-ADMIN only) · Singpass (M-AUTH) · WhatsApp notifications (`services/emailer.py` gains a provider) · elderly self-book surface (new `views/senior.js`, reuses M-VISITS API) · photo uploads in reports (M-VISITS + object storage).

## 9. Change log

- **v1.1 (2026-07-21) — prototype-sync round.** M-CORE: global user menu (top-right) with **sign out for every role**; `SERVICE_META` price/fee estimates and `TRIGGERS` in config; DB migration `visits.crisis_trigger`. M-VISITS: urgent/soon bookings gain the **"What happened?" trigger step** (pinned top-3 + click-to-call "not sure"); visit payloads now carry `trigger`, `times_together` (completed visits for this kaki+senior pair — the consistency signal), and `estimate` (price stack + kaki fee). Caregiver visit page gains the **kaki pass** (with "N visits together"), **estimated-cost stack** ("billed via ICCP during pilot"), and **contact/coordinator call row**; Visits tab split **Active/History**. Kaki: $ figures on rows/impact, "you receive ~$X · cashless weekly via Vanguard" on visit detail, **training & certificates** section in profile. M-ADMIN: trigger pill on request cards; **suspend/reinstate** buttons. Deliberately not ported from the prototype (still demo-only there): elderly self-book module, kaki "Available/Now geofenced" tab (conflicts with manual matching), agent console screens, add-kaki flow.
- **v1 (2026-07-21)** — initial build: M-AUTH (email OTP, hardcoded admin, approval gate), M-CARE, M-VISITS (full lifecycle, visit OTP, reports, care notes), M-ADMIN (approvals, manual matching, quality), M-HELP (guide + pluggable Claude chatbot), M-CORE (DuckDB schema v1, design system port).
