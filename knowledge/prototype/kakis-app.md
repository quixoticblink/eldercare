---
title: "Kakis — the working app"
status: live
last_updated: 2026-08-09
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
  → trigger → details), read the start code to the kaki, receive the report.
- **Kaki** — declare availability as a weekly half-day grid plus dated exceptions,
  accept or pass back an assigned visit, start it with the family's 4-digit code,
  finish with a report.
- **Coordinator** — approve people, match visits, and now optionally automate both.

Full feature reference and user guide: [[../../app/SPEC|app/SPEC.md]] section 9.

## The design decisions worth remembering

**The start code is one-way.** The caregiver's screen shows a 4-digit code; the kaki
enters it. The kaki never sees it in their own app. That single asymmetry is what
converts "the app says a visit happened" into "someone was physically at the door and
the family let them in."

**No public ratings, anywhere.** Concerns from either side go privately to the care
team. This is MOH guidance rather than our preference, but it also removes the
mechanism by which gig platforms make vulnerable workers performatively cheerful.

**Availability sorts, it doesn't filter.** The matching screen ranks kakis
available → unknown → unavailable for that exact date and half-day, but shows all of
them. An urgent case may still justify phoning someone who is nominally off. A kaki who
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

## Where it stands

Live, hardened, and audited against ISO/IEC 5055 — see
[[../../app/deploy/SECURITY-AUDIT|SECURITY-AUDIT.md]]. Rate limiting on sign-in, health
data off world-readable permissions, security headers, pinned dependencies. 170
automated assertions covering the full lifecycle.

Fit for a **supervised tabletop**, which is exactly what [[../journal/2026-08-03-ncss-vanguard|NCSS and Vanguard]]
asked for on Aug 3. Not fit for unsupervised public launch: backups have never been
restore-tested, there is no PDPA review or user-facing deletion path, and the pricing
is still placeholder.

*Connects to:* [[README]] · [[kakis-build-plan]] · [[kakis-prototype-spec]] ·
[[../journal/2026-08-03-ncss-vanguard]] · [[../reframing/hmw-current]]
