---
title: "Kakis — the working app"
status: live
last_updated: 2026-09-05
url: https://singaporekakis.com
---

The prototype became a real thing. Not a clickable HTML mock — a deployed app with a
database, real sign-in codes going to real phones, and three roles that can actually
transact with each other. It runs at **https://singaporekakis.com**.

The distinction matters for the rubric line about human centricity. A prototype proves
you understood the journey. A running app proves the journey survives contact with an
SMS provider, a coordinator's Tuesday, and a caregiver who types their number with a
space in it.

## What it is, concretely

FastAPI and DuckDB behind a no-framework HTML/JS frontend, on one t3.micro in
Singapore, TLS via Caddy. One box, one file for a database. That is not a placeholder
for a "real" stack — at pilot scale it is the right amount of machinery, and the whole
thing can be understood by one person in an afternoon. The upgrade path (Next.js,
Postgres) is written down in [[kakis-build-plan]] and deliberately not taken yet.

Three roles share one app:

- **Caregiver** — set up the household and care plan, book a visit (service → urgency
  → trigger → details, with exact times for planned visits), check the kaki's photo
  and code at the door, then read the start code to the kaki, receive the report.
- **Kaki** — declare working hours per day plus dated exceptions, upload a photo and
  certificates, accept or pass back an assigned visit, say when they're on the way, show
  their code at the door, start with the family's 4-digit code, finish with a report.
- **Coordinator** — approve people (with their certificates), match visits, and
  optionally automate both.

Full feature reference and user guide: [[app/SPEC|app/SPEC.md]] section 9.

## The design decisions worth remembering

**The start code is one-way — and since v1.6 the door check runs both ways.** The
caregiver's screen shows a 4-digit code; the kaki enters it. The kaki never sees it in
their own app. That single asymmetry is what converts "the app says a visit happened"
into "someone was physically at the door and the family let them in." NCSS pointed out
on Aug 18 that this proves admission, not identity, so v1.6 added the other half: the
kaki shows a photo and a code of their own, the caregiver enters it, and only then does
the caregiver's start code appear. Two codes, two directions, one door.

**No public ratings, anywhere.** Concerns from either side go privately to the care
team. This is MOH guidance rather than our preference, but it also removes the
mechanism by which gig platforms make vulnerable workers performatively cheerful.

**Availability sorts, it doesn't filter.** The matching screen ranks kakis
available → unknown → unavailable for that exact date and time, but shows all of
them. (v1.6 adds two more sort keys ahead of it — a kaki the family asked for by name,
and a match to a stated gender preference — and auto-match will never assign against
either.) An urgent case may still justify phoning someone who is nominally off. A kaki who
has never set availability reads *unknown*, never *unavailable* — otherwise silence
would quietly remove them from work.

**Every automation defaults off.** Auto-approve caregivers, auto-approve kakis,
auto-match on booking. Each removes a human from a decision about who enters a
vulnerable person's home, so each is a choice someone makes deliberately. Auto-matching
will not assign a kaki whose availability doesn't positively cover the visit; anything
it can't fill waits for a person.

**Every number is in one file with its source.** `assumptions.json` holds hours, rates,
subsidy percentages and the transport allowance, each with a `source` line. Most are
still marked `PLACEHOLDER` — the 54% community care subsidy and the 14% foundation
top-up are illustrative, not confirmed by MOH or a funder. They appear on screens
families see, so the honest label is load-bearing, and the coordinator can see and
change them without a developer.

## What confused me / what went wrong

Three things cost real time, all worth writing down.

**A crash that only appeared on the second boot.** The v1.1 migration
`ALTER TABLE visits ADD COLUMN ... DEFAULT ''` leaves a write-ahead-log entry that
DuckDB 1.5.5 throws an internal exception replaying after an unclean shutdown. The
service started clean, then crash-looped on every restart afterwards with nothing but a
C++ stack trace. A reboot would have taken the pilot down permanently. Fixed by
checkpointing after schema init. The general lesson: *test the second start, not the
first.*

**"The matching is broken" wasn't.** A visit assigned fine — to a different kaki than
the one being checked. The UI was a row of chips where one tap assigned instantly, with
no confirmation and no name in the toast. A silent mis-assignment is indistinguishable
from a broken feature. Rebuilt as explicit selection with a confirm naming the person.

**SMS that reports success and delivers nothing.** AWS SNS accepts a publish to any
number and returns a MessageId, but while the account is sandboxed for a region it
delivers only to *verified* numbers. One handset worked; every other Singapore number
silently got nothing. Moved to Twilio, which has no per-region sandbox. Sandbox status
is per account *per region* — a support case approved elsewhere doesn't help.

The pattern across all three: **the system said it succeeded.** Acceptance is not
delivery, an assignment is not the right assignment, and a clean first boot is not a
working service.

Two more from the v1.6 round, both caught by a reviewer rather than a test, which is
its own lesson.

**The kaki was getting the start code after all.** The rule "the kaki never sees the
start code" was enforced in exactly one place — the single-visit GET — and nowhere
else. The list endpoint, and the responses to the kaki's own accept, start and complete,
all carried `otp_code` in the JSON. The UI never rendered it, so eight seniors and two
partner reviews never noticed; anyone with the browser's network tab would have. v1.6
added a new endpoint with the same leak and the reviewer traced every return. Fixed
with one function every visit response passes through. A hard rule that lives in one
code path isn't a rule, it's a coincidence.

