---
title: "Kakis — from prototype to app: tech choices and build plan"
status: draft
last_updated: 2026-07-21
based_on: [kakis-prototype-spec (v2), kakis-design-brief, respite-marketplace-concept, vanguard-operational-data]
method: "Superpowers-style: brainstorm → design decisions → plan (github.com/obra/superpowers)"
---

ok so the v2 prototype exists and the team has signed off on the spec. The next question is the real one: what do we build it *with*, and in what order, given five people with day jobs, an Aug 20 milestone, and a Q4 Pasir Ris pilot at maybe 100–300 bookings/month. This entry follows the Superpowers discipline — settle the design questions first, write the plan second, and only then let anyone write code. The punchline up front: **a Next.js PWA on Vercel + Supabase (Singapore region) + a thin Claude-agent worker layer — and aggressively *not* building anything we can buy, borrow from Vanguard, or do manually at pilot scale.**

## First principles from our own wiki

Two findings constrain every technology choice:

1. **The moat is not code** ([[../reframing/devils-advocate]] critique 8, confirmed by Vanguard). So the build should be as small as possible — every hour on infrastructure is an hour not spent on certification, trust, and pilot operations.
2. **Pilot scale is tiny by software standards.** 20–30 kakis, 30–50 seniors, a few hundred bookings/month. Anything that scales to "Singapore" before the pilot proves demand is premature. Boring, managed, and replaceable beats clever.

Corollary (Superpowers would call this YAGNI): where the spec marks something **[ops]**, the first version is allowed to be a human — the "concierge backend" pattern. Agents replace humans workflow-by-workflow as volume justifies it.

## The design decisions (brainstormed, with alternatives)

**D1 — Web app (PWA), not native apps.** Crisis activation can't wait for an App Store download: a caregiver whose helper just left gets a *link* — WhatsApp or SMS — and is booking in thirty seconds. PWAs deploy like the microsite (push → live), skip two app-store review cycles per release, and the team already ships on Vercel. Add-to-home-screen covers the kaki's daily use. *Rejected:* Flutter / React Native — two store pipelines, slower iteration, and nobody on the team maintains mobile toolchains. Native becomes worth it post-pilot if push-notification reliability on iOS PWAs proves painful (the one real PWA weakness — mitigated with WhatsApp as the primary notification rail, below).

**D2 — Next.js + TypeScript + Tailwind, one repo, three surfaces.** The prototype is already componentised in spirit (screens, chips, passes, tiers); port the design tokens straight in. One Next.js app serves `/care` (caregiver), `/senior` (elderly mode), `/kaki` (respite giver), `/ops` (console, auth-gated) — matching the spec's four modules and the "separate builds for ops" intent via route-level auth, not a second codebase. *Rejected:* separate repos per surface (coordination cost for five part-timers), plain React SPA (lose server-side rendering for the link-first crisis flow).

**D3 — Supabase as the entire backend.** Postgres (the booking domain is relational: seniors–kakis–visits–certs), Auth with phone-OTP out of the box (spec D2: phone = identity), Row Level Security for PDPA-grade data separation (a kaki sees only her visits; a family only their senior), Realtime for visit tracking, Storage for cert documents, hosted in `ap-southeast-1`. One managed service, generous free tier, SQL we can export the day Vanguard's IT wants it. *Rejected:* Firebase (document model fights the relational domain), custom Node+Postgres (ops burden), AWS Amplify (complexity without benefit at this scale).

**D4 — Matching is a deterministic scoring function; the LLM never picks the kaki.** This is auditable-by-MOH territory. The match score = weighted sum (consistency, language, proximity, certification-fit) with the spec's broad-base states as named weight presets and per-senior overrides — pure SQL/TypeScript, explainable line by line. The **agents** (Claude API via tool use) sit *around* it: the matching agent watches demand/supply and *recommends* state changes with simulated impact; the onboarding agent cross-checks documents against registry lists and *recommends* approval; the quality agent reads reports and care notes, categorises (elderly QoL / kaki service / kaki wellbeing), and *recommends* follow-ups. Every recommendation carries its evidence; a human clicks approve. That's the prototype's ops console, made real. *Rejected:* LLM-as-matcher (unexplainable, unnecessary — the scoring function is 50 lines), and no-agents-at-all (manual triage is exactly what caps Vanguard at 20–30 bookings/month).

**D5 — WhatsApp first for notifications, SMS fallback, voice for seniors.** Caregivers and kakis live on WhatsApp; job offers, confirmations, and visit updates go there via Twilio's WhatsApp Business API. The senior gets what the prototype promises: *a phone call from a person she knows.* No senior-facing push, ever. *Rejected:* app push as primary (iOS PWA push is the weak link; WhatsApp sidesteps it).

**D6 — Payments start manual, PayNow when real.** Pilot month one: "bill my ICCP account" is the only rail — Vanguard invoices families as they do today, kaki payouts run weekly from a CSV via GIRO/PayNow through Vanguard finance (spec [ops] G3 answered by deferring it). Month two+: Stripe Singapore (PayNow QR supported) or HitPay for card/PayNow in-app. Building payment plumbing before the payer stack is ruled ([ops] G2) would be building on sand.

