# Kakis app — SPEC v1.6 (pilot build)

The deployable pilot app. FastAPI + DuckDB backend on a VM; static phone-first frontend (Vercel or served by the same VM). This SPEC is the contract: **every future change names the module it touches, and only that module's files change.** If a change can't be expressed that way, the SPEC gets amended first (add a module or split one), then the code follows.

Working name *Kakis* remains provisional (Kampung Kakis collision — see wiki).

---

## 1. Architecture

```
app/
├── SPEC.md                ← this file (the contract)
├── assumptions.json       ← every rate, hour and subsidy, with a source per figure
├── backend/               ← FastAPI + DuckDB, runs on the VM
│   ├── main.py            ← app factory, CORS, static mount, router registration ONLY
│   ├── config.py          ← env vars, constants ONLY
│   ├── db.py              ← DuckDB connection, schema DDL, seed ONLY
│   ├── security.py        ← token signing/verify, identifier classification ONLY
│   ├── settings.py        ← DB-backed coordinator settings (automation toggles) ONLY
│   ├── assumptions.py     ← read/write assumptions.json ONLY
│   ├── requirements.txt   ← pinned dependencies (bump deliberately, then smoke-test)
│   ├── services/
│   │   ├── emailer.py     ← Resend integration ONLY
│   │   ├── sms.py         ← SNS / Twilio, swappable via SMS_PROVIDER ONLY
│   │   ├── notify.py      ← assignment notifications, channel selection ONLY
│   │   ├── matching.py    ← candidate scoring for the coordinator roster ONLY
│   │   ├── availability.py ← weekly pattern + dated exceptions ONLY
│   │   ├── ratelimit.py   ← DB-backed sign-in caps ONLY
│   │   └── llm.py         ← help-chatbot provider chain (Anthropic → OpenAI → guide) ONLY
│   ├── tests/
│   │   └── smoke.py       ← full-lifecycle assertions; prints its own count
├── tests/e2e/             ← Playwright suite (v1.6): one spec per role + the lifecycle; run.sh, check.sh, second-boot.sh
├── playwright.config.js   ← phone viewport, Asia/Singapore, one worker, throwaway DB on :8100
├── package.json           ← @playwright/test only; the app itself has no build step
│   └── routers/
│       ├── auth.py        ← M-AUTH   endpoints
│       ├── users.py       ← M-USERS  endpoints
│       ├── care.py        ← M-CARE   endpoints (households, care plans)
│       ├── visits.py      ← M-VISITS endpoints (requests → lifecycle → reports)
│       ├── admin.py       ← M-ADMIN  endpoints (approvals, manual matching, quality)
│       └── chat.py        ← M-HELP   endpoints
├── frontend/              ← static SPA, no build step
│   ├── index.html         ← shell + screen containers
│   ├── config.js          ← KAKIS_API base URL (set this when frontend is on Vercel)
│   ├── vercel.json        ← frontend-on-Vercel config
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
    ├── EC2-DEPLOYMENT.md  ← the box that is actually running
    ├── README.md          ← generic VM + Vercel instructions
    ├── SECURITY-AUDIT.md  ← ISO/IEC 5055 self-assessment (v1.5)
    ├── kakis.service      ← systemd unit
    ├── Caddyfile          ← reverse proxy + TLS sample
    ├── aws-sns-policy.json ← least-privilege IAM for SMS (sms-voice:*, not sns:*)
    ├── preflight.py       ← pre-go-live environment check
    └── set-secret.sh      ← writes a secret into the service environment
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
| **M-CORE** | app wiring, DB schema, design system, coordinator settings | `main.py`, `config.py`, `db.py`, `settings.py` | `app.js`, `api.js`, `ui.js`, `kakis.css` | env vars, schema migrations, theme, automation toggles |

Cross-module rule: routers never import each other; shared logic lives in `db.py`/`security.py`/`services/`. Frontend views never call `fetch` directly — always through `api.js`.

---

## 3. Roles, auth, approval

- **Login:** one box takes an **email address or a Singapore mobile number** (v1.2). `security.classify` normalises it — bare 8-digit numbers get `DEFAULT_COUNTRY_CODE` (`+65`) and become E.164. A 6-digit code goes out by Resend (email) or the configured SMS provider (`SMS_ENABLED=1`), expires in `OTP_MINUTES` (10) and is single-use. Verify returns a signed token (HMAC, `TOKEN_DAYS` = 30). No passwords.
- **Returning users are asked only for the six digits.** `/auth/request-code` returns `known` and `needs_profile`; name and role are collected once, at first sign-in. An account can hold both channels, tracked in `users.email_verified` / `users.phone_verified`. Phone-only accounts store `email = NULL` — an empty string would collide under the UNIQUE constraint as soon as a second one appeared.
- **Roles:** `admin` · `caregiver` · `kaki`. Chosen at first login (except admin); stored on the user.
- **Admin is hardcoded** via `ADMIN_EMAILS` **or `ADMIN_PHONES`** (comma-separated; phones in full E.164), so a coordinator can run the pilot from a phone with no email. Admin logins are auto-approved with role `admin`.
- **Everyone else lands `pending`** and sees a waiting screen until the admin approves them (M-ADMIN). Approval assigns/confirms the role, overriding what the person chose.
- **Rate limits (v1.5, DB-backed so a deploy cannot reset them):** 5 code requests per identifier, 20 per IP, 5 failed verifications — all per 15 minutes.
- **`DEV_MODE=1`** returns the code in the API response so the app works before Resend or SMS is configured. **`DEMO_IDENTIFIERS`** does the same for named identifiers *even when `DEV_MODE=0`* — every entry is effectively a shared password, so it must never hold a real user's identifier and should be emptied once SMS delivery works.

## 4. Data model (DuckDB)

`users` (id, email?, name, phone, role, status[pending|approved|suspended], email_verified, phone_verified, **photo** (data URL, ≤200 KB), created_at) · `kaki_profiles` (user_id, services[], languages[], area, tier, weekly_slots, availability_note, **gender**[female|male|'']) · `availability_exceptions` (id, user_id, date, half_day[morning|afternoon|all], available, note) · **`kaki_certificates`** (id, user_id, name, issuer, expires, file_name, mime, data (data URL ≤1 MB), uploaded_at) · `households` (id, caregiver_id, senior_name, senior_age, address) · `care_plans` (household_id, meds, mobility, languages[], contacts, **contact_name, contact_relationship, contact_phone**, notes) · `visits` (id, household_id, caregiver_id, kaki_id?, service, tier[urgent|soon|planned], date, time_window, **start_time, end_time, hours**, language, **languages[]**, notes, status, otp_code, **kaki_code, kaki_verified_at**, crisis_trigger, **kaki_gender_pref**[any|female|male], **preferred_kaki_id**, **on_way_at**, **cancelled_by, cancelled_by_name, cancel_reason, cancelled_at**, timestamps…) · `visit_reports` (visit_id, chips[], text, meds_confirmed) · `care_notes` (id, household_id, visit_id?, author_id, chips[], text) · `otp_codes` (identifier, channel, code, expires) · `auth_attempts` (kind, key, ts) · `settings` (key, value, updated_at) · `audit_log` (ts, actor, action, detail).

**v1.6 shapes.** `kaki_profiles.weekly_slots` is now `{"Tue": {"from": "09:00", "to": "12:00"}, …}` in 30-minute steps; the v1.3 half-day form `{"Tue": ["morning"]}` is still read (morning = 08:00–13:00, afternoon = 13:00–18:00 from `assumptions.json`) and the API keeps returning the derived half-day view as `weekly` next to `weekly_hours`. `visits.time_window` holds `"HH:MM–HH:MM"` when exact times were given, so the matcher and older screens keep working; `hours` is the prorated duration (round up to `assumptions.time.rounding_hours`, floor `min_visit_hours`) and drives the estimate. Every `visits` column added in v1.6 defaults so rows from v1.5 read cleanly; visits that were `assigned`/`accepted` at upgrade get a `kaki_code` back-filled at boot.

`users.email` is nullable — a phone-only account stores NULL, because empty strings collide under the UNIQUE constraint. **Migrations:** `ALTER TABLE … ADD COLUMN IF NOT EXISTS` in `db.py`, followed by a `CHECKPOINT` — an un-checkpointed `ADD COLUMN … DEFAULT` leaves a WAL entry that DuckDB 1.5.5 crash-loops replaying after an unclean shutdown.

**Visit lifecycle (M-VISITS):** `requested → assigned → accepted → in_progress → completed` (+ `cancelled`, `declined→requested`, and since v1.6 `kaki cancels from assigned/accepted → requested` with the kaki cleared and the reason kept). Assignment is manual by admin or by the opt-in auto-matcher. **The door, v1.6:** the kaki's visit page shows their photo and a per-assignment 4-digit `kaki_code`; the caregiver enters it (`verify-kaki`) and only then receives `otp_code`, which they read to the kaki; the kaki enters it to `start`. Both codes are rate-limited to 5 wrong tries per visit per 15 minutes. `on_way_at` is stamped by the kaki between accept and start. Completion requires a report. The emergency contact on the care plan is messaged on start and complete.

## 5. API contract (all under `/api`)

- `POST /auth/request-code` {identifier} → {known, needs_profile} · `POST /auth/verify` {identifier, code, role?, name?} → {token, user} · `GET /auth/me`
- `PUT /users/me` profile+prefs (name, phone, kaki: services, languages, area, **gender**) · `PUT /users/me/photo` {data_url} (kaki) · `GET|POST /users/me/certificates`, `DELETE /users/me/certificates/{id}` (kaki; pending kakis included) · `GET|PUT /users/me/availability` (weekly hours or legacy half-days) · `POST|DELETE /users/me/availability/exceptions`
- `GET|PUT /care/household` · `GET|PUT /care/plan` (mobility now includes *Bedridden*; `contact_name/relationship/phone`, phone normalised to E.164)
- `POST /visits` create request — `service, tier, date, languages[] (or legacy language), notes, trigger, kaki_gender_pref, preferred_kaki_id`, and either `window` (urgent/soon presets) or `start_time`+`end_time` (planned, 30-minute steps; a same-day window that has ended is refused; planned dates beyond `max_advance_days` are refused) · `GET /visits` (role-scoped list) · `GET /visits/past-kakis` (caregiver: kakis who have completed a visit for this household) · `GET /visits/{id}` · `POST /visits/{id}/accept|decline|on-the-way|start{otp}|complete{report}` · `POST /visits/{id}/verify-kaki {code}` (caregiver) · `POST /visits/{id}/cancel {reason}` (caregiver: any non-final state; kaki: reason required, assigned/accepted → requested, in_progress → cancelled; admin: any non-final) · `POST /visits/{id}/care-note`. Every visit response passes through `_out()`: the kaki never receives `otp_code`; the caregiver never receives `kaki_code` and receives `otp_code` only after `kaki_verified_at`; household-help visits are minimised for the kaki (no age, meds or private notes).
- `GET /admin/overview` counts · `GET /admin/pending-users` (with certificate counts) · `GET /admin/users` · `GET /admin/users/{id}/certificates`, `…/{cid}/file` · `POST /admin/users/{id}/approve|suspend` · `GET /admin/kakis?visit_id=` roster (sorted preferred → availability → gender match → history → load; `language_ok`, `gender_ok`, `preferred` per row) · `POST /admin/visits/{id}/assign` {kaki_id} · `POST /admin/auto-match` · `GET|PUT /admin/settings` (+ `max_advance_days`) · `GET /admin/quality` reports + notes + **cancellations**
- `POST /chat` {message, history[]} → {reply, source} — auth **optional**: signed in reaches the LLM (`source: assistant`), signed out or bad token gets the keyword guide (`source: guide`) and never calls a paid provider

Errors: `{detail}` with proper status codes; frontend surfaces via toast.

## 6. Environment

`backend/config.py` is the single source of truth — it is env vars only, no logic, so it reads as the reference. Grouped:

| Group | Variables |
|---|---|
| **Core** | `JWT_SECRET` (required in prod) · `DB_PATH` (default `./kakis.duckdb`) · `CORS_ORIGINS` (default `*`; tighten to the frontend origin) · `PORT` (default 8000) · `DEV_MODE` (default 1) · `TZ` (default `Asia/Singapore`; the service unit also sets it — the box runs UTC and every wall-clock rule is a Singapore rule) |
| **Admin** | `ADMIN_EMAILS` (default `abhishekkaul@gmail.com`) · `ADMIN_PHONES` (E.164, comma-separated) |
| **Email (M-AUTH)** | `RESEND_API_KEY` · `MAIL_FROM` (default `Kakis <onboarding@resend.dev>`) · `MAIL_REPLY_TO` — Resend sends via DNS records, not a mailbox, so `MAIL_FROM` may be unable to receive; without a reply-to, replies bounce |
| **SMS (M-AUTH)** | `SMS_ENABLED` (default 0) · `SMS_PROVIDER` (`sns` \| `twilio`, default `sns`) · `DEFAULT_COUNTRY_CODE` (default `+65`) |
| ↳ AWS SNS | `AWS_REGION` (default `ap-southeast-1`) · `SMS_SENDER_ID` (default `Kakis`; clear it — Singapore carriers drop unregistered alphanumeric sender IDs) |
| ↳ Twilio | `TWILIO_ACCOUNT_SID` · `TWILIO_AUTH_TOKEN` · `TWILIO_FROM` · `TWILIO_MESSAGING_SERVICE_SID` (takes precedence over `TWILIO_FROM`) |
| **Help bot (M-HELP)** | `ANTHROPIC_API_KEY` + `LLM_MODEL` (default `claude-sonnet-4-5`) · `OPENAI_API_KEY` + `OPENAI_MODEL` (default `gpt-4o-mini`) |
| **Demo backdoor** | `DEMO_IDENTIFIERS` — see section 3. Each entry is a shared password. Empty it once SMS works. |
| **Rate limits** | `RATE_LIMIT_CODE_PER_IDENTIFIER` (5) · `RATE_LIMIT_CODE_PER_IP` (200) · `RATE_LIMIT_VERIFY_FAILURES` (5) · `RATE_LIMIT_VISIT_CODE` (5, per visit, both door codes) — all per 15 minutes |

Constants that are *not* env-configurable live in the same file: `TOKEN_DAYS` (30), `OTP_MINUTES` (10), `TRIGGERS`, `LOCKED_SERVICES`, `TIERS`, `LANGUAGES` (now with Cantonese), `GENDERS`, `GENDER_PREFS`, `HALF_DAYS`, `WEEKDAYS`. Coordinator-editable settings (no restart) live in the `settings` table: the three automation toggles, PayNow, and `max_advance_days` (30). The bookable services and every rate come from `assumptions.json`, not from config.

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
  approves you. It says so in one line — there is nothing to do; you are
  messaged when approved. A kaki can add certificates from here before
  approval, which is what the coordinator looks at.
- Five wrong codes, or five code requests in fifteen minutes, locks the account
  for a short period. The message always carries the coordinator's number.
- The **? button** floats on every screen, including before you sign in.

### 9.1 Caregiver — booking respite for a family member

**Set up once.** *Home → your household*: the senior's name, age and address.
Then *Care plan*: medications, mobility (including *Bedridden*), languages, one
emergency contact as name / relationship / mobile (that number is messaged when a
visit starts and ends), notes. Every kaki reads the care plan before a visit
(household-help kakis see only mobility, the contact and the address), so this is
the single highest-value thing a caregiver fills in. *Your profile* on Home edits
your own name and number.

**Book a visit.** *Home → Book a visit*:

1. **Service** — Chaperone, Companionship, Wellness check or Household help.
   *Medicine administration* is visible but locked: it needs Tier 2
   certification and is not bookable in v1.
2. **Urgency** — Urgent (within the hour), Soon (within two hours), or Planned.
3. **What happened** — urgent and soon bookings ask for a trigger (helper left
   suddenly, spouse hospitalised, discharge with no plan…). This is what turns
   a booking into a story the coordinator can prioritise.
4. **Details** — for a planned visit, a date (up to the coordinator's horizon,
   30 days by default) and an exact start and end in 30-minute steps, charged
   by the half hour with a one-hour minimum; for urgent and soon, an arrival
   window that is still ahead of you. The languages come pre-filled from the
   care plan and you can pick several. Optionally a female or male kaki, and
   *someone they know* — a kaki who has visited before. Required and optional
   fields say which they are, and a refresh keeps you on the same step.

**While it runs.** The visit page says how long matching usually takes and
messages you when a kaki is matched, confirms, is on the way, or cancels. It
shows the assigned kaki with their **photo** (and *"N visits together"* where
you have history) and the estimated cost stack. **At the door:** compare the
photo, ask the kaki for the 4-digit code on their screen and enter it under
*Check it's them*. Your own **4-digit start code** then appears; read it to the
kaki to start the visit. Only you can see it — that is how the app confirms
someone was really let in.

**After.** You get the kaki's report — chips, a short note, and whether
medications were confirmed. You can add a **private care note** the care team
sees but the kaki does not. Cancel from the visit page at any point before it
is completed, with a few words on why; the kaki and coordinator are told.
Whether anything is paid for a cancelled visit is the coordinator's decision.

### 9.2 Kaki — serving visits

**Profile** (*Profile* tab) drives matching: a **photo** (families see it at
the door), whether you are female or male (some families ask), services you can
help with, languages you speak, phone number, and your **certificates** — CPR +
AED, mobility training and the like, as a PDF or a photo, up to ten. The
coordinator checks these before approving you and when matching.

**When I can work** (*Profile → When I can work*) is the part most kakis skip
and shouldn't. Tick the days you normally work and the hours, in 30-minute
steps, then add dated exceptions — a day off, or an extra slot outside your
usual pattern. Exceptions win over the weekly pattern for that date. If you set
nothing, the coordinator sees *unknown* rather than *unavailable*, so you keep
getting offered work — but they are guessing.

**A visit, start to finish:**

1. **Assigned** — you get an SMS or email that says the service, the hours and
   the task. You do not need to keep the app open. Open the visit: senior,
   address, why they need help, the care plan (household help shows only what
   the task needs), and what you will receive.
2. **Accept** — or *I can't make it*, which passes it straight back to the
   coordinator with no penalty. After accepting you can still cancel with a
   reason; the family and coordinator are told and the visit goes back for a
   new match.
3. **On my way** — tap it when you leave; the family gets a message.
4. **At the door** — show your photo and the 4-digit *code for the family* on
   your visit page. They enter it, then read you their start code; enter that
   to **start**. You never see their code in your own app; that is the point.
5. **Complete** — tick what applies, write a short note the family will read,
   and confirm medications if the care plan lists any.
6. **Flag a concern** — about the senior's wellbeing *or how you were treated*.
   Goes privately to the care team. There are no public ratings, by design.

**Impact** shows visits, hours, estimated earnings, and repeat visits per
senior. Payouts run weekly via Vanguard to PayNow during the pilot.

### 9.3 Coordinator (admin) — running the pilot

**Today** is the console: awaiting approval, to match, active visits, completed —
each count is a button to the list behind it.

**Approvals** — each pending person shows how they signed up and, for a kaki,
how many certificates they have uploaded, with a button to open each one.
Approve as caregiver or as kaki; the button you press sets their final role, overriding
what they chose, which is how you fix someone who picked wrong. Suspend takes
effect on their **next request**, not at token expiry.

**Matching** — one card per open request, urgent first. Each lists every
approved kaki with:

- an availability badge — **available / unknown / unavailable** for that exact
  date and time, sorted best-first;
- whether the family asked for this kaki, whether they match a requested
  gender, history with this senior, language match, service match, workload.

Choose one, then press **Assign selected kaki** and confirm. The toast names
who the *server* recorded. It sorts rather than filters on purpose: an urgent
case may still justify phoning someone nominally off.

**Settings** — three automation toggles, all **off** by default:

| Toggle | Effect |
|---|---|
| Auto-approve caregivers | New caregivers skip the queue |
| Auto-approve kakis | New kakis become bookable unreviewed |
| Auto-match on booking | Assigns the best *available* kaki at booking time |

Auto-matching never picks *unknown* or *unavailable*, and never assigns
against a stated gender preference — anything it cannot fill stays for a human.
Also here: **bookings open up to N days ahead** (30 by default). **Auto-match all open requests now** runs the same sweep on
demand whether or not the toggle is on.

Also here: **per-service pricing** (hours, family rate, kaki rate) written
straight back to `assumptions.json`, and **PayNow** details shown to caregivers.

**Assumptions** — every rate, hour and subsidy percentage with its source.
Anything marked `PLACEHOLDER` has not been confirmed with Vanguard or MOH,
which is currently most of the pricing.

**Quality** — visit reports, private care notes, and **cancellations** (who,
why, when) — the pattern to look at before deciding any compensation rule. No
public ratings of care staff, per MOH guidance.

### 9.4 The help bot

The **?** button opens a guide plus a chatbot, on every screen.

- **Signed in** → a provider call with the app's rules as context, returning
  `source: assistant`. `services/llm.py` tries **Anthropic first if
  `ANTHROPIC_API_KEY` is set, then OpenAI if `OPENAI_API_KEY` is set**, then
  falls through to the keyword guide. The live box runs OpenAI
  (`gpt-4o-mini`) because only that key is configured on it; set the Anthropic
  key and it switches with no code change.
- **Signed out** → the built-in keyword guide only, returning `source: guide`.
  It still answers "how do I sign in?", which is the question that gets asked
  there, and never calls a paid provider.
- **Bad or expired token** → same as signed out. It degrades rather than
  returning 401, which is the v1.5 bug.
- **No key configured** → the keyword guide for everyone. The app degrades; it
  does not break.

### 9.5 Hard rules encoded in the app

- No public ratings of care staff (MOH). Concerns go privately to a human.
- Certification gates tasks — Tier 2 services are visible but locked.
- Urgent requests sort first, everywhere.
- The kaki never sees the visit start code; the caregiver never sees the kaki's
  code and sees the start code only after entering the kaki's (v1.6).
- Money figures are illustrative and say so on every screen showing them.
- Every automation defaults off; auto-match never overrides a stated preference.

## 10. Change log

- **v1.6 (2026-09-05) — the August feedback round built in.** Eighteen features from `knowledge/prototype/feature-buckets-2026-09-04.md`, each behind a Playwright end-to-end test (new `tests/e2e/`, 24 specs) and a smoke assertion (156 → 368), one commit per feature, two review passes. **M-AUTH:** no placeholder number in the sign-in field. **M-USERS:** waiting screen says there is nothing to do; caregiver profile screen; kaki photo (`users.photo`, data URL ≤200 KB, resized on the phone); kaki gender; certificates (`kaki_certificates`, ≤1 MB, ten per kaki, pending kakis can add them); availability re-cut from half-day grid to per-day hours in 30-minute steps (legacy half-days still read); phone-only accounts can't retype their sign-in number, changed numbers are unverified until used. **M-CARE:** *Bedridden*; emergency contact split into name/relationship/phone and messaged on start and complete; care plan first on Home. **M-VISITS:** booking steps are hash routes with a persisted draft (refresh keeps the step), required/optional markers; a same-day window that has ended is refused and the presets roll forward after 5pm; exact start/end times, hours prorated to the half hour (min 1 h) and priced accordingly; languages pre-filled from the care plan, several per visit, Cantonese; "Other — tell us" trigger; advance-booking horizon (`settings.max_advance_days`); caregiver told on confirm / pass-back / cancel / on-the-way and shown the usual time-to-match; assignment message to the kaki carries hours and the task; `on-the-way`; **identity both ways** — per-assignment `kaki_code` shown with the kaki's photo, `verify-kaki` reveals the caregiver's `otp_code`, both codes rate-limited per visit; `preferred_kaki_id` with `/visits/past-kakis`; `kaki_gender_pref`; household-help visits minimised for the kaki; cancellation after accept and mid-visit by either side with who and why, kaki cancels return the visit to matching. **M-ADMIN:** dashboard counts are links; roster sorts preferred → fit → gender → history; auto-match honours preference and gender; certificates on approval; cancellations under Quality. **M-HELP:** guide and system prompt updated for all of it. **M-CORE:** `TZ` pinned to Asia/Singapore in config and the service unit (the box runs UTC); `App.config` now carries the whole `/auth/me` config (PayNow and the money disclaimer had never reached the UI); `UI.ymd/hhmm/timeOptions/shrinkImage`. **What went wrong on the way:** the first review found the new on-the-way endpoint (and, pre-existing, list/accept/start/complete) handing the kaki the start code in the JSON body — fixed with a single `_out()` every visit response passes through; the frontend computed "today" in UTC (yesterday until 8am here); `window_end_hour` missed "9am–12"; the second review found a blank kaki code verifying visits assigned before the upgrade, and HTML from a cancellation reason reaching an email. All in the smoke suite now.

- **Doc pass (2026-08-09) — the SPEC caught up with the code.** No behaviour change; sections 1, 3, 4, 5, 6 and 9.4 had drifted behind v1.2–v1.5 and were describing an app that no longer existed. Section 1 gained the five missing service modules (`sms`, `notify`, `matching`, `availability`, `ratelimit`), plus `assumptions.py`, `settings.py`, `requirements.txt` and `tests/`; `vercel.json` corrected from `deploy/` to `frontend/`. Section 3 replaced "login: email" and "mobile OTP: planned" with the dual-channel reality, plus `ADMIN_PHONES`, the rate limits, and the `DEMO_IDENTIFIERS` backdoor warning. Section 4 gained `availability_exceptions`, `auth_attempts`, `settings`, the columns added by migration, and the checkpoint rule. Section 5 corrected the auth and chat contracts. Section 6 became a grouped table generated from `config.py` — it had listed 10 of the 24 variables that actually exist. Section 9.4 corrected the help-bot provider: the chain is **Anthropic if keyed, then OpenAI, then the keyword guide**, and the live box runs OpenAI only because that is the key it has. Separately, `smoke.py` now counts its own assertions instead of carrying a hand-maintained number, which had reached six different values across five documents (24 / 30 / 52 / 133 / 148 / 170; the real figure is 156). One `assert` sharing a line with an assignment was split onto its own line so the derived count is exact rather than approximate.
- **v1.5 (2026-08-09) — hardening, and the help bot fixed.** Security audit against ISO/IEC 5055; findings and residual risk in [`deploy/SECURITY-AUDIT.md`](deploy/SECURITY-AUDIT.md). Auth gained rate limiting (5 code requests per identifier, 20 per IP, 5 failed verifications, all per 15 min, DB-backed so a deploy cannot reset them); `/api/docs` closed; HSTS/CSP/frame headers added in Caddy; the DuckDB file and backups taken off world-readable while holding medication data; uvicorn moved to loopback; dependencies pinned. **M-HELP bug:** `/api/chat` required a token, but the help button is reachable from the sign-in screen — a signed-out caregiver asking "how do I sign in?" got a 401 rendered as "I couldn't reach the helper". Auth is now optional: signed in reaches the LLM, signed out gets the keyword guide and never touches a paid provider. Sign-in screen links out to the initiative microsite. Smoke test extended to cover the four endpoints (decline, cancel, suspend, admin user list) that had no coverage at all. *(Amended in the 2026-08-09 doc pass: this line originally read "133 → 170 assertions". Both figures were hand-maintained and wrong — the file has 155 `assert` statements. The banner now derives the count instead.)*
- **v1.4 (2026-08-08) — notifications, automation, editable pricing.** Assignment notifies both kaki and caregiver on whichever channel they signed in with. Coordinator settings (DB-backed, no restart): auto-approve per role and auto-match, all default off. Auto-matching assigns only kakis whose availability positively covers the visit; anything unfillable stays for a human. Per-service pricing editable from the admin panel and written back to `assumptions.json`. PayNow details surfaced to caregivers.
- **v1.3 (2026-07-31) — availability, assumptions, safer matching.** Kaki availability as a recurring Mon–Sun × half-day pattern plus dated exceptions; the matching roster is scored per visit and sorted available → unknown → unavailable. Every money and time figure moved into `assumptions.json` with a stated source per value. Matching rebuilt from one-tap chips to explicit selection with confirmation — the previous UI made mis-assignment silent and indistinguishable from a broken feature.
- **v1.2 (2026-07-30) — dual-channel sign-in.** M-AUTH: one sign-in box now takes an **email or a mobile number**; whichever the person types is normalised (`security.classify` → E.164, `+65` assumed for bare 8-digit numbers) and the code is delivered by Resend or **AWS SNS** (`services/sms.py`, `SMS_ENABLED=1`). `/auth/request-code` returns `known` and `needs_profile`, so **returning users are only asked for the 6 digits** — never their name or role again. An account can hold both channels: the second one is captured at signup and marked verified the first time it is used to sign in, tracked in `users.email_verified` / `users.phone_verified`. Admins may be listed by `ADMIN_EMAILS` or `ADMIN_PHONES`. Phone-only accounts store `email = NULL` (an empty string would collide under the UNIQUE constraint the moment a second one appeared). `otp_codes` is rekeyed from `email` to `(identifier, channel)`. M-CORE: `UI.contact(user)` for display where either field may be empty. Smoke test: 30 → 52 assertions.
- **v1.1 (2026-07-21) — prototype-sync round.** M-CORE: global user menu (top-right) with **sign out for every role**; `SERVICE_META` price/fee estimates and `TRIGGERS` in config; DB migration `visits.crisis_trigger`. M-VISITS: urgent/soon bookings gain the **"What happened?" trigger step** (pinned top-3 + click-to-call "not sure"); visit payloads now carry `trigger`, `times_together` (completed visits for this kaki+senior pair — the consistency signal), and `estimate` (price stack + kaki fee). Caregiver visit page gains the **kaki pass** (with "N visits together"), **estimated-cost stack** ("billed via ICCP during pilot"), and **contact/coordinator call row**; Visits tab split **Active/History**. Kaki: $ figures on rows/impact, "you receive ~$X · cashless weekly via Vanguard" on visit detail, **training & certificates** section in profile. M-ADMIN: trigger pill on request cards; **suspend/reinstate** buttons. Deliberately not ported from the prototype (still demo-only there): elderly self-book module, kaki "Available/Now geofenced" tab (conflicts with manual matching), agent console screens, add-kaki flow.
- **v1 (2026-07-21)** — initial build: M-AUTH (email OTP, hardcoded admin, approval gate), M-CARE, M-VISITS (full lifecycle, visit OTP, reports, care notes), M-ADMIN (approvals, manual matching, quality), M-HELP (guide + pluggable Claude chatbot), M-CORE (DuckDB schema v1, design system port).