**Wall-clock rules on a UTC box.** The pilot VM runs UTC. "That window has passed",
"bookings open 30 days ahead", "on the way since 18:07" — all Singapore rules, all
computed from the server clock, all eight hours out. The smoke suite pins the clock, so
it could not see it; the frontend computed "today" with `toISOString()`, which is
yesterday until 8am here, so it agreed with the server for the wrong reason. Fixed by
naming the zone in config and in the service environment, and by never using a UTC date
function in the frontend again.

## Where it stands

Live, hardened, and audited against ISO/IEC 5055 — see
[[app/deploy/SECURITY-AUDIT|SECURITY-AUDIT.md]]. Rate limiting on sign-in and on both
door codes, health data off world-readable permissions, security headers, pinned
dependencies. 394 smoke assertions and 32 Playwright end-to-end specs covering the full
lifecycle, in English and in Chinese — the smoke figure derives from its own source, after the hand-maintained
version drifted to six different numbers across five documents.

Fit for a **supervised tabletop**, which is exactly what [[../journal/2026-08-03-ncss-vanguard|NCSS and Vanguard]]
asked for on Aug 3. Not fit for unsupervised public launch: backups have never been
restore-tested, there is no PDPA review or user-facing deletion path, and the pricing
is still placeholder.

**Two rounds of outside eyes since.** On Aug 18 NCSS desk-reviewed the app role by role
— [[ncss-app-review-2026-08-18]] — and one of their thirty items reverses the start-code
decision above: they want the kaki to read the code to the caregiver, as an identity check.
The code as built proves admission, not identity; the register argues for both halves and a
test on round 2.

**And it has now had that Table Top Exercise.** On Aug 21 eight seniors ran the app on their own
phones at a Care Corner AAC in Toa Payoh, with Vanguard and NCSS facilitating —
[[../journal/2026-08-21-tabletop-vanguard-ncss]]. The lifecycle held end to end and the
two hard rules survived contact (no ratings, the kaki never saw the code). What didn't
hold was everything *around* the app: wifi, "what is a browser", the approval wait, a
placeholder number in the phone field, and the subsidy figures that every screen labels
illustrative and every participant asked about anyway. Three new field-level asks came
out of it — kaki gender preference, kaki photo, dual-role sign-up — and cancellation
turned from a pre-arrival action into a lifecycle question with a liability attached.
The full register, mapped to modules, is [[tabletop-2026-08-21-feedback]]. Note what the
session did not test: the six crisis triggers. It ran planned bookings. What gets built
next, and in what order, is [[feature-buckets-2026-09-04]].

**v1.6 shipped on 2026-09-05** — Buckets 1 and 2 of that file, eighteen features, live.
The ones that change what a senior sees at the door: the kaki now carries a photo and a
4-digit code of their own; the family enters it and only then gets their start code to
read back. Both halves of the identity argument from Aug 18 and Aug 21, in one flow.
Exact start and end times in half-hour steps, charged by the half hour with a one-hour
minimum. Languages pre-filled from the care plan, Cantonese added. A female-or-male
preference and "the same kaki again", both sorting the coordinator's roster and both
respected by auto-match. Cancellation after accept and mid-visit, either side, with the
reason recorded and the other side told. Certificates uploaded by the kaki and read by
the coordinator before approval. And the small things that stopped eight people on
Aug 21: no placeholder number in the sign-in box, a waiting screen that says there is
nothing to do, required fields marked, a refresh that keeps your place, and no
"2–5pm" offered at six in the evening.

Every feature has a Playwright test (24 specs, `app/tests/e2e/`) and a smoke assertion
(156 → 368), one commit each, and two review passes whose findings are in the change
log. The build plan, task by task, is [[plans/v1.6-buckets-1-2]].

**v1.7 shipped the same evening** — the Mandarin UI, the first item pulled out of
Bucket 3. A button in the brand bar switches every caregiver and kaki screen, the help
panel and the person's messages to Simplified Chinese; the coordinator console stays
English by design. It is a string dictionary (`frontend/js/i18n.js`, about four hundred
ids) behind `UI.t()`, with display names for data values so that what the app stores
never changes, and a `users.lang` column so the choice follows the person to another
phone and decides the language of their SMS. Two things the reviews caught that the
tests had not: a shared phone could flip the next person's message language (the
server's record now wins), and names had been reaching emails unescaped since v1.4.
The plan is [[plans/v1.7-language-switch]]; the journal entry
[[../journal/2026-09-05-v1.7-language]]. Still not built, by decision: Malay, subsidy
rules, dual-role accounts, live updates — Bucket 3.

*Connects to:* [[README]] · [[kakis-build-plan]] · [[kakis-prototype-spec]] ·
[[tabletop-2026-08-21-feedback]] · [[ncss-app-review-2026-08-18]] · [[../journal/2026-08-03-ncss-vanguard]] ·
[[../journal/2026-08-21-tabletop-vanguard-ncss]] · [[../reframing/hmw-current]]

*2026-09-04: added the Aug 18 NCSS review and the Aug 21 Table Top Exercise outcome to "Where it stands"; linked the recommendation register.*
*2026-09-05: v1.6 shipped — Buckets 1 and 2; two new entries under "what went wrong" (the start-code leak, the UTC box).*
*2026-09-05, later: v1.7 shipped — the Mandarin UI for caregivers and kakis; console English by design.*