**D7 — Singpass is a mock until there's an entity.** Real Myinfo requires a registered entity and API onboarding — that's the counterparty question ([[../journal/2026-07-07-vanguard-prep]]), not a technical one. Pilot workaround that's arguably *stronger*: every kaki attends Vanguard training in person and shows NRIC there — identity verified by a human at the training desk, recorded in the console. The prototype's consent screen stays as the committed future flow.

**D8 — Boring supporting cast.** Sentry (errors), PostHog (product analytics — which tier do caregivers actually use?), GitHub Actions (CI), Vercel previews per PR, and an append-only `audit_log` table from day one (every match, approval, and override — the pilot's evidence base for the MOH data case is itself a product requirement).

## The data model, in one paragraph

`households` (family + senior) → `care_plans` (meds, mobility, languages, contacts — the editable plan) → `visit_requests` (service, tier, trigger, window) → `matches` (scored candidates, chosen, state-at-time, explanation) → `visits` (OTP start/end, status timeline) → `visit_reports` + `care_notes` (private, routed) → `quality_flags` (categorised, archived). Supply side: `kakis` → `certifications` (registry ID, expiry, tier) → `preferences` (languages, days, geofence) → `payouts`. Plus `weight_states`, `audit_log`, `users` (Supabase Auth). Fifteen-odd tables; nothing exotic.

## The plan (phases sized to the calendar)

**Phase 0 — decisions & scaffold (now → end July).** Get G1–G6 answered by Vanguard (SLA, subsidy rules, payment rail, volume cap, ratings ruling, ops metrics). Stand up the repo: Next.js + Supabase + auth + the design tokens from the prototype. Port the four-language copy of elderly mode into i18n files early — retrofitting translation is misery. Exit: `npm run dev` shows the landing screen with real auth behind it.

**Phase 1 — the thin vertical slice (Aug 1 → Aug 20, SGLN milestone).** One booking, end to end, with humans where agents will be: caregiver signs in (OTP) → books a *planned* chaperone visit → coordinator assigns in the console (manual, but logging what the scoring function *would* have picked — shadow mode) → kaki sees it in her list → OTP start/end → report → care note routed. Payments mocked; matching in shadow mode; WhatsApp notifications live (that part is cheap and demonstrably magic). Exit: the Aug 20 demo is a *real* booking on real infrastructure, not the HTML prototype.

**Phase 2 — tiers, matching, agents (Sep → Oct).** Urgent/Soon tiers with SLA timers; the scoring function goes live with broad-base states + per-senior overrides; onboarding agent (doc cross-check) and quality agent (report reading, categorisation, pattern flags) ship behind the approve-button; elderly self-book mode; PayNow via Stripe/HitPay if G3 says so. Exit: Wei Lin's "Today" screen is real and the coordinator touches only exceptions.

**Phase 3 — pilot hardening (Q4, Pasir Ris).** Onboard the first ~20 kakis at a Vanguard training day (NRIC verified in person), ~30 households via the ICCP intake; SLA dashboards; the audit log becomes the demand-evidence export for MOH; iterate weekly against the quality agent's categories. Exit: the pilot generates the data slide 13 of the deck admits we don't have.

## How to actually run Superpowers on this

Install it in Claude Code (`/plugin install superpowers@claude-plugins-official`), open the repo, and feed it this file plus [[kakis-prototype-spec]]. The workflow maps cleanly: the spec is the **brainstorm output**; this entry is the **design doc**; ask for the **writing-plans** skill to explode each phase into its 2–5-minute TDD tasks (it will demand exact file paths and failing-test-first — let it); then **subagent-driven-development** executes with two-stage review while a human watches the checkpoints. One git worktree per workstream (caregiver flow / kaki flow / ops console) keeps five part-time contributors from colliding. The P0/P1 register in the spec is the prioritisation the planner should respect.

## What could bite us (said out loud)

Twilio WhatsApp templates need pre-approval — start that paperwork in Phase 0, not when notifications block the demo. Supabase RLS policies are easy to get subtly wrong — they're the PDPA surface, so they get real tests, not vibes. iOS PWA notification limits are real — hence WhatsApp-first, but validate with one kaki's actual iPhone in Phase 1. And the standing risk from the wiki applies to the stack too: if the pilot's owner in October is Vanguard IT or a government cluster, they inherit Postgres + TypeScript on managed services — the most inheritable stack there is. That's not an accident.

## Connects to

[[kakis-prototype-spec]] is the build target this plan sequences. [[kakis-design-brief]] holds the evidence-to-design trace. [[../strategy/respite-marketplace-concept]] and [[../strategy/consistency-as-design-constraint]] are the strategy this implements. [[../reframing/devils-advocate]] critiques 8 and 14 shaped D4 directly. [[../evidence/vanguard-operational-data]] sets the scale assumptions. The counterparty question in [[../journal/2026-07-07-vanguard-prep]] gates D7.
