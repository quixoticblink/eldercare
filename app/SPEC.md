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
| **M-AUTH** | OTP login by email **or** mobile, sessions, roles, approval status | `routers/auth.py`, `security.py`, `services/emailer.py`, `services/sms.py` | `views/auth.js` | delivery provider (Resend → other in `emailer.py`; SNS → Twilio in `sms.py`), session length, admin allowlist (`ADMIN_EMAILS` / `ADMIN_PHONES`), phone country default |
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

## 9. Feature reference and user guide

Live at **https://singaporekakis.com**. Three roles share one app; the role
decides the bottom nav and everything behind it. Written so a coordinator can
hand it to a caregiver or a kaki without translating anything.

### 9.0 Signing in — everyone

One box takes either an **email address** or a **Singapore mobile number**.
`9123 4567`, `+65 9123 4567` and `6591234567` all reach the same account. A
6-digit code arrives by email (Resend) or SMS (Twilio); it expires in 10
minutes and is single-use.

- **First time only** you are asked for your name, whether you are a caregiver
  or a kaki, and optionally a second way to reach you. **Every time after, just
  the six digits** — the app recognises you before the screen is drawn.
- After a first sign-in you land on a **waiting screen** until the coordinator
  approves you. Tap *Check again* once they have.
- Five wrong codes, or five code requests in fifteen minutes, locks the account
  for a short period. The message always carries the coordinator's number.
- The **? button** floats on every screen, including before you sign in.

### 9.1 Caregiver — booking respite for a family member

**Set up once.** *Home → your household*: the senior's name, age and address.
Then *Care plan*: medications, mobility, languages, emergency contacts, notes.
Every kaki reads the care plan before a visit, so this is the single highest-value
thing a caregiver fills in.

**Book a visit.** *Home → Book a visit*:

1. **Service** — Chaperone, Companionship, Wellness check or Household help.
   *Medicine administration* is visible but locked: it needs Tier 2
   certification and is not bookable in v1.
2. **Urgency** — Urgent (within the hour), Soon (within two hours), or Planned.
3. **What happened** — urgent and soon bookings ask for a trigger (helper left
   suddenly, spouse hospitalised, discharge with no plan…). This is what turns
   a booking into a story the coordinator can prioritise.
4. **Details** — date, time window, preferred language, a note for the kaki.

**While it runs.** The visit page shows status, the assigned kaki (with *"N
visits together"* where you have history), the estimated cost stack, and a
**4-digit start code**. Read that code to the kaki when they arrive — it is how
the app confirms someone actually turned up.

**After.** You get the kaki's report — chips, a short note, and whether
medications were confirmed. You can add a **private care note** the care team
sees but the kaki does not. Cancel from the visit page; please give two hours'
notice so nobody is already travelling.

### 9.2 Kaki — serving visits

**Profile** (*Profile* tab) drives matching: services you can help with,
languages you speak, phone number, and your training record.

**When I can work** (*Profile → When I can work*) is the part most kakis skip
and shouldn't. Tick a Mon–Sun × morning/afternoon grid for your normal week,
then add dated exceptions — a day off, or an extra slot outside your usual
pattern. Exceptions win over the weekly pattern for that date. If you set
nothing, the coordinator sees *unknown* rather than *unavailable*, so you keep
getting offered work — but they are guessing.

**A visit, start to finish:**

1. **Assigned** — you get an SMS or email. Open the visit: senior, address,
   why they need help, the care plan, and what you will receive.
2. **Accept** — or *I can't make it*, which passes it straight back to the
   coordinator with no penalty.
3. **Start** — ask the family for the 4-digit code and enter it. You never see
   this code in your own app; that is the point.
4. **Complete** — tick what applies, write a short note the family will read,
   and confirm medications if the care plan lists any.
5. **Flag a concern** — about the senior's wellbeing *or how you were treated*.
   Goes privately to the care team. There are no public ratings, by design.

**Impact** shows visits, hours, estimated earnings, and repeat visits per
senior. Payouts run weekly via Vanguard to PayNow during the pilot.

### 9.3 Coordinator (admin) — running the pilot

**Today** is the console: awaiting approval, to match, active visits, completed.

**Approvals** — each pending person shows how they signed up. Approve as
caregiver or as kaki; the button you press sets their final role, overriding
what they chose, which is how you fix someone who picked wrong. Suspend takes
effect on their **next request**, not at token expiry.

**Matching** — one card per open request, urgent first. Each lists every
approved kaki with:

- an availability badge — **available / unknown / unavailable** for that exact
  date and half-day, sorted best-first;
- history with this senior, language match, service match, current workload.

Choose one, then press **Assign selected kaki** and confirm. The toast names
who the *server* recorded. It sorts rather than filters on purpose: an urgent
case may still justify phoning someone nominally off.

**Settings** — three automation toggles, all **off** by default:

| Toggle | Effect |
|---|---|
| Auto-approve caregivers | New caregivers skip the queue |
| Auto-approve kakis | New kakis become bookable unreviewed |
| Auto-match on booking | Assigns the best *available* kaki at booking time |

Auto-matching never picks *unknown* or *unavailable* — anything it cannot fill
stays for a human. **Auto-match all open requests now** runs the same sweep on
demand whether or not the toggle is on.

Also here: **per-service pricing** (hours, family rate, kaki rate) written
straight back to `assumptions.json`, and **PayNow** details shown to caregivers.

**Assumptions** — every rate, hour and subsidy percentage with its source.
Anything marked `PLACEHOLDER` has not been confirmed with Vanguard or MOH,
which is currently most of the pricing.

**Quality** — visit reports and private care notes. No public ratings of care
staff, per MOH guidance.

### 9.4 The help bot

The **?** button opens a guide plus a chatbot, on every screen.

- **Signed in** → OpenAI (`gpt-4o-mini`) with the app's rules as context.
- **Signed out** → the built-in keyword guide only. It still answers "how do I
  sign in?", which is the question that gets asked there, and never calls a
  paid provider.
- **No key configured** → the keyword guide for everyone. The app degrades; it
  does not break.

### 9.5 Hard rules encoded in the app

- No public ratings of care staff (MOH). Concerns go privately to a human.
- Certification gates tasks — Tier 2 services are visible but locked.
- Urgent requests sort first, everywhere.
- The kaki never sees the visit start code.
- Money figures are illustrative and say so on every screen showing them.

## 10. Change log

- **v1.5 (2026-08-09) — hardening, and the help bot fixed.** Security audit against ISO/IEC 5055; findings and residual risk in [`deploy/SECURITY-AUDIT.md`](deploy/SECURITY-AUDIT.md). Auth gained rate limiting (5 code requests per identifier, 20 per IP, 5 failed verifications, all per 15 min, DB-backed so a deploy cannot reset them); `/api/docs` closed; HSTS/CSP/frame headers added in Caddy; the DuckDB file and backups taken off world-readable while holding medication data; uvicorn moved to loopback; dependencies pinned. **M-HELP bug:** `/api/chat` required a token, but the help button is reachable from the sign-in screen — a signed-out caregiver asking "how do I sign in?" got a 401 rendered as "I couldn't reach the helper". Auth is now optional: signed in reaches the LLM, signed out gets the keyword guide and never touches a paid provider. Sign-in screen links out to the initiative microsite. Smoke test: 133 → 170 assertions, including the four endpoints (decline, cancel, suspend, admin user list) that had no coverage at all.
- **v1.4 (2026-08-08) — notifications, automation, editable pricing.** Assignment notifies both kaki and caregiver on whichever channel they signed in with. Coordinator settings (DB-backed, no restart): auto-approve per role and auto-match, all default off. Auto-matching assigns only kakis whose availability positively covers the visit; anything unfillable stays for a human. Per-service pricing editable from the admin panel and written back to `assumptions.json`. PayNow details surfaced to caregivers.
- **v1.3 (2026-07-31) — availability, assumptions, safer matching.** Kaki availability as a recurring Mon–Sun × half-day pattern plus dated exceptions; the matching roster is scored per visit and sorted available → unknown → unavailable. Every money and time figure moved into `assumptions.json` with a stated source per value. Matching rebuilt from one-tap chips to explicit selection with confirmation — the previous UI made mis-assignment silent and indistinguishable from a broken feature.
- **v1.2 (2026-07-30) — dual-channel sign-in.** M-AUTH: one sign-in box now takes an **email or a mobile number**; whichever the person types is normalised (`security.classify` → E.164, `+65` assumed for bare 8-digit numbers) and the code is delivered by Resend or **AWS SNS** (`services/sms.py`, `SMS_ENABLED=1`). `/auth/request-code` returns `known` and `needs_profile`, so **returning users are only asked for the 6 digits** — never their name or role again. An account can hold both channels: the second one is captured at signup and marked verified the first time it is used to sign in, tracked in `users.email_verified` / `users.phone_verified`. Admins may be listed by `ADMIN_EMAILS` or `ADMIN_PHONES`. Phone-only accounts store `email = NULL` (an empty string would collide under the UNIQUE constraint the moment a second one appeared). `otp_codes` is rekeyed from `email` to `(identifier, channel)`. M-CORE: `UI.contact(user)` for display where either field may be empty. Smoke test: 30 → 52 assertions.
- **v1.1 (2026-07-21) — prototype-sync round.** M-CORE: global user menu (top-right) with **sign out for every role**; `SERVICE_META` price/fee estimates and `TRIGGERS` in config; DB migration `visits.crisis_trigger`. M-VISITS: urgent/soon bookings gain the **"What happened?" trigger step** (pinned top-3 + click-to-call "not sure"); visit payloads now carry `trigger`, `times_together` (completed visits for this kaki+senior pair — the consistency signal), and `estimate` (price stack + kaki fee). Caregiver visit page gains the **kaki pass** (with "N visits together"), **estimated-cost stack** ("billed via ICCP during pilot"), and **contact/coordinator call row**; Visits tab split **Active/History**. Kaki: $ figures on rows/impact, "you receive ~$X · cashless weekly via Vanguard" on visit detail, **training & certificates** section in profile. M-ADMIN: trigger pill on request cards; **suspend/reinstate** buttons. Deliberately not ported from the prototype (still demo-only there): elderly self-book module, kaki "Available/Now geofenced" tab (conflicts with manual matching), agent console screens, add-kaki flow.
- **v1 (2026-07-21)** — initial build: M-AUTH (email OTP, hardcoded admin, approval gate), M-CARE, M-VISITS (full lifecycle, visit OTP, reports, care notes), M-ADMIN (approvals, manual matching, quality), M-HELP (guide + pluggable Claude chatbot), M-CORE (DuckDB schema v1, design system port).
